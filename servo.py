import Adafruit_BBIO.PWM as PWM
import threading
import time
class Servo:

    def __init__(self, servo_pin, min_angle, max_angle):
 
#pins are  P8_13, P8_19, P9_14 and P9_16
        self.servo_pin = servo_pin
        self.min_angle = min_angle
        self.max_angle = max_angle
        self.duty_min = 3.0
        self.duty_max = 14.5
        self.duty_span = self.duty_max - self.duty_min
        print self.servo_pin
        PWM.start(self.servo_pin, (100.0-self.duty_min), 60.0,1)
        self.angle=95.0
        self.target=90.0
        self.speed=0.0
        self.interval=0.01
        self.acc=20.0 #deg/s/s
        self.max_speed=100.0
        self.lastnow=0
        #time.sleep(1)
        self.setangle(90.0)

    def deinit(self):
          PWM.stop(self.servo_pin)
          PWM.cleanup()
         
    def setangle(self,a):
        #print "set:"
        #print a
        a=float(a)
        #print a
        

        if a > self.max_angle :
            a = self.max_angle
        if a < self.min_angle :
            a = self.min_angle

        # self.angle = a
        # duty = 100.0 - ((self.angle / 180.0) * self.duty_span + self.duty_min) 
        # PWM.set_duty_cycle(self.servo_pin, duty)

        self.target=a
        self.step()

    def inBrakingZone(self):
        distance=abs(self.target-self.angle)
        s=self.speed*self.speed*0.5/self.acc
        return distance < s 

    def step(self):

        distance = abs( self.target - self.angle )

        deltat = self.interval
        #deltat = time.clock() - self.lastnow
        #self.lastnow = time.clock()

        if distance < 1.0 :
            #print "distance < 1"
            return #arrived

        if self.inBrakingZone() :
            self.speed -= self.acc * deltat
            if self.speed < 0.0 :
                #print "Speed -ve"
                self.speed =0.0 
                return
        else:
            if self.speed < self.max_speed:
                self.speed += self.acc * deltat
        
        #print "step"
        if self.target > self.angle :
            self.angle += self.speed * deltat
            if self.angle > self.target :
                self.speed = 0.0
                #print "Past target +ve"
                return
        else:
            self.angle -= self.speed * deltat
            if self.angle < self.target :
                self.speed=0.0
                #print "Past target -ve"
                return
        #print self.speed
        #print self.angle
        #print self.target

        if self.angle > self.max_angle :
            self.angle = self.max_angle
        if self.angle < self.min_angle :
            self.angle = self.min_angle

        duty = 100.0 - ((self.angle / 180.0) * self.duty_span + self.duty_min) 
        #print self.servo_pin
        #print self.angle       
        PWM.set_duty_cycle(self.servo_pin, duty)
        if abs(self.angle-self.target) > 1.0:
            t = threading.Timer(self.interval,self.step)
            t.start()
        
            
