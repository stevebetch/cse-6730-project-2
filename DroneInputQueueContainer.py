from LPInputQueue import *

class DroneInputQueueContainer:
    
    def __init__(self):
        self.queues = dict()
        
    # gets the number of input queues (number of drones)
    def __len__(self):
        return len(self.queues)
    
    # adds a queue to the container, associated with the given droneid
    def addDroneInputQueue(self, droneId):
        self.queues[droneId] = LPInputQueue()
        self.queues[droneId].setLocalTime(0)
        
    # sets the LPID variable in the member input queues to that of the drone
    # with which it is associated
    def setLPIDs(self, drones):
        for drone in drones:
            self.queues[drone.uid].setLPID(drone.LPID)
            
    # Gets list containing LPIDs of all contained input queues
    def getLPIDs(self):
        lpids = []
        for droneid in self.queues:
            q = self.queues[droneid]
            lpids.append(q.LPID)
        return lpids
    
    # Sets the localTime variable in the input queue associated with the given droneid
    def setLocalTime(self, droneid, time):
        self.queues[droneid].setLocalTime(time)

    # Gets the LPID value for the input queue associated with the given droneid
    def getLPID(self, droneid):
        return self.queues[droneid].LPID
    
    # Gets the number of white messages present in the input queue associated with the given droneid
    def numWhiteMessages(self, droneid):
        return self.queues[droneid].numWhiteMessages()
    
    # Gets the droneid associated with the given LPID
    def getDroneIDForLPID(self, lpid):
        for droneid, q in self.queues.items():
            if q.getLPID() == lpid:
                return droneid
        return None
    
    # Gets the input queue for the drone with the given droneid
    def getInputQueue(self, droneid):
        return self.queues.get(droneid) 
    
    # Sets the input queue for the drone with the given droneid
    def setInputQueue(self, droneid, queue):
        self.queues[droneid] = queue
        
    # tells whether the input queue associated with the given droneid has any messages in it
    def hasMessages(self, uid):
        return self.queues[uid].hasMessages()
    
    # Adds the given message to the input queue for the drone with the given droneid
    def addMessage(self, droneId, message):
        q = self.queues.get(droneId)
        q.addMessage(message) 
        
    # tells the number of input queues in the container
    def size(self):
        return len(self.queues)
    
    # Gets list of droneids for all input queues in the container
    def keys(self):
        return self.queues.keys()  
        