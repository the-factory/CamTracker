import cv2
import numpy as np

class Tracker:
    def __init__(self):
        self.PRE_THRESH_VAL = 15
        self.POST_THRESH_VAL = 9
        self.CANNY_MIN = 1
        self.CANNY_MAX = 25
        self.background = None
        self.capture = cv2.VideoCapture(0)
        self.window_name = "Main"
        self.window = cv2.namedWindow(self.window_name)
        cv2.createTrackbar("Canny-Max", self.window_name, self.CANNY_MAX, 100, self.cannyMax())
        cv2.createTrackbar("Pre-Threshold", self.window_name, self.PRE_THRESH_VAL, 51, self.setPreThreshVal())
        cv2.createTrackbar("Post-Threshold", self.window_name, self.POST_THRESH_VAL, 51, self.setPostThreshVal())
    
    def setPreThreshVal(self):
        def f(val):
            if (val%2 == 0): self.PRE_THRESH_VAL = val+1
            else: self.PRE_THRESH_VAL = val
        return f
    def setPostThreshVal(self):
        def f(val):
            if (val%2 == 0): self.POST_THRESH_VAL = val+1
            else: self.POST_THRESH_VAL = val
        return f
    def cannyMax(self):
        def f(val):
            self.CANNY_MAX = val
        return f

    def captureFrame(self):
        success, frame = self.capture.read()
        return frame
    def smoothedEdges(self, frame):
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
        frame = cv2.GaussianBlur(frame, (self.PRE_THRESH_VAL,self.PRE_THRESH_VAL), 0)
        frame = cv2.Canny(frame, self.CANNY_MIN, self.CANNY_MAX)    
        frame = cv2.GaussianBlur(frame, (self.POST_THRESH_VAL,self.POST_THRESH_VAL), 0)
        return frame
    def backgroundSubtract(self, frame):
        frame = cv2.subtract(frame, self.background)
        return frame
    def dilateEdges(self, frame):
        x = cv2.dilate(frame, cv2.getStructuringElement(cv2.MORPH_CROSS,(6,6)))
        return x
    def setBackground(self):
        total = None
        for i in xrange(10):
            frame = self.captureFrame()
            edges = self.smoothedEdges(frame)
            if total is None: total = edges
            else: total = cv2.add(total, edges)
        self.background = total
    def contours(self, frame):
        c, h = cv2.findContours(frame, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
        return c
    def mainloop(self):
        while True:
            original_frame = self.captureFrame()
            edges = self.smoothedEdges(original_frame)
            foreground = None
            if self.background is not None:
                foreground = self.backgroundSubtract(edges)
            else: foreground = edges
            dilated = self.dilateEdges(foreground)
            contours = self.contours(np.copy(dilated))
            cv2.drawContours(original_frame, [contours[0]], 0, (255,0,255),-1)
            cv2.imshow(self.window_name, dilated)
            key = cv2.waitKey(1)
            if key == 113: break
            elif key == 98: self.setBackground()
        cv2.destroyAllWindows()
