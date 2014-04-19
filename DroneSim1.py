#from DroneType1 import *
from Drone import *
from DroneSimController import *
from HMINT import *
from IMINT import *
from CAOC import *
from multiprocessing import Process
import math, time, sys
import Pyro4
from LPInputQueue import *
from DroneInputQueueContainer import *

PYRO_HOST = '192.168.1.10'
PYRO_PORT = 12778

# parameters (later get from file)
numDrones = 3
typeOfDrone = "DroneType1"
numTargets = 10
seedNum = 1
mapSize = 100 # notional so that we can call HMINT initialization, eventually we can get this from initEnv()
#mapsize really means number of map nodes.
mapX=300
mapY=300
numStreets=50

heuristic = 1

#
# Function definitions
#

def createNewDrone(uid, droneType):
    print('Creating new drone of type ' + droneType)
    droneref = Drone(uid, droneType)
    droneref.setConnectionParams(PYRO_HOST, PYRO_PORT)
    return droneref

    
def initIMINT():
    imintref = IMINT(heuristic)
    imintref.setConnectionParams(PYRO_HOST, PYRO_PORT)
    print('IMINT initialized')
    return imintref

def initCAOC():
    caocref = CAOC(numDrones,heuristic)
    hmint = HMINT(numTargets, seedNum, mapSize)
    caocref.setHMINT(hmint)
    hmint.setCAOC(caocref)
    caocref.setConnectionParams(PYRO_HOST, PYRO_PORT)
    print('HMINT/CAOC initialized')
    return caocref
    
#
# Main method
#

def main():
        
    #
    # initialization
    #
    print "Starting run"
    
    # Urban network/map
    Map = GenMap(mapX,mapY)
    Map.map(numStreets)
    
    # Create PYRO remote object daemon
    daemon = Pyro4.Daemon(host=PYRO_HOST, port=PYRO_PORT)
    ns = Pyro4.locateNS()    
    
    # Create CAOC/HMINT, will be separate process started by Controller
    caoc = initCAOC()
    caocInQ = LPInputQueue()
    caocInQ.setLocalTime(0)   
    caocInQ_uri = daemon.register(caocInQ)
    ns.register("inputqueue.caoc", caocInQ_uri)    
    
    # Create IMINT, will be separate process started by Controller
    imint = initIMINT()
    imintInQ = LPInputQueue()
    imintInQ.setLocalTime(0)
    imintInQ_uri = daemon.register(imintInQ)
    ns.register("inputqueue.imint", imintInQ_uri)    
    
    # Create Simulation Controller
    controller = DroneSimController(caoc, imint)
    controller.setConnectionParams(PYRO_HOST, PYRO_PORT)
    controllerInQ = LPInputQueue()
    controllerInQ.setLocalTime(0)
    controllerInQ_uri = daemon.register(controllerInQ)
    ns.register("inputqueue.controller", controllerInQ_uri)
    
    # Create drone entities, each will be separate process started by Controller
    droneInQs = DroneInputQueueContainer()
    drones = []
    for i in range(numDrones):
        dronename = i
        drone = createNewDrone(dronename, typeOfDrone)
        drones.append(drone)
        controller.addDrone(drone)
        droneInQs.addDroneInputQueue(dronename)
    droneInQs_uri = daemon.register(droneInQs)
    ns.register("inputqueue.drones", droneInQs_uri)    

    
    # Start Controller process, which starts everything else
    pController = Process(group=None, target=controller, name='Drone Sim Controller Process')
    print 'starting controller'
    pController.start()
    
    # Drones
    pDrones = []
    for i in range(0, len(drones)):
        pDrone = Process(group=None, target=drones[i], name='drone'+str(drones[i].uid), args=(Map.MapEntryPt,)) 
        pDrones.append(pDrone)
        pDrone.start()    
    
    # IMINT
    pIMINT = Process(group=None, target=imint, name='IMINT Process')
    pIMINT.start()
    
    # HMINT/CAOC
    pCAOC = Process(group=None, target=caoc, name='HMINT/CAOC Process')
    pCAOC.start()        
    
    # Run shared object requests loop
    print 'starting shared objects request loop'
    daemon.requestLoop()
        
#
# Start of Execution
#
if __name__ == '__main__':
    main()
