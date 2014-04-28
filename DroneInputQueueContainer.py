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
            lpids.append(q.LPID)
        return lpids
    
    def setLocalTime(self, droneid, time):
        self.queues[droneid].setLocalTime(time)
    
    def getLPID(self, droneid):
        return self.queues[droneid].LPID
    
    def numWhiteMessages(self, droneid):
        return self.queues[droneid].numWhiteMessages()
    
    def getDroneIDForLPID(self, lpid):
        for droneid, q in self.queues.items():
            if q.getLPID() == lpid:
                return droneid
        return None
    
    def getInputQueue(self, droneid):
        return self.queues.get(droneid) 
    
    def setInputQueue(self, droneid, queue):
        self.queues[droneid] = queue
        
    def hasMessages(self, uid):
        return self.queues[uid].hasMessages()
    
    def addMessage(self, droneId, message):
        q = self.queues.get(droneId)
        q.addMessage(message) 
        
    def size(self):
        return len(self.queues)
    
    def keys(self):
        return self.queues.keys()  
        