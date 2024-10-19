import time
import matplotlib.pyplot as plt
from drawnow import *
import serial

val = [ ]
cnt = 0

#create the serial port object
port = serial.Serial('COM5', 115200, timeout=0.5)
plt.ion()


#create the figure function
def makeFig():
    plt.ylim(1000,5500)
    plt.title('Osciloscope')
    plt.grid(True)
    plt.ylabel('data')
    plt.plot(val, 'ro-', label='Channel 0')
    plt.legend(loc='lower right')


while (True):

    port.write(b's') #handshake with Arduino
    if (port.inWaiting()):# if the arduino replies
        value = port.readline()# read the reply
        print(value)#print so we can monitor it
        number = int(float(value)) #convert received data to integer 
        print('Channel 1: {0}'.format(number))
        # Sleep for half a second.
        time.sleep(0.01)
        val.append(number)
        drawnow(makeFig)#update plot to reflect new data input
        plt.pause(.000001)
        cnt = cnt+1
    if(cnt>50):
        val.pop(0)#keep the plot fresh by deleting the data at position 0