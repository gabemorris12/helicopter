import sys
import time
from _thread import start_new_thread

import select
from machine import ADC, Pin, PWM

from pid import PID

Kp = 1500
Ki = 1500
Kd = 500

ang_points = (8200, 52882)  # angle at 0 degrees and 180 degrees

kill_button = Pin(17, Pin.IN, Pin.PULL_DOWN)
poll = select.poll()
poll.register(sys.stdin, 1)

adc = ADC(26)

pwm = PWM(Pin(11))
pwm.freq(1000)

pid = PID(Kp, Ki, Kd, set_point=90, output_limits=(0, 65535))


def receive_input():
    # helpful source can be found here: https://electrocredible.com/raspberry-pi-pico-serial-uart-micropython/
    data = []
    while poll.poll(0):  # for some reason, it has to be like this ...
        data.append(sys.stdin.read(1))

    data = ''.join(data)

    return data


def data_transfer():
    time.sleep(0.5)
    while True:
        if kill_button.value() and pid.active:
            pid.disable()
        elif kill_button.value() and not pid.active:
            pid.enable()

        data = receive_input()

        if data:
            pid.set_point = float(data)

        time.sleep(0.2)


start_new_thread(data_transfer, ())


def get_ang(pot):
    return 180/(ang_points[1] - ang_points[0])*(pot - ang_points[0])


t_values, outputs = [], []
while True:
    values = [adc.read_u16() for _ in range(300)]
    angle = get_ang(sum(values)/len(values))
    dt, output = pid(angle)
    pwm.duty_u16(int(output))
    # print(output)
