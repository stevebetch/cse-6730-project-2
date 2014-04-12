from LPInputQueue import *

class DroneInputQueueContainer:
    
    def __init__(self):
        self.queues = dict()
    
    def addDroneInputQueue(self, droneId):
        self.queues[droneId] = LPInputQueue()
    
    def addMessage(self, droneId, message):
        q = self.queues.get(droneId)
        q.put(message)
        
    def getNextMessage(self, droneId):
        q = self.queues.get(droneId)
        return q.get()
        
    def size(self):
        return len(self.queues)
    
    def keys(self):
        return self.queues.keys()  
        