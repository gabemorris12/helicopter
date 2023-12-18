# Press enter with nothing in the prompt to turn the motor off
from machine import Pin, PWM

pwm = PWM(Pin(11))
pwm.freq(1000)
duty = 0

while True:
    try:
        duty = int(input("Duty: "))
    except ValueError:
        duty = 0
    finally:
        pwm.duty_u16(duty)
