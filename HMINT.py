import sys
from CAOC import *

class HMINT
"Human intelligence"

caoc
running = false

def __init__(self, caoc):
    self.caoc = caoc
    # intialization of parameters that control target generation

# Starts target generation
def start(self):
    self.running = true
    while self.running:
        # generate targets and add to CAOC priority queue
        generateNextTarget()
        
def stop(self):
    self.running = false
    
def generateNextTarget(self):
    target = Target(param1, param2)
    caoc.addTarget(target)
    
    