import serial
import csv
import matplotlib.pyplot as plt
import time

# --- Configuration ---
# check your COM port in Arduino IDE
SERIAL_PORT = 'COM#'  
BAUD_RATE = 115200
SAVE_FILE = "training_data.csv"
# ---------------------

def main():
    # Initialize lists OUTSIDE the try block to avoid UnboundLocalError
    pwm_list = []
    feedback_list = []
    load_sense_list = []
    ser = None

    try:
        # Initialize Serial Connection
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        time.sleep(2)  # Wait for connection to stabilize
        
        print(f"Success: Connected to {SERIAL_PORT}")
        print("Instructions: Adjust your potentiometer and let the ESP32 complete the sweeps.")
        print("Action: Press 'Ctrl+C' to stop recording and generate the graph.")

        # Create CSV and write header
        with open(SAVE_FILE, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["PWM_Duty", "Feedback_ADC", "Load_Sense_ADC"])

            while True:
                if ser.in_waiting > 0:
                    line = ser.readline().decode('utf-8', errors='ignore').strip()
                    
                    if not line or line.startswith('#'):
                        if "Starting New Sweep" in line:
                            print("\n>>> Status: New Sweep Detected...")
                        continue
                    
                    try:
                        parts = line.split(',')
                        if len(parts) == 3:
                            pwm = float(parts[0])
                            v_fb = float(parts[1])
                            l_sn = float(parts[2])
                            
                            writer.writerow([pwm, v_fb, l_sn])
                            
                            pwm_list.append(pwm)
                            feedback_list.append(v_fb)
                            load_sense_list.append(l_sn)
                            
                            print(f"Recording: PWM={pwm:>3.0f} | V_FB={v_fb:>7.2f} | L_Sense={l_sn:>7.2f}", end='\r')
                    except ValueError:
                        continue

    except KeyboardInterrupt:
        print("\n\nProcess: Collection stopped by user.")
    except Exception as e:
        print(f"\nError: {e}")
        print("Check if the Serial Port is correct and not used by Arduino IDE.")
    finally:
        if ser and ser.is_open:
            ser.close()
        
        # --- Visualization Section ---
        if len(pwm_list) > 0:
            print(f"Summary: Captured {len(pwm_list)} samples. Generating plots...")
            plt.figure(figsize=(10, 6))
            scatter = plt.scatter(pwm_list, feedback_list, c=load_sense_list, cmap='plasma', s=15)
            plt.colorbar(scatter).set_label('Load_Sense_ADC')
            plt.title('V-Feedback vs PWM (Multiple Loads)')
            plt.xlabel('PWM Duty')
            plt.ylabel('Feedback ADC')
            plt.grid(True)
            plt.show()
        else:
            print("\nResult: No data was captured. Plotting skipped.")

if __name__ == "__main__":
    main()