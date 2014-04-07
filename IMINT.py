import sys
from LogicalProcess import *

class IMINT (LogicalProcess):
    
    # instance variable list
    #controller
        
    def __init__(self):
        pass
    
    def __call__(self):
        self.run()
    
    def setController(self, controller):
        self.controller = controller       
            
    def handleMessage(self, msg):
        # determine message type and process accordingly
        pass
    
    def run(self):
        print('IMINT Running')