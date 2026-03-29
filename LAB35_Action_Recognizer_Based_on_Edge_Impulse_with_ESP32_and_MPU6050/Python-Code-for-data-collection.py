import serial
import time

ser = serial.Serial('COM#', 115200, timeout=1) 
file_name = "stirring.csv"

with open(file_name, "w") as f:

    f.write("timestamp,accX,accY,accZ\n") 
    print(f"Recording into {file_name}...")
    
    start_time = time.time()
    current_ms = 0
    
    while time.time() - start_time < 10:
        line = ser.readline().decode('utf-8').strip()
        if line:
            
            f.write(f"{current_ms},{line}\n")
            print(f"{current_ms}: {line}")
            current_ms += 20

ser.close()
print("Complete the Record！")