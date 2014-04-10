import sys
from Drone import *
from GlobalControlProcess import *
from multiprocessing import Process


class DroneSimController(GlobalControlProcess):
    
    # instance variable list
    #caoc - CAOC object, will be run in a new Process
    #imint - IMINT object, will be run in a new Process
    #drones - Drone objects, each will be run in a new Process
    #gvt - Global Virtual Time

    
    def __init__(self, caoc, imint):
        self.caoc = caoc
        self.imint = imint
        self.drones = []
        self.gvt = 0
        
    def __call__(self):
        self.run()
        
    def addDrone(self, drone):
        self.drones.append(drone)
            
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
        
        # connect with Queue manager        
        manager = self.QueueServerClient(self.REMOTE_HOST, self.PORT, self.AUTHKEY)
        
        # Get the message queue objects from the client
        inputQueues = manager.get_queues()
        print len(inputQueues.keys())
        inputQueue = inputQueues.get('controller')
        #imintInQ = inputQueues.get('imint')
        caocInQ = inputQueues.get('caoc')
        droneInQs = inputQueues.get('drones')
        
        imintInQ = manager.get_imint_input_queue()
        imintInQ.put('Controller Message')              
        
        # IMINT
        pIMINT = Process(group=None, target=self.imint, name='IMINT Process')
        pIMINT.start()
        
        # Drones
        pDrones = []
        for i in range(0, len(self.drones)):
            pDrone = Process(group=None, target=self.drones[i], name=self.drones[i].id) 
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
            