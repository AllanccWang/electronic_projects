import serial
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from scipy.ndimage import uniform_filter1d
from scipy.signal import find_peaks, hilbert
from scipy.optimize import curve_fit

# ===== STM32 Settings (match your CubeMX) =====
PORT = "COM3"           
BAUD = 115200
BUFFER_SIZE = 1024
VREF = 3.3
SAMPLE_RATE = 170000    

# Qubit params
F0_EXPECTED = 5033      
T1_EXPECTED = 0.1       

ser = serial.Serial(PORT, BAUD, timeout=0.5)
print(f"Qubit Scope: {PORT} @ {SAMPLE_RATE/1000:.0f}kSps")

fig, ((ax_wave, ax_fft), (ax_rabi, ax_t1)) = plt.subplots(2, 2, figsize=(12, 10))
fig.suptitle('ESP32+STM32 RLC Qubit Real-Time Analysis')

# Buffers
wave_buffer = np.zeros(4096)
fft_buffer = []
rabi_data = {'time': [], 'amp': []}

# Plot lines
wave_line, = ax_wave.plot([], [], 'b-', lw=1.5)
fft_line, = ax_fft.plot([], [], 'r-', lw=2)
rabi_line, = ax_rabi.plot([], [], 'go-', lw=2)
t1_line, = ax_t1.plot([], [], 'bo-', lw=2)

# Formatting
ax_wave.set_ylabel('Voltage (V)'); ax_wave.set_ylim(0, VREF*1.1); ax_wave.grid(alpha=0.3)
ax_fft.set_xlabel('Freq (kHz)'); ax_fft.grid(alpha=0.3)
ax_rabi.set_xlabel('Pulse (ms)'); ax_rabi.set_ylabel('Peak V'); ax_rabi.grid(alpha=0.3)
ax_t1.set_xlabel('Time (s)'); ax_t1.set_ylabel('Envelope'); ax_t1.grid(alpha=0.3)

status_text = fig.text(0.02, 0.02, 'Ready...', fontsize=11, 
                       bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))

plt.tight_layout()

def exp_decay(t, A, tau, offset):
    return A * np.exp(-t/tau) + offset

def analyze_qubit(volt):
    N = len(volt); t = np.arange(N) / SAMPLE_RATE
    
    # FFT resonance
    fft = np.fft.rfft(volt)
    freq = np.fft.rfftfreq(N, 1/SAMPLE_RATE)/1000  # kHz
    fft_mag = np.abs(fft)
    f_peak = freq[np.argmax(fft_mag[2:30])]  # 2-30kHz
    amp_peak = fft_mag.max()
    
    # Envelope (Hilbert)
    envelope = np.abs(hilbert(volt))
    
    # Steady-state (your logic)
    high_mask = volt > 0.7 * VREF
    v_steady = np.mean(volt[high_mask]) if np.sum(high_mask)>10 else 0
    
    return {'f_peak':f_peak, 'amp_peak':amp_peak, 'v_steady':v_steady, 
            'envelope':envelope, 'rms':np.sqrt(np.mean(volt**2))}

def update(frame):
    global wave_buffer, fft_buffer, rabi_data
    
    raw = ser.read(4096)
    if len(raw) != 4096: 
        status_text.set_text(f'Short read: {len(raw)}')
        return wave_line, fft_line, rabi_line, t1_line
    
    data = np.frombuffer(raw, dtype=np.uint16)
    volt = data * VREF / 4095.0
    
    # Rolling buffer
    wave_buffer = np.roll(wave_buffer, -len(volt))
    wave_buffer[-len(volt):] = volt
    
    analysis = analyze_qubit(volt)
    
    # Waveform (last 1024 pts)
    wave_line.set_data(np.arange(1024), wave_buffer[-1024:])
    ax_wave.set_xlim(0, 1024)
    
    # FFT
    f_disp = np.fft.rfftfreq(1024, 1/SAMPLE_RATE)/1000
    fft_disp = np.abs(np.fft.rfft(wave_buffer[-1024:]))
    fft_line.set_data(f_disp, fft_disp)
    ax_fft.set_xlim(0, 15); ax_fft.set_ylim(0, fft_disp.max()*1.1)
    
    # Rabi tracking
    fft_buffer.append(analysis)
    if len(fft_buffer) > 100: fft_buffer = fft_buffer[-100:]
    
    if len(fft_buffer) > 5:
        recent = fft_buffer[-5:]
        pulse_est = len(recent) * 0.2  # Proxy ms
        rabi_data['time'].append(pulse_est)
        rabi_data['amp'].append(analysis['v_steady'])
        if len(rabi_data['time']) > 50:
            rabi_data['time'] = rabi_data['time'][-50:]
            rabi_data['amp'] = rabi_data['amp'][-50:]
        
        rabi_line.set_data(rabi_data['time'], rabi_data['amp'])
        ax_rabi.set_xlim(0, max(10, max(rabi_data['time'] or [0])))
    
    # T1 fit (last 100 envelope pts)
    if len(analysis['envelope']) > 100:
        t_fit = np.arange(100) / SAMPLE_RATE
        env_fit = analysis['envelope'][-100:]
        try:
            popt, _ = curve_fit(exp_decay, t_fit, env_fit, 
                              p0=[1.0, T1_EXPECTED, 0.1])
            t_plot = np.linspace(0, 0.2, 100)
            t1_line.set_data(t_plot, exp_decay(t_plot, *popt))
        except: pass
    
    # Status
    status = (f"f_peak: {analysis['f_peak']:.1f}kHz | "
              f"V_steady: {analysis['v_steady']:.2f}V | "
              f"RMS: {analysis['rms']:.2f}V")
    status_text.set_text(status)
    
    return wave_line, fft_line, rabi_line, t1_line  # Fixed return!

# FIXED: blit=False + explicit return
ani = FuncAnimation(fig, update, interval=33, blit=False)
plt.show(block=True)

ser.close()
