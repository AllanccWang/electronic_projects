import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

def ne555_resonator_freq(qubit_freq, coupling_cap_effective, mode="A"):
    """
    Simulate NE555 #2 (Resonator) frequency shift based on NE555 #1 (Qubit) operation.
    
    Parameters:
    - qubit_freq (Hz): Output frequency of NE555 #1 (Input)
    - coupling_cap_effective (0.0-1.0): 1uF capacitor coupling strength (Control)
    - mode: "A" (Linear) or "B" (Nonlinear/Realistic)
    
    Returns:
    - f_r (Hz): Frequency of NE555 #2 Pin 3 (Output)
    """
    uncoupled_baseline = 9000
    
    # 1. Baseline Shift: 1uF capacitor always introduces a DC offset on Pin 5
    # This happens regardless of the qubit frequency.
    coupling_baseline_shift = 250 * coupling_cap_effective
    
    # 2. Frequency Modulation: AC signal from NE555 #1 modulates Pin 5 voltage
    # The phase and amplitude depend on the qubit frequency.
    # sin() term creates different shifts for 8000Hz vs 9000Hz
    freq_modulation = 250 * coupling_cap_effective * np.sin(2 * np.pi * qubit_freq / 9500)
    
    if mode == "A":
        # Linear Model
        f_r = uncoupled_baseline + coupling_baseline_shift + freq_modulation
    else:
        # Nonlinear Model: Adds saturation and noise
        # Pin 5 cannot accept infinite voltage change (Saturation)
        saturation = 200 * coupling_cap_effective * (1 - np.exp(-abs(freq_modulation)))
        # Stronger coupling picks up more electrical noise
        coupling_noise = 100 * coupling_cap_effective * np.random.randn()
        f_r = uncoupled_baseline + coupling_baseline_shift + freq_modulation + saturation + coupling_noise
    
    return max(8700, f_r)

def esp32_readout(f_r):
    """ESP32 Logic: Determine state based on frequency threshold"""
    if f_r > 9100:
        return "|1⟩"
    elif f_r < 9050:
        return "|0⟩"
    return "❓"

# -----------------------------------------------------------
# Streamlit UI Layout
# -----------------------------------------------------------
st.title("NE555 Dispersive Readout Simulator")

# 1. Parameter Definitions (Requested Feature)
st.markdown("""
### 📝 Parameter Definitions
*   **Qubit Freq ($f_q$)**: The output frequency of NE555 #1. 
    *   8000Hz |0> (Ground State)
    *   9000Hz |1> (Excited State)
*   **Coupling Strength**: The effective impact of the **1uF capacitor** connecting the two circuits.
    *   0.0: Capacitor removed (No interaction).
    *   1.0: Strong coupling (Maximum frequency shift).
*   **Resonator Freq ($f_r$)**: The output frequency of NE555 #2 (The Readout).
    *   We measure this to infer the state of the Qubit.
""")

st.divider()

# 2. Sidebar Controls (Removed "Parameters" header)
# Re-added Mode Selector so Model B can be tested
mode = st.sidebar.selectbox("Physics Model", ["A: Linear", "B: Nonlinear (w/ Noise)"])

qubit_freq_0 = st.sidebar.slider("Qubit |0⟩ f_q (Hz)", 7900, 8100, 8000, 25)
qubit_freq_1 = st.sidebar.slider("Qubit |1⟩ f_q (Hz)", 8900, 9100, 9000, 25)
coupling_cap_effect = st.sidebar.slider("1uF Capacitor Effect (0-1)", 0.0, 1.0, 0.8, 0.05)

# 3. Calculations
mode_key = "A" if "A" in mode else "B"
f_r0 = ne555_resonator_freq(qubit_freq_0, coupling_cap_effect, mode_key)
f_r1 = ne555_resonator_freq(qubit_freq_1, coupling_cap_effect, mode_key)

# 4. Readout Display
col1, col2 = st.columns(2)
col1.metric("NE555 #2 Output ($f_r$) for |0⟩", f"{f_r0:.0f} Hz", esp32_readout(f_r0))
col2.metric("NE555 #2 Output ($f_r$) for |1⟩", f"{f_r1:.0f} Hz", esp32_readout(f_r1))

st.metric("Frequency Difference (Dispersive Shift)", f"{abs(f_r1 - f_r0):.0f} Hz")

# -----------------------------------------------------------
# Visualization Charts
# -----------------------------------------------------------
fig, axes = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle(f"1uF Coupling Analysis (Mode: {mode_key})")

# Chart 1: Bar Comparison
baseline = 9000
axes[0,0].bar(["No coupling", "|0⟩ +1uF", "|1⟩ +1uF"], 
              [baseline, f_r0, f_r1],
              color=['gray', 'blue', 'red'])
axes[0,0].axhline(y=9100, color='green', ls='--', lw=2, label='|1⟩ Threshold')
axes[0,0].axhline(y=9050, color='orange', ls='--', lw=2, label='|0⟩ Threshold')
axes[0,0].set_title("Readout Frequency Shift")
axes[0,0].set_ylabel("NE555 #2 f_r (Hz)")
axes[0,0].legend()

# Chart 2: Qubit Frequency Sweep
f_q_range = np.linspace(7800, 9200, 60)
f_r_range = [ne555_resonator_freq(fq, coupling_cap_effect, mode_key) for fq in f_q_range]
axes[0,1].plot(f_q_range, f_r_range, 'b-', lw=3)
axes[0,1].axhline(y=9100, color='green', ls='--', lw=2)
axes[0,1].axhline(y=9050, color='orange', ls='--', lw=2)
axes[0,1].axhline(y=baseline, color='gray', ls=':', label='No coupling')
axes[0,1].set_title(f"f_q vs f_r (Coupling={coupling_cap_effect})")
axes[0,1].set_xlabel("Qubit Input f_q (Hz)")
axes[0,1].set_ylabel("Readout Output f_r (Hz)")
axes[0,1].grid(True, alpha=0.3)

# Chart 3: Coupling Strength Effect (Both States)
coupling_range = np.linspace(0.0, 1.0, 50)
f_r0_coupling = [ne555_resonator_freq(8000, c, mode_key) for c in coupling_range]
f_r1_coupling = [ne555_resonator_freq(9000, c, mode_key) for c in coupling_range]
axes[1,0].plot(coupling_range, f_r0_coupling, 'b-', lw=3, label="|0⟩ f_q=8000Hz")
axes[1,0].plot(coupling_range, f_r1_coupling, 'r-', lw=3, label="|1⟩ f_q=9000Hz")
axes[1,0].axhline(y=9100, color='green', ls='--', lw=2)
axes[1,0].axhline(y=baseline, color='gray', ls=':', alpha=0.7)
axes[1,0].set_title("Coupling Strength Impact")
axes[1,0].set_xlabel("1uF Effective Coupling (0 to 1)")
axes[1,0].set_ylabel("Readout Output f_r (Hz)")
axes[1,0].legend()
axes[1,0].grid(True)

# Chart 4: Noise Visualization (Only visible in Mode B)
if mode_key == "B":
    noise_trials = 100
    coupling_vals = np.linspace(0.2, 1.0, 5)
    for c in coupling_vals:
        f_r_noise = [ne555_resonator_freq(8500, c, "B") for _ in range(noise_trials)]
        axes[1,1].scatter([c]*noise_trials, f_r_noise, alpha=0.3, s=15)
    axes[1,1].set_title("Noise Pickup (Mode B)")
    axes[1,1].set_xlabel("Coupling Strength")
    axes[1,1].set_ylabel("f_r Distribution")
else:
    axes[1,1].text(0.5, 0.5, "Switch to Mode B to see noise", 
                   ha='center', va='center', fontsize=12)
    axes[1,1].set_title("Noise Pickup (Linear Mode - Clean)")

plt.tight_layout()
st.pyplot(fig)
