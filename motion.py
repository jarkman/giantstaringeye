#!/usr/bin/env python

# Derived from http://sundararajana.blogspot.com/2007/05/motion-detection-using-opencv.html

# TODO: tweak average weighting, threshold, erode and dilate parameters
# TODO: mask off camera donut
# TODO: compute altitude
# TODO: compute interest (pupil dilation)

import cv2.cv as cv
import math
import time
from eye import Eye

class Target:
    
    IMAGE_WIDTH = 352
    IMAGE_HEIGHT = 288
    
    INITIAL_STARE_COUNT = 5 # how many frames without proximate movement before we start tracking a new blob
    TRACKING_PROXIMITY = 20.0 # blobs further away than this are considered not part of the tracked object
    
    def __init__(self):
        self.capture = cv.CaptureFromCAM(0)
        cv.SetCaptureProperty(self.capture, cv.CV_CAP_PROP_FRAME_WIDTH, self.IMAGE_WIDTH)
        cv.SetCaptureProperty(self.capture, cv.CV_CAP_PROP_FRAME_HEIGHT, self.IMAGE_HEIGHT)
        # cv.NamedWindow("Target", 1)
        # cv.NamedWindow("Intermediate", 1)
        self.theGiantEye = Eye()
        self.interest = 0.0 # how interested we are, 0 - 100

    def drawRect(self, image, rect):
        pt1 = (rect[0], rect[1])
        pt2 = (rect[0] + rect[2], rect[1] + rect[3])                
        cv.Rectangle(image, pt1, pt2, cv.CV_RGB(255,0,0), 1)

    def bullsEye(self, image, point):        
        cv.Circle(image, point, 40, cv.CV_RGB(255, 255, 255), 1)
        cv.Circle(image, point, 30, cv.CV_RGB(255, 100, 0), 1)
        cv.Circle(image, point, 20, cv.CV_RGB(255, 255, 255), 1)
        cv.Circle(image, point, 10, cv.CV_RGB(255, 100, 0), 5)
        
    def calcAzimuth(self, point):
        xoffs = point[0] - self.image_centre[0]
        yoffs = point[1] - self.image_centre[1]       
        return 180.0 - 180.0 * math.atan2(yoffs, xoffs) / math.pi

    def calcAltitude(self, point):
        # outside of image donut is horizontal-ish (-20 degrees)
        # inside of image dount is steeply down (-70)
        # for servo, 30 is steep down, 90 is horizontal
        d = self.distance(self.image_centre, point)
        inner_radius = 45.0
        outer_radius = 120.0
        angle_min = 60.0 # steep down
        angle_max = 90.0 # nearly horizontal

        if d < inner_radius:
            return angle_min
        elif d > outer_radius:
            return angle_max
        else:
            return (d - inner_radius) / (outer_radius - inner_radius) * (angle_max - angle_min) + angle_min

    def area(self, rect):
        return rect[2] * rect[3]
    
    def centre(self, rect):
        return (rect[0] + rect[2] / 2, rect[1] + rect[3] / 2)

    def distance(self, p1, p2):
        return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

    def chooseTrackingPoint(self, rectangles, last):
        
        if len(rectangles) == 0:
            return None
        
        # given non-empty list of rectangles
        # ideas: choose the rectangle closest to the last one; if no last one, choose the biggest
        # if all rectangles are too far away, return None
        # return the centre point of the chosen rectangle
        
        def proximity(rect):
            c = self.centre(rect)           
            return self.distance(c, last)
        
        if last:
            choice = sorted(rectangles, key=proximity)[0] # we want the nearest
            
           
            if proximity(choice) > 50.0: # but forget it if too far away
                # print "ignoring blob at distance ", proximity(choice)
                choice = None
            # else:
                # print "tracking blob ", choice, "at distance ", proximity(choice) 
        else:
            choice = sorted(rectangles, key=self.area)[0] # we want the biggest
            # print "biggest blob  is ", choice
        
        return self.centre(choice) if choice else None

    def applyMask(self, image):
	cv.Circle(image, self.image_centre, 45, cv.CV_RGB(127, 127, 127), -1)
	cv.Circle(image, self.image_centre, 150, cv.CV_RGB(127, 127, 127), 100)

    def incInterest(self):
        if self.interest < 100.0:
            self.interest += 5.0

    def decInterest(self):
        if self.interest > 0.0:
            self.interest -= 5.0

    def loseInterest(self):
        self.interest = 0.0
                
    
    def calibrate(self):
        # Set the servos to known positions so we can assemble the hardware
        # Set alt to level
        self.theGiantEye.setAltitude(90)
        #Set azimuth to straigh ahead
        self.theGiantEye.setAzimuth(90)
        # set the pupil to min interest, all the way out
        self.theGiantEye.setPupil(0)

    def run(self):
        # Capture first frame to get size
        frame = cv.QueryFrame(self.capture)
        frame_size = cv.GetSize(frame)
        self.image_centre = (frame_size[0] / 2, frame_size[1] / 2)
        self.applyMask(frame)
                
        difference = cv.CloneImage(frame)
        temp = cv.CloneImage(frame)
        
        grey_image = cv.CreateImage(frame_size, cv.IPL_DEPTH_8U, 1)
        
        moving_average = cv.CreateImage(frame_size, cv.IPL_DEPTH_32F, 3)      
        cv.ConvertScale(frame, moving_average, 1.0, 0.0)

        print 'Size: ', frame_size
        
        stare_count = self.INITIAL_STARE_COUNT
        tracking_point = None
        
        while True:
            # Capture frame from webcam
            color_image = cv.QueryFrame(self.capture)
            self.applyMask(frame)
            
            # Smooth to get rid of false positives
            # cv.Smooth(color_image, color_image, cv.CV_GAUSSIAN, 3, 0)
            
            # third parameter is weight, originally 0.020
            cv.RunningAvg(color_image, moving_average, 0.1, None)
            
            # Convert the scale of the moving average.
            cv.ConvertScale(moving_average, temp, 1.0, 0.0)
            
            # Minus the current frame from the moving average.
            cv.AbsDiff(color_image, temp, difference)
            
            # Convert the image to grayscale.
            cv.CvtColor(difference, grey_image, cv.CV_RGB2GRAY)
            
            # Convert the image to black and white. Threshold was  originally 70
            cv.Threshold(grey_image, grey_image, 30, 255, cv.CV_THRESH_BINARY)
            
            # cv.ShowImage("Intermediate", grey_image)

            # Dilate and erode to get object blobs
            cv.Dilate(grey_image, grey_image, None, 18)
            cv.Erode(grey_image, grey_image, None, 10)
            
            # Calculate movements
            storage = cv.CreateMemStorage(0)
            contour = cv.FindContours(grey_image, storage, cv.CV_RETR_CCOMP, cv.CV_CHAIN_APPROX_SIMPLE)
                       
            # contour is a CVSeq object: http://docs.opencv.org/modules/core/doc/dynamic_structures.html#cvseq
            # it represents a sequence of contours; each contour is a vector of points
            # cvseq object is itself an iterable over the first vector in the sequence
            
            rectangles = []
            
            while contour:
                # Draw rectangles
                bound_rect = cv.BoundingRect(list(contour))
                # bound_rect is (x, y, width, height)
                # print "Rectangle: ", bound_rect
                
                # move to next contour in the sequence
                contour = contour.h_next()
                
                self.drawRect(color_image, bound_rect)
                rectangles.append(bound_rect)
            
            candidate = self.chooseTrackingPoint(rectangles, tracking_point)                 
                            
            if candidate:
                tracking_point = candidate
                stare_count = self.INITIAL_STARE_COUNT
                self.incInterest()
            else:
                # idea: count down a few frames before forgetting the tracking point
                if stare_count:
                    stare_count -= 1
                    self.decInterest()
                else:
                    tracking_point = None
                    self.loseInterest()

            if tracking_point:
                # draw bull's eye
                self.bullsEye(color_image, tracking_point)              

                azimuth = self.calcAzimuth(tracking_point)
                print "Azimuth: ", azimuth
                self.theGiantEye.setAzimuth(azimuth)  

                altitude = self.calcAltitude(tracking_point)
                print "Altitude: ", altitude
                self.theGiantEye.setAltitude(altitude)

            # always display the interest level
            print "Interest: ", self.interest
            self.theGiantEye.setPupil(self.interest)

            # if lost interest, stare into the distance
            if self.interest < 5.0:
                self.theGiantEye.setAltitude(90.0)

            # Display frame to user
            # cv.ShowImage("Target", color_image)
            
            time.sleep(0.001)

            # Listen for ESC or ENTER key
            c = cv.WaitKey(7) % 0x100
            if c == 27 or c == 10:
                break

if __name__=="__main__":
    t = Target()
    #t.calibrate()
    t.run()
