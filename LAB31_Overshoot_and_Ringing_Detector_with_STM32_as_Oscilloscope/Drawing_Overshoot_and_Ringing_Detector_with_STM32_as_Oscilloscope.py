import serial
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from scipy.ndimage import uniform_filter1d
from scipy.signal import find_peaks


# ===== User settings =====
PORT = "COM3"
BAUD = 115200
BUFFER_SIZE = 1024
VREF = 3.3
SAMPLE_RATE = 170000  # Hz, adjust to actual ADC/TIM settings


# Trigger & Analysis params
TRIGGER_THRESHOLD = 0.5 * VREF   # trigger threshold
PRE_SAMPLES = 100
POST_SAMPLES = 300
STEADY_FRAC = 0.9
RINGING_FRAC = 0.2
MAX_RINGING_FREQ = 200000  # Hz, expected max ringing freq


# ===== Serial init =====
ser = serial.Serial(PORT, BAUD, timeout=0.5)


# ===== Analysis functions =====
def detect_rising_edge_window(
    volt,
    threshold=TRIGGER_THRESHOLD,
    pre_samples=PRE_SAMPLES,
    post_samples=POST_SAMPLES,
):
    """Find first rising edge and cut a window around it (volt in V)."""
    above = volt > threshold
    rising = np.diff(above.astype(int)) > 0
    trigger_candidates = np.where(rising)[0]
    if len(trigger_candidates) == 0:
        return None, None, None

    trigger_idx = trigger_candidates[0]

    start = max(0, trigger_idx - pre_samples)
    end = min(len(volt), trigger_idx + post_samples)
    window = volt[start:end]

    return trigger_idx, window, start


def analyze_overshoot_ringing(
    window,
    steady_frac=STEADY_FRAC,
    ringing_frac=RINGING_FRAC,
):
    """Compute overshoot & ringing metrics; return None if window is bad."""
    if window is None or len(window) < 100:
        return None

    # Require enough high-level samples; otherwise skip this window
    high_mask = window > (0.7 * VREF)
    if np.sum(high_mask) < 10:
        return None

    # Steady-state: average high-level samples
    v_steady = np.mean(window[high_mask])

    # Rising edge completion: first time reaching 90% of steady
    pct90 = 0.9 * v_steady
    reach90 = np.where(window >= pct90)[0]
    rise_end = reach90[0] if len(reach90) > 0 else len(window) // 2

    # Overshoot
    post_rise = window[rise_end:]
    v_max = np.max(post_rise)
    overshoot_pct = (
        100 * (v_max - v_steady) / v_steady if v_steady > 0 else 0
    )

    # Ringing region
    ringing_len = int(ringing_frac * len(window))
    ringing_data = post_rise[:ringing_len]

    # Minimum period in samples (limit highest freq)
    if MAX_RINGING_FREQ > 0:
        min_period_samples = int(SAMPLE_RATE / MAX_RINGING_FREQ)
        min_period_samples = max(min_period_samples, 2)
    else:
        min_period_samples = 2

    peaks, _ = find_peaks(
        ringing_data,
        height=v_steady * 1.01,
        distance=min_period_samples,
    )

    if len(peaks) < 2:
        ringing_freq_khz = 0.0
        decay_ratio = 0.0
    else:
        peak_amps = ringing_data[peaks] - v_steady
        valid = peak_amps > 0
        if np.sum(valid) >= 2:
            peak_amps = peak_amps[valid]
        decay_ratio = (
            100 * peak_amps[-1] / peak_amps[0] if peak_amps[0] > 0 else 0
        )
        peak_diffs = np.diff(peaks) / SAMPLE_RATE  # seconds
        f_hz = 1.0 / np.mean(peak_diffs)
        ringing_freq_khz = f_hz / 1000.0

    return {
        "overshoot_pct": overshoot_pct,
        "v_steady": v_steady,
        "v_max": v_max,
        "ringing_freq_khz": ringing_freq_khz,
        "decay_ratio_pct": decay_ratio,
        "num_peaks": len(peaks),
    }


# ===== Matplotlib setup =====
plt.ion()
fig, (ax1, ax2) = plt.subplots(2, 1, height_ratios=[3, 1])

WINDOW = 256
x = np.arange(WINDOW)
y = np.zeros(WINDOW)
wave_line, = ax1.plot(x, y, label="waveform")

ax1.set_xlabel("Sample index")
ax1.set_ylabel("Voltage (V)")
ax1.set_ylim(0, VREF)
ax1.set_title("STM32 Oscilloscope + Overshoot/Ringing Detector")

status_ax = ax2
status_ax.axis("off")
status_text = status_ax.text(
    0.05, 0.5, "Ready...", transform=status_ax.transAxes, va="center", fontsize=12
)

latest_results = None


def update(frame):
    global latest_results

    n_bytes = BUFFER_SIZE * 2
    raw = ser.read(n_bytes)
    if len(raw) != n_bytes:
        print(f"Short read: {len(raw)} bytes")
        return wave_line, status_text

    # ADC -> volts
    data = np.frombuffer(raw, dtype=np.uint16)
    volt = data * VREF / 4095.0
    smooth = uniform_filter1d(volt, size=8)

    # ---- detect & analyze on full buffer ----
    trigger_idx, window, start = detect_rising_edge_window(smooth)
    if window is not None:
        latest_results = analyze_overshoot_ringing(window)
        if latest_results is not None:
            print(
                f"Trigger {trigger_idx}, win_len {len(window)}, "
                f"ADC_max {data.max()} counts, "
                f"V_max_window {window.max():.3f} V, "
                f"peaks {latest_results['num_peaks']}"
            )

    # ---- display: always show last WINDOW samples (oscilloscope view) ----
    segment = smooth[-WINDOW:]
    x_seg = np.arange(len(segment))

    wave_line.set_xdata(x_seg)
    wave_line.set_ydata(segment)
    ax1.set_xlim(x_seg[0], x_seg[-1])
    ax1.set_ylim(0, VREF)

    # remove old V_steady / V_max lines
    for line_obj in ax1.get_lines()[1:]:
        line_obj.remove()

    # draw V_steady, V_max if valid results
    if latest_results is not None:
        res = latest_results
        ax1.axhline(
            res["v_steady"],
            color="g",
            ls="--",
            alpha=0.8,
            label="V_steady",
        )
        ax1.axhline(
            res["v_max"],
            color="r",
            ls="--",
            alpha=0.8,
            label="V_max",
        )
        ax1.legend(loc="upper right")

        status = (
            f"Overshoot {res['overshoot_pct']:.1f}%  |  "
            f"Ring {res['ringing_freq_khz']:.1f} kHz\n"
            f"decay {res['decay_ratio_pct']:.0f}%  |  "
            f"Vsteady {res['v_steady']:.2f} V"
        )
    else:
        status = "No valid rising edge window"

    status_text.set_text(status)

    return wave_line, status_text


ani = FuncAnimation(fig, update, interval=50, blit=True)
plt.tight_layout()
plt.show()

try:
    while True:
        plt.pause(0.1)
except KeyboardInterrupt:
    ser.close()
