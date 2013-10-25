import Servo
import time




# working pins are  P8_13, P9_16, P9_21 P9_22
# Non-working pins are P9_14 and P8_19
azimuth_servo = Servo.Servo("P8_13", 0.0, 180.0)

alt_servo = Servo.Servo("P9_21",30.0,128.0) #should be P8_19  90 is horizintal, 30 is down, 128 is up

pupil_servo = Servo.Servo("P9_16",0.0,130.0) #should be P9_14  130 is small pupil, 0 is big pupil

azimuth_servo.setangle(90.0)
alt_servo.setangle(90.0)
pupil_servo.setangle(90.0)

while True:

     
    anglea = raw_input("Angle (0 to 180 x to exit):")
    if anglea == 'x':
        azimuth_servo.deinit()
        alt_servo.deinit()
        pupil_servo.deinit()
        break
    anglef=float(anglea)
    azimuth_servo.setangle(anglef) 

