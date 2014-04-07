import sys
from Drone import *
from LadderQueue import *

class DroneSimController:
    
    # instance variable list
    #drones = []
    #fel
    #gvt
    #drones
    
    def __initFEL__(self):
        self.fel = LadderQueue   
    
    def __init__(self, caoc, imint):
        self.__initFEL__()
        self.caoc = caoc
        self.imint = imint
        self.drones = []
        
    def __call__(self):
        self.run()
        
    def addDrone(self, drone):
        drone.setController(self)
        self.drones.append(drone)
    
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
        
    def run(self):
        print('Drone Sim Controller running')
        
    
    