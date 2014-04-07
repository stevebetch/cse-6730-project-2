import sys
from Drone import *
from LadderQueue import *
from multiprocessing import Process

class DroneSimController:
    
    # instance variable list
    #drones = []
    #fel
    #gvt
    #drones
    #caoc
    #imint
    
    def __initFEL__(self):
        self.fel = LadderQueue()
    
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
        
        # Self
        print('Drone Sim Controller running')
        
        # IMINT
        pIMINT = Process(group=None, target=self.imint, name='IMINT Process')
        pIMINT.start()
        
        # Drones
        pDrones = []
        for i in range(0, len(self.drones)):
            dronename = 'Drone %d process' % (i)
            pDrone = Process(group=None, target=self.drones[i], name=dronename) 
            pDrones.append(pDrone)
            pDrone.start()
        
        # HMINT/CAOC
        pCAOC = Process(group=None, target=self.caoc, name='HMINT/CAOC Process')
        pCAOC.start()        
        
        # Verify all processes running
        while (not pIMINT.is_alive()):
            time.sleep(100)
        print('Detected IMINT alive')
        while (not pCAOC.is_alive()):
            time.sleep(100) 
        print('Detected CAOC/HMINT alive')
        for i in range(0, len(self.drones)):
            dronename = 'Drone %d process' % (i)
            pDrone = pDrones[i]
            while (not pDrone.is_alive()):
                time.sleep(100)
            print('Detected drone alive')
    
    