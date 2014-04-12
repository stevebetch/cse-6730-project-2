from DroneType1 import *
from DroneSimController import *
from HMINT import *
from IMINT import *
from CAOC import *
from multiprocessing import Process
import Queue
import math, time, sys
import Pyro4
from Pyro4 import *
from Pyro4.core import *
from Pyro4.naming import *
from LPInputQueue import *
from DroneInputQueueContainer import *


PYRO_HOST = '192.168.0.3'
PYRO_PORT = 50987

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
    caocref = CAOC()
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
    for i in range(numDrones):
        dronename = i
        drone = createNewDrone(dronename, typeOfDrone)
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
    
    # Run shared object requests loop
    print 'starting shared objects request loop'
    daemon.requestLoop()

        
#
# Start of Execution
#
if __name__ == '__main__':
    main()