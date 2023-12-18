from machine import ADC, Pin, PWM
from pid import PID

Kp = 500
Ki = 200
Kd = 0


def get_ang(pot):
    return 180/(ang_points[1] - ang_points[0])*(pot - ang_points[0])


ang_points = (8200, 52882)  # angle at 0 degrees and 180 degrees
adc = ADC(26)

pwm = PWM(Pin(11))
pwm.freq(1000)

pid = PID(Kp, Ki, Kd, set_point=90, output_limits=(0, 65535))

while True:
    values = [adc.read_u16() for _ in range(10)]
    angle = get_ang(sum(values)/len(values))
    output = pid(angle)
    pwm.duty_u16(int(output))
    # print(output)
