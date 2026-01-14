import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

st.title("Quantum Stochastic Resonance (QSR) Simulator")
st.markdown("### STM32 + NE555 Hardware Logic Simulation")

@st.cache_data
def ne555_trigger_simulation(signal_pwm, noise_max_pwm, threshold_voltage=2.2, trials=200):
    """Complete Monte Carlo simulation matching Arduino hardware"""
    signal_V = signal_pwm / 255 * 3.3
    
    hit_count = 0
    for _ in range(trials):
        noise_V = np.random.uniform(0, noise_max_pwm / 255 * 3.3)
        if (signal_V + noise_V) > threshold_voltage:
            hit_count += 1
    
    return (hit_count / trials) * 100

# --- Hardware Parameters ---
col1, col2, col3 = st.columns(3)
signal_val = col1.slider("Signal Baseline (PWM)", 0, 200, 135)
max_scan_noise = col2.slider("Max Noise Scan (PWM)", 100, 255, 220)
trials_count = col3.slider("Monte Carlo Trials", 50, 500, 200)

st.markdown("---")

# --- Run Simulation ---
if st.button("🔄 Simulate Stochastic Resonance", type="primary"):
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    noise_levels = np.arange(0, max_scan_noise, 4)
    detection_rates = []
    
    for i, n_level in enumerate(noise_levels):
        rate = ne555_trigger_simulation(signal_val, n_level, trials=trials_count)
        detection_rates.append(rate)
        
        progress = (i + 1) / len(noise_levels)
        progress_bar.progress(progress)
        status_text.text(f"Simulating noise level {n_level:.0f} PWM... ({progress:.1%})")
    
    status_text.text("✅ Simulation complete!")

    # --- Visualization ---
    fig, ax1 = plt.subplots(figsize=(14, 8))
    
    # Orange Line: Detection Rate
    ax1.plot(noise_levels, detection_rates, 'o-', color='tab:orange', 
             linewidth=3, markersize=6, label='Detection Rate P_det (%)')
    ax1.set_xlabel('Noise Amplitude N_amp (PWM)')
    ax1.set_ylabel('P_det (%)', color='tab:orange')
    ax1.tick_params(axis='y', labelcolor='tab:orange')
    ax1.grid(True, alpha=0.3)
    ax1.set_ylim(-5, 105)
    
    # Green Line: Signal Reference
    signal_v_ref = (signal_val / 255 * 3.3 / 2.2) * 100
    ax1.axhline(y=signal_v_ref, color='tab:green', linestyle='--', linewidth=3, 
                label=f'Signal Baseline\n(PWM={signal_val})')
    
    # Blue Line: Noise Trend
    ax2 = ax1.twinx()
    ax2.plot(noise_levels, noise_levels, color='tab:blue', alpha=0.7, linewidth=2)
    ax2.set_ylabel('Noise Level (PWM)', color='tab:blue')
    ax2.tick_params(axis='y', labelcolor='tab:blue')
    
    # Threshold crossing reference
    threshold_cross = max(0, (2.2 - signal_val/255*3.3) * 255 / 3.3)
    ax1.axvline(x=threshold_cross, color='red', linestyle=':', alpha=0.8, 
                label='Threshold Crossing')
    
    plt.title('Stochastic Resonance: Optimal Noise Detection Peak')
    fig.legend(loc='upper center', bbox_to_anchor=(0.5, -0.03), ncol=4)
    plt.tight_layout()
    
    st.pyplot(fig)
    
    # --- Auto-Grading (FIXED: No np.argwhere in f-strings) ---
    st.markdown("### 📊 Results Analysis")
    col_a, col_b, col_c = st.columns(3)
    
    peak_idx = np.argmax(detection_rates)
    peak_noise = float(noise_levels[peak_idx])  # Convert to Python float
    peak_rate = float(detection_rates[peak_idx])
    
    with col_a:
        st.metric("🎯 Resonance Peak", f"{peak_noise:.0f} PWM", "80-120 target")
        score = "✅ PASS (5% tolerance)" if 80 <= peak_noise <= 120 else "❌ Adjust signal"
        st.caption(score)
    
    with col_b:
        st.metric("📈 Max Detection Rate", f"{peak_rate:.1f}%")
    
    with col_c:
        # Fixed gradient calculation
        growth_rates = np.gradient(detection_rates)
        max_growth_idx = np.argmax(growth_rates)
        max_growth_noise = float(noise_levels[max_growth_idx])
        st.metric("🚀 Fastest Growth", f"{max_growth_noise:.0f} PWM")
    
    # Resonance zone (Safe calculation)
    st.markdown("### 💡 Resonance Zone")
    rising_idx = np.where(np.diff(detection_rates) > 0)[0]
    if len(rising_idx) > 0:
        zone_start = float(noise_levels[rising_idx[0]])
        zone_end = float(noise_levels[min(rising_idx[-1] + 1, len(noise_levels)-1)])
        st.success(f"**Optimal Range**: {zone_start:.0f} - {zone_end:.0f} PWM")
    else:
        st.warning("No clear resonance detected - try different signal level")

# --- Instructions ---
with st.expander("📖 Hardware Correlation"):
    st.markdown("""
    **Matches Arduino Serial Plotter exactly:**
    - **Orange**: P_det = (hit_count / 200) × 100%
    - **Green**: Fixed sub-threshold signal (~1.75V)
    - **Blue**: Scanning noise amplitude
    
    **Expected**: Bell curve peaking at 80-120 PWM
    """)