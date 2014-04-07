import sys
from LogicalProcess import *

class IMINT (LogicalProcess):
    
    # instance variable list
    #id - unique id for component
    #controller - the simulation executive
        
    def __init__(self):
        LogicalProcess.__init__(self)
        self.id = 'IMINT'
    
    def __call__(self):
        self.run()
    
    def setController(self, controller):
        self.controller = controller       
            
    def handleMessage(self, msg):
        # determine message type and process accordingly
        pass
    
    def run(self):
        print('IMINT Running')