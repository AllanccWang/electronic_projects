import streamlit as st
import matplotlib.pyplot as plt
import numpy as np

st.title("Multi-Sensor Fusion Structural Stability")

# =============================================================================
# PARAMETERS - Sidebar
# =============================================================================
st.sidebar.header("Simulation Parameters")
mass_motor = st.sidebar.slider("Motor Mass (g)", 50, 200, 100)
total_weight = st.sidebar.slider("Total Weight (g)", 900, 1200, 1100)
friction_factor = st.sidebar.slider("Friction Factor", 0.1, 0.5, 0.3)

# =============================================================================
# CORE SYSTEM DYNAMICS
# =============================================================================
def system_dynamics(angle_degrees, total_weight, mass_motor, friction_factor):
    """Physics-based Stability Index"""
    theta = np.radians(angle_degrees)
    
    # Non-linear geometric effect
    geo_factor = np.sin(theta)
    
    # Load Cell: mass distribution
    mass_ratio = mass_motor / total_weight
    
    # MPU6050: torque amplification
    torque_amp = 1 + 2 * np.tanh(theta)
    
    # Raw instability
    instability = geo_factor * mass_ratio * torque_amp
    
    # Friction resistance
    friction = friction_factor * np.cos(theta)
    
    si = np.clip(instability - friction, 0, 1)
    return si

# =============================================================================
# AUTO SCORING (Defined First)
# =============================================================================
def auto_score(stability, angles):
    """4-criteria evaluation for <5% error"""
    score = 100
    growth_rate = np.gradient(stability, angles)
    
    # Display results in columns
    col1, col2 = st.columns(2)
    
    # Test 1: Range [0,1]
    if np.min(stability) >= 0 and np.max(stability) <= 1.05:
        col1.metric("SI Range", "✅ PASS")
    else:
        score -= 20
        col1.metric("SI Range", "❌ FAIL")
    
    # Test 2: Strong feedback
    if np.std(growth_rate) > 0.015:
        col2.metric("Dynamics", "✅ STRONG")
    else:
        score -= 30
        col2.metric("Dynamics", "⚠️ WEAK")
    
    # Test 3: Non-linear fusion
    linear_model = angles / 45.0
    correlation = abs(np.corrcoef(stability, linear_model)[0,1])
    if correlation < 0.92:
        st.success(f"✅ Non-linear: corr={correlation:.2f}")
    else:
        score -= 30
        st.warning(f"🔄 Too linear: corr={correlation:.2f}")
    
    # Test 4: Early warning <38°
    alert_idx = np.argmax(stability > 0.8)
    alert_angle = angles[alert_idx] if alert_idx < len(angles) else 45
    early_warning = alert_angle < 38
    
    if early_warning:
        st.success(f"✅ Early alert: {alert_angle:.1f}°")
    else:
        score -= 20
        st.warning(f"⚠️ Late alert: {alert_angle:.1f}°")
    
    return score, alert_angle, np.max(growth_rate)

# =============================================================================
# RUN SIMULATION
# =============================================================================
st.header("Real-time Analysis")
if st.button("🚀 Analyze Structure", type="primary"):
    
    # Generate test data
    angles = np.linspace(0, 45, 100)
    stability_values = np.array([
        system_dynamics(angle, total_weight, mass_motor, friction_factor)
        for angle in angles
    ])
    
    # =============================================================================
    # 4 SCORING CHARTS - FIXED PLOTTING
    # =============================================================================
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 10))
    
    # Chart 1: Stability vs Angle
    ax1.plot(angles, stability_values, 'blue', linewidth=3, label='Fused Model')
    ax1.axhline(y=0.8, color='orange', linestyle='--', label='Warning (0.8)')
    ax1.axhline(y=1.0, color='red', linestyle='--', label='Collapse (1.0)')
    ax1.set_title("State 1: Stability Index vs Angle", fontweight='bold')
    ax1.set_xlabel("Tilt Angle (degrees)")
    ax1.set_ylabel("Stability Index (0-1)")
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Chart 2: Weight Effect
    weight_shift = np.sin(np.radians(angles)) * (mass_motor / total_weight)
    ax2.plot(weight_shift, stability_values, 'green', linewidth=3)
    ax2.set_title("State 2: Weight Shift Effect", fontweight='bold')
    ax2.set_xlabel("Weight Ratio (m/total)")
    ax2.set_ylabel("Stability Index")
    ax2.grid(True, alpha=0.3)
    
    # Chart 3: Causal Diagram
    ax3.plot(angles, weight_shift, 'red', linewidth=3)
    ax3.set_title("Causal Relation Diagram", fontweight='bold')
    ax3.set_xlabel("Tilt Angle (degrees)")
    ax3.set_ylabel("Weight Shift Ratio")
    ax3.grid(True, alpha=0.3)
    
    # Chart 4: Growth Rate
    growth = np.gradient(stability_values, angles)
    ax4.plot(angles, growth, 'purple', linewidth=3)
    ax4.axhline(y=0.02, color='orange', linestyle='--', label='Alert Rate')
    ax4.set_title("Growth Rate of Instability", fontweight='bold')
    ax4.set_xlabel("Tilt Angle (degrees)")
    ax4.set_ylabel("d(SI)/dθ")
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    st.pyplot(fig)
    
    # =============================================================================
    # FINAL RESULTS
    # =============================================================================
    st.subheader("🤖 Auto-Scoring")
    final_score, warning_angle, max_growth = auto_score(stability_values, angles)
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Final Score", f"{final_score}/100")
    col2.metric("Warning Trigger", f"{warning_angle:.1f}°")
    col3.metric("Peak Instability", f"{max_growth:.3f}")
    
    if final_score >= 95:
        st.balloons()
        st.success("🎉 **100% PASS! Deploy to ESP32**")
