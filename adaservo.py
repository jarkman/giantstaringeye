import Adafruit_BBIO.PWM as PWM
servo_pin = "P8_13"
#also P8_13, P8_19 f, P9_14 f and P9_16
#P9_21 w    P9_22 w   P9_31  f
duty_min = 3
duty_max = 14.5
duty_span = duty_max - duty_min
PWM.start(servo_pin, (100-duty_min), 60.0,1)
while True:
 angle = raw_input("Angle (0 to 180 x to exit):")
 if angle == 'x':
  PWM.stop(servo_pin)
  PWM.cleanup()
  break
 angle_f = float(angle)
 duty = 100 - ((angle_f / 180) * duty_span + duty_min) 
 PWM.set_duty_cycle(servo_pin, duty)

