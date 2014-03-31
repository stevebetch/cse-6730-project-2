import sys
from LogicalProcess import *

class Drone (LogicalProcess):
    
    controller
    
    def __init__(self):
        pass
    
    def setController(self, controller):
        self.controller = controller
            
    def handleMessage(self, msg):
        # determine message type and process accordingly
        pass
    
    def start(self):
        # Begin process of selecting target from CAOC priority queue, tracking, check when refueling needed, etc.