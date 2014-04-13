from DroneType1 import *
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

PYRO_HOST = '192.168.0.3'
PYRO_PORT = 12778

# parameters (later get from file)
numDrones = 3
typeOfDrone = "DroneType1"
startTime = 1
endTime = 7*24*60
numTargets = 10

#
# Function definitions
#

def createNewDrone(uid, droneType):
    print('Creating new drone of type ' + droneType)
    droneref = Drone(uid, droneType)
    droneref.setConnectionParams(PYRO_HOST, PYRO_PORT)
    return droneref

def initEnv():
    # initialization of map network
    print('Environment initialized')
    
def initIMINT():
    imintref = IMINT()
    imintref.setConnectionParams(PYRO_HOST, PYRO_PORT)
    print('IMINT initialized')
    return imintref

def initCAOC():
    caocref = CAOC(3,1)
    hmint = HMINT(numTargets)
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
    print 'Starting run'
    
    # Urban network/map
    initEnv()
    
    # Create PYRO remote object daemon
    daemon = Pyro4.Daemon(host=PYRO_HOST, port=PYRO_PORT)
    ns = Pyro4.locateNS()    
    
    # Create CAOC/HMINT, will be separate process started by Controller
    caoc = initCAOC()
    caocInQ = LPInputQueue()
    caocInQ_uri = daemon.register(caocInQ)
    ns.register("inputqueue.caoc", caocInQ_uri)    
    
    # Create IMINT, will be separate process started by Controller
    imint = initIMINT()
    imintInQ = LPInputQueue()
    imintInQ_uri = daemon.register(imintInQ)
    ns.register("inputqueue.imint", imintInQ_uri)    
    
    # Create Simulation Controller
    controller = DroneSimController(caoc, imint)
    controller.setConnectionParams(PYRO_HOST, PYRO_PORT)
    controllerInQ = LPInputQueue()
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
        
    # create target priority queue shared object
    targetPriQ = Queue.Queue()
    targetPriQ_uri = daemon.register(targetPriQ)
    ns.register("priorityqueue.targets", targetPriQ_uri)
    
    # Start Controller process, which starts everything else
    pController = Process(group=None, target=controller, name='Drone Sim Controller Process')
    print 'starting controller'
    pController.start()
    
    # IMINT
    pIMINT = Process(group=None, target=imint, name='IMINT Process')
    pIMINT.start()
    
    # Drones
    pDrones = []
    for i in range(0, len(drones)):
        pDrone = Process(group=None, target=drones[i], name='drone'+str(drones[i].uid)) 
        pDrones.append(pDrone)
        pDrone.start()
    
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