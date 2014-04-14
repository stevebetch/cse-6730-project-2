from LPInputQueue import *

class DroneInputQueueContainer:
    
    def __init__(self):
        self.queues = dict()
    
    def addDroneInputQueue(self, droneId):
        self.queues[droneId] = LPInputQueue()
        self.queues[droneId].setLocalTime(0)
        
    def hasMessages(self, uid):
        return self.queues[uid].hasMessages()
    
    def addMessage(self, droneId, message):
        q = self.queues.get(droneId)
        q.addMessage(message)
        
    def getNextMessage(self, droneId):
        q = self.queues.get(droneId)        
        msg = None
        
        if q.hasMessages():

            # peek at first message
            firstMsg = q.getNextMessage()
            if (not firstMsg.isAntiMessage()):
                return firstMsg
            else:
                q.justPut(firstMsg)
            
                # loop until non-antiMessage is found
                while True:
                    currMsg = q.getNextMessage()
                    if currMsg == firstMsg:
                        q.justPut(currMsg)
                        break
                    if (currMsg.isAntiMessage()):
                        # put it back and get another one
                        q.justPut(currMsg)
                    else:
                        msg = currMsg
                        break
        return msg 
        
    def size(self):
        return len(self.queues)
    
    def keys(self):
        return self.queues.keys()  
        