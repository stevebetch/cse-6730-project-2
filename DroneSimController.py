import sys

class DroneSimController:
    
    drones = []
    fel = LadderQueue()
    gvt
    
    def __init__(self, caoc, imint):
        initFEL()
        self.caoc = caoc
        self.drones = drones
        self.imint = imint
        caoc.setController(self)
        imint.setController(self)
        
    def addDrone(self, drone):
        drone.setController(self)
        drones.append(drone)
        
    def initFEL():
        pass
    
    # Schedule new event
    def scheduleEvent(event):
        fel.addEvent(event)
            
    def advanceTime(time):
        pass
    
    def updateGVT():
        minTimesList = []
        minTimesList.append(caoc.requestGVT())
        minTimesList.append(imint.requestGVT())
        for drone in drones:
            minTimesList.append(drone.requestGVT())
        gvt = min(minTimesList)
        
    
    