from LPInputQueue import *

class DroneInputQueueContainer:
    
    def __init__(self):
        self.queues = dict()
        
    def __len__(self):
        return len(self.queues)
    
    def addDroneInputQueue(self, droneId):
        self.queues[droneId] = LPInputQueue()
        self.queues[droneId].setLocalTime(0)
        
    def setLPIDs(self, drones):
        for drone in drones:
            self.queues[drone.uid].setLPID(drone.LPID)
            
    def getLPIDs(self):
        lpids = []
        for droneid in self.queues:
            q = self.queues[droneid]
            print 'LPID for drone %d = %d' % (droneid, q.LPID)
            lpids.append(q.LPID)
        return lpids
    
    def getLPID(self, droneid):
        return self.queues[droneid].LPID
    
    def getInputQueue(self, droneid):
            return self.queues[droneid]    
        
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
        