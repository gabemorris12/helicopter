import serial
import time
import threading
import re
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import warnings
import numpy as np

warnings.filterwarnings('ignore', category=UserWarning)

time.sleep(3)  # wait for flash to occur
ser = serial.Serial('COM3')

data_pattern = re.compile(r'\(([\n0-9.]+), ([\n0-9.]+)\)')

t_values, angles = [], []


def receive_data():
    t = 0
    t_values_, angles_ = [], []
    while True:
        time.sleep(0.01)
        if ser.in_waiting:
            data = ser.read_all().decode()
            matches = data_pattern.finditer(data)

            for match in matches:
                dt, ang = float(match.group(1)), float(match.group(2))
                t += dt
                t_values_.append(t)
                angles_.append(ang)

            t_values.extend(t_values_)
            angles.extend(angles_)

            t_values_.clear()
            angles_.clear()


def set_angle():
    while True:
        try:
            angle = input('Enter Angle: ')
            float(angle)
        except ValueError:
            print('Type in a number only')
            continue
        else:
            ser.write(angle.encode())


receive_thread = threading.Thread(target=receive_data)
set_thread = threading.Thread(target=set_angle)
receive_thread.start()
set_thread.start()

fig, ax = plt.subplots()
ax.grid()
ax.set_xlabel('Time (s)')
ax.set_ylabel('Angle (deg)')
ax.set_ylim([0, 180])

lines = [ax.plot([], [], color='maroon')[0]]


def init():
    lines[0].set_data([], [])
    return lines


def animate(_):
    lines[0].set_data(t_values, angles)
    n, _ = divmod(t_values[-1], 10)
    ax.set_xlim(10*n, 10*(n + 1))
    return lines


ani = FuncAnimation(fig, animate, init_func=init)
plt.show()
