from machine import ADC, Pin
import time


def get_ang(pot):
    return 180/(ang_points[1] - ang_points[0])*(pot - ang_points[0])


ang_points = (8200, 52990)  # angle at 0 degrees and 180 degrees

adc = ADC(26)
led = Pin(25, Pin.OUT)

while True:
    values = [adc.read_u16() for _ in range(10_000)]
    # print(sum(values)/len(values))
    print(get_ang(sum(values)/len(values)))
    # noinspection PyUnresolvedReferences
    led.toggle()
    time.sleep(2)
