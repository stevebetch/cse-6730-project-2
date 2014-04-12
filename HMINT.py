import sys
from CAOC import *
from Target import *

class HMINT:
    "Human intelligence"
    
    # instance variable list
    #caoc
    #running = false
    
    def __init__(self, numTargets):
        running = 'false'
        self.numTargets = numTargets
        self.count = 0
        # intialization of parameters that control target generation
        
    def setCAOC(self, caoc):
        self.caoc = caoc
        
    def generateNextTarget(self):
            target = Target(None)
            self.caoc.addTarget(target)
            self.count = self.count + 1
    
    # Starts target generation
    def start(self):
        self.running = 'true'
        while self.count < self.numTargets:
            # generate targets and add to CAOC priority queue
            self.generateNextTarget()
        self.stop()
            
    def stop(self):
        self.running = 'false'
        
        