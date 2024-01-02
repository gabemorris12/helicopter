import sys
import time
from _thread import start_new_thread

import select
from machine import ADC, Pin, PWM

from pid import PID

Kp = 3000
Ki = 3000
Kd = 500

above_90 = (1500, 1500, 600)

ang_points = (10108, 54580)  # angle at 0 degrees and 180 degrees

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
            if float(data) > 90:
                pid.tunings = above_90
            else:
                pid.tunings = (Kp, Ki, Kd)
            pid.set_point = float(data)

        # print(f'Time({t_values})')
        # print()
        # print(f'Angle({outputs})', '\n')
        # t_values.clear()
        # outputs.clear()

        time.sleep(0.1)


start_new_thread(data_transfer, ())


def get_ang(pot):
    return 180/(ang_points[1] - ang_points[0])*(pot - ang_points[0])


while True:
    values = [adc.read_u16() for _ in range(300)]
    angle = get_ang(sum(values)/len(values))
    dt, output = pid(angle)
    print((dt, angle))
    pwm.duty_u16(int(output))
