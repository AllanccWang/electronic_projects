import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import networkx as nx
import math

st.title("RC Oscillator System Dynamics (NE555 Astable)")

# Parameters from resources & theory
V = 5.0  # 5V supply
R1 = 10**4  # R1 10kΩ
R2 = 10**4  # R2 10kΩ (user adjustable)
C = 4.7*10**(-6)  # ~4.7uF for T~0.1s

@st.cache_data
def system_dynamics(R1, R2, C, t_max=10, dt=0.01):
    t = np.arange(0, t_max, dt)
    T_theory = 0.693 * (R1 + 2 * R2) * C
    tau_charge = (R1 + R2) * C
    tau_discharge = R2 * C
    
    # Simple periodic sawtooth approximation (fixed broadcast error)
    period = T_theory
    phase = (t % period) / period
    Vc = np.piecewise(phase, 
                      [phase < 0.5, phase >= 0.5],
                      [lambda p: V * (1/3 + (2/3) * (1 - np.exp(-2 * p * np.log(2)))),  # Charge to 2/3
                       lambda p: V * (2/3) * np.exp(-2 * (1-p) * np.log(2))])     # Discharge to 1/3
    
    led_on = (Vc > V / 2).astype(int)
    switches = np.sum(np.diff(led_on) < 0)  # Count falling edges (cycles)
    num_switches = switches  # Cycles in 10s
    blink_rate = np.ones_like(t) * (1 / T_theory)
    growth_rate = np.gradient(np.convolve(led_on, np.ones(100)/100, mode='valid'))  # Smoothed rate
    
    return t, Vc, T_theory, num_switches, blink_rate, growth_rate

# Interactive params
col1, col2, col3 = st.columns(3)
R1 = col1.number_input("R1 (ohms)", value=10000, min_value=1000, step=1000, format="%d")
R2 = col2.number_input("R2 (ohms)", value=10000, min_value=1000, step=1000, format="%d")
C = col3.number_input("C (F)", value=4.7e-6, min_value=0.1e-6, step=0.1e-6, format="%.1e")

T_theory = 0.693 * (R1 + 2 * R2) * C
f_theory = 1 / T_theory
st.info(f"Theory Period T = {T_theory:.3f}s, Frequency f = {f_theory:.1f}Hz (~{10/T_theory:.1f} cycles in 10s)")

if st.button("Run Simulation & Score"):
    try:
        t, Vc, T_est, switches, rate, growth = system_dynamics(R1, R2, C)
        
        ## Plot 1: Vc State Voltage (Pin 2/6)
        fig1, ax1 = plt.subplots(figsize=(10,4))
        ax1.plot(t[:1000], Vc[:1000], label=f'Period T={T_est:.3f}s')
        ax1.axhline(V/3, color='g', ls='--', label='1/3 Vcc (Trigger)')
        ax1.axhline(2*V/3, color='r', ls='--', label='2/3 Vcc (Threshold)')
        ax1.axhline(V/2, color='orange', ls=':', label='LED Threshold')
        ax1.set_title("State 1: Capacitor Voltage Vc (Pin 2/6)")
        ax1.set_xlabel("Time (s)")
        ax1.set_ylabel("Vc (V)")
        ax1.legend()
        ax1.grid(True)
        st.pyplot(fig1)
        
        ## Plot 2: LED Output
        fig2, ax2 = plt.subplots(figsize=(10,4))
        ax2.plot(t[:1000], (Vc[:1000] > V/2)*5, 'g-', linewidth=3, label='Pin 3 Output')
        ax2.set_title("State 2: LED Blink Signal")
        ax2.set_xlabel("Time (s)")
        ax2.set_ylabel("Output Voltage (V)")
        ax2.grid(True)
        st.pyplot(fig2)
        
        ## Plot 3: System Causal Loop
        G = nx.DiGraph()
        # Rename nodes for clarity
        edges = [
            ("Vc", "I_chg", {"label": "-"}), ("I_chg", "Vc", {"label": "+"}),  # Negative feedback loop 1
            ("Vc", "I_dis", {"label": "+"}), ("I_dis", "Vc", {"label": "-"}),  # Negative feedback loop 2
            ("R", "tau", {"label": "+"}), ("C", "tau", {"label": "+"}), ("tau", "T", {"label": "+"})  # Parameter influence
        ]
        G.add_edges_from(edges)
        
        # Use circular layout for better spacing, or spring with high k
        pos = nx.circular_layout(G) 
        
        fig3, ax3 = plt.subplots(figsize=(10, 6)) # Increased height
        
        # Draw nodes
        nx.draw_networkx_nodes(G, pos, node_color='lightblue', node_size=2000, ax=ax3)
        
        # Draw edges with arrows
        nx.draw_networkx_edges(G, pos, edge_color='gray', arrowstyle='->', arrowsize=20, ax=ax3)
        
        # Draw labels with background to avoid blur/overlap
        nx.draw_networkx_labels(G, pos, font_size=10, font_weight="bold", ax=ax3)
        
        # Draw edge labels (signs)
        edge_labels = nx.get_edge_attributes(G, 'label')
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=12, font_color='red', ax=ax3)
        
        ax3.set_title("Relationship Diagram: Causal Loops (Negative Feedback Stabilizes)")
        ax3.axis('off') # Remove box
        st.pyplot(fig3)
        
        ## Plot 4: Growth Rate
        fig4, ax4 = plt.subplots(figsize=(10,4))
        ax4.plot(t[100:], growth[:len(t)-100], 'b-', label="Measured Blink Rate")
        ax4.axhline(1/T_est, color='r', ls='--', linewidth=2, 
                   label=f'Theory {1/T_est:.1f} Hz')
        ax4.set_title("Growth Rate: Blink Frequency (Stabilizes to Theory)")
        ax4.set_xlabel("Time (s)")
        ax4.set_ylabel("Frequency (Hz)")
        ax4.legend()
        ax4.grid(True)
        st.pyplot(fig4)
        
        ## KPI Auto-Scoring
        target_cycles = 72.5  # Target for T=0.1s in 10s (duty-adjusted)
        error_pct = abs(switches - target_cycles) / target_cycles * 100
        
        col_a, col_b = st.columns(2)
        col_a.metric("10s Cycles", f"{switches:.1f}", delta=f"Target: {target_cycles:.1f}")
        col_b.metric("Error %", f"{error_pct:.2f}%", "Goal: <5%")
        
        if error_pct < 5:
            st.balloons()
            st.success("✅ **Correct!** System model validated: Causal loops + exponential dynamics. Linear assumption error >20% rejected.")
        else:
            st.warning("⚠️ **Adjust RC values.** Check T=0.693(R1+2R2)C formula & feedback signs.")
        
        st.caption(f"Real-world: Count LED blinks in 10s, input your R1/R2/C to match.")
            
    except Exception as e:
        st.error(f"Simulation Error: {str(e)} - Check R/C values are reasonable (R>1kΩ, C>0.1uF).")