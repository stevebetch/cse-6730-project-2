import sys
from LogicalProcess import *

class IMINT (LogicalProcess):
    
    controller
        
    def __init__(self):
        pass
    
    def setController(self, controller):
        self.controller = controller       
            
    def handleMessage(self, msg):
        # determine message type and process accordingly
        pass    