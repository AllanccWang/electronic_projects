
"""
Quantum Readout Analyzer - 5s Accumulate + Plot
"""

import serial
import numpy as np
import matplotlib.pyplot as plt
import sys
import time

SERIAL_PORT = "COM3"
BAUDRATE = 115200
SAMPLE_RATE = 170000
BUFFER_LEN = 1024

F0_TARGET = 5000
IQ_LEN = 512
ACCUM_TIME = 5.0  # 5 seconds accumulate

def read_packet(ser):
    """Read sync-framed packet"""
    sync = ser.read(2)
    if len(sync) < 2 or sync != b'\xAA\x55':
        return None  # wait for sync
    
    len_bytes = ser.read(2)
    if len(len_bytes) < 2:
        return None
    
    pkt_len = (len_bytes[0] << 8) | len_bytes[1]
    data = ser.read(pkt_len)
    
    if len(data) == pkt_len:
        return np.frombuffer(data, dtype=np.uint16)
    return None

def find_stm32_port():
    import serial.tools.list_ports
    ports = serial.tools.list_ports.comports()
    for p in ports:
        if 'CP2102' in p.description or 'STM32' in p.description:
            return p.device
    return SERIAL_PORT

def iq_demod(wave_data, f0=F0_TARGET, fs=SAMPLE_RATE):
    t = np.arange(len(wave_data)) / fs
    carrier = np.exp(1j * 2 * np.pi * f0 * t)
    iq = wave_data * carrier
    return np.mean(np.real(iq)), np.mean(np.imag(iq))

def main():
    print("=== Quantum Readout Analyzer (5s Accumulate) ===")
    port = find_stm32_port()
    print(f"Connecting to {port}...")
    
    ser = serial.Serial(port, BAUDRATE, timeout=1)
    time.sleep(2)
    
    trial_num = 0
    
    try:
        while True:
            adc_data = read_packet(ser)
            if adc_data is not None:
                voltage = (adc_data.astype(float) / 4095 * 3.3) - 1.65
            print("\nWaiting ESP32 'run' command... (5s accumulate)")
            
            # Accumulate 5 seconds data
            start_time = time.time()
            all_voltage = []
            all_iq = []
            
            while time.time() - start_time < ACCUM_TIME:
                raw = ser.read(2 * BUFFER_LEN)
                if len(raw) == 2 * BUFFER_LEN:
                    # Fix STM32 DMA uint16 endianness + extract 12-bit ADC
                    adc_raw = np.frombuffer(raw, dtype=np.uint16)
                    adc_raw = np.flip(adc_raw.byteswap(), 0)  # byte-swap + reverse
                    adc = adc_raw & 0x0FFF  # extract 12-bit LSB
                    print(f"Fixed ADC range: {adc.min():4d} - {adc.max():4d}")
                    
                    voltage = adc.astype(float) / 4095 * 3.3  # 0-3.3V (no offset)
                    all_voltage.extend(voltage)

                    
                    # Real-time IQ (last chunk)
                    I, Q = iq_demod(voltage[-IQ_LEN:])
                    all_iq.append((I, Q))
                
                # Live stats
                if len(all_voltage) > 0:
                    peak = np.max(np.abs(all_voltage))
                    rms = np.std(all_voltage)
                    elapsed = time.time() - start_time
                    print(f"\rAccum: {elapsed:4.1f}s | Peak:{peak:5.3f}V | RMS:{rms:5.3f}V | Samples:{len(all_voltage):6d}", end="")
            
            trial_num += 1
            all_voltage = np.array(all_voltage)
            
            # Final IQ & Fidelity
            amps = [np.sqrt(I**2 + Q**2) for I, Q in all_iq[-32:]]  # last 32 IQs
            noise_rms = np.std([np.sqrt(I**2 + Q**2) for I, Q in all_iq[:64]])
            threshold = noise_rms * 3.0
            amps = [np.sqrt(I**2 + Q**2) for I, Q in all_iq[-32:]]
            fidelity = np.sum(np.array(amps) > threshold) / len(amps) * 100 if amps else 0

            print(f"\n📊 Trial {trial_num} Complete!")
            print(f"   Noise RMS: {noise_rms:.4f}V, Thresh: {threshold:.4f}V")
            print(f"   Fidelity: {fidelity:.1f}% (32 samples)")
            print(f"   Peak/RMS: {np.max(np.abs(all_voltage)):.3f}V / {np.std(all_voltage):.3f}V")
            print(f"\n📊 Trial {trial_num} Complete!")
            print(f"   Total samples: {len(all_voltage)}")
            print(f"   Fidelity: {fidelity:.1f}%")
            print(f"   Peak/RMS: {np.max(np.abs(all_voltage)):.3f}V / {np.std(all_voltage):.3f}V")
            
            # Plot (only once per trial)
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))
            
            # Full waveform
            t_ms = np.arange(len(all_voltage)) / SAMPLE_RATE * 1000
            ax1.plot(t_ms, all_voltage)
            ax1.set_xlabel("Time (ms)")
            ax1.set_ylabel("Voltage (V)")
            ax1.grid(True)
            ax1.set_title(f"STM32 PA0 - {ACCUM_TIME}s Accumulate")
            
            # IQ History
            if all_iq:
                I_hist = [p[0] for p in all_iq[-64:]]  # last 64 IQ points
                Q_hist = [p[1] for p in all_iq[-64:]]
                ax2.scatter(I_hist, Q_hist, alpha=0.7, s=60)
                ax2.axhline(0, color='k', lw=0.5)
                ax2.axvline(0, color='k', lw=0.5)
                ax2.grid(True)
                ax2.set_xlabel("I")
                ax2.set_ylabel("Q")
                ax2.set_title(f"IQ Plane (Fid: {fidelity:.1f}%)")
            
            plt.tight_layout()
            plt.show(block=False)
            plt.pause(2)  # show 2 seconds
            plt.close()
            
            print("Ready for next ESP32 'run'...")
    
    except KeyboardInterrupt:
        print("\nStopped")
    finally:
        ser.close()

if __name__ == "__main__":
    main()
