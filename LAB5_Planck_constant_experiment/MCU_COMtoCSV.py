import serial
import time
import csv

sensor_file=open('SensorData.csv', mode='w')
sensor_writer=csv.writer(sensor_file, delimiter=',', escapechar=' ', quoting=csv.QUOTE_NONE)
sensor_writer.writerow(["LED voltage", "photoresistor voltage", "Time"])

com = "COM5"
baud = 115200

ser = serial.Serial(com, baud, timeout = 0.1)

while ser.isOpen() == True:
    data = str(ser.readline().decode('utf-8')).rstrip()
    if data is not "":
         print(data)
         dd=data.split(",")
         with open('SensorData.csv', mode='a') as sensor_file:
             sensor_writer = csv.writer(sensor_file)
             sensor_writer.writerow([int(dd[0]), int(dd[1]), str(time.asctime())])
             
# Close port and CSV file to exit
ser.close()
sensor_file.close()
print("logging finished")

'''
The next step is to edit this data in order for it to be represented in graphical form.
First, you’ll have to delete all unnecessary spaces.
To do that, press F5 > Click “Special” > Select “Empty”.
'''