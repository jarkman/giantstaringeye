'''
Created on 27 Oct 2013

@author: anton
'''

from servo import Servo

class Eye:
    '''
    classdocs
    '''

    def __init__(self):
        '''
        Constructor
        '''
        self.azimuth_servo = Servo("P8_13", 0.0, 180.0)
        self.altitude_servo = Servo("P9_21",30.0,128.0)
        self.pupil_servo = Servo("P9_16",0.0,130.0)
 
    
    def setAzimuth(self, angle):
        self.azimuth_servo.setangle(angle)
        
    def setAltitude(self, angle):
        self.altitude_servo.setangle(angle)
    
    def setPupil(self, size):
        '''
        Set pupil size, as a percentage of maximum
        '''
        # largest angle => most interested pupil
        self.pupil_servo.setangle(self.pupil_servo.min_angle + size * (self.pupil_servo.max_angle - self.pupil_servo.min_angle) / 100.0)  
        
