import serial
import time

time.sleep(3)  # wait for flash to occur
ser = serial.Serial('COM3')

while True:
    try:
        angle = input('Enter Message: ')
        float(angle)
    except ValueError:
        print('Type in a number only')
        continue
    else:
        ser.write(angle.encode())
