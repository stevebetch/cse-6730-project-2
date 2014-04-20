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
import socket
import threading



#
# Function definitions
#
PYRO_HOST = ''
PYRO_PORT = 12778


def createNewDrone(uid, droneType,heuristic):
    print('Creating new drone of type ' + droneType)
    droneref = Drone(uid, droneType,heuristic)
    droneref.setConnectionParams(PYRO_HOST, PYRO_PORT)
    return droneref
    
def initIMINT(heuristic):
    imintref = IMINT(heuristic)
    imintref.setConnectionParams(PYRO_HOST, PYRO_PORT)
    print('IMINT initialized')
    return imintref

def initCAOC(randNodes,Data):
    caocref = CAOC(Data.numDrones,Data.heuristic)
    hmint = HMINT(Data.numTargets, Data.seedNum, randNodes)
    caocref.setHMINT(hmint)
    hmint.setCAOC(caocref)
    caocref.setConnectionParams(PYRO_HOST, PYRO_PORT)
    print('HMINT/CAOC initialized')
    return caocref

def get_local_ip_address():
    ipaddr = ''
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('1.1.1.1', 8000))
        ipaddr = s.getsockname()[0]
        s.close()
    
    except:
        pass
    return ipaddr

#
# Main method
#

def main(Data):

    
    #
    # initialization
    #
    print 'Starting run'
    
    #print "Using Nuisance mean of:", Nuisance
    
    PYRO_HOST=get_local_ip_address()
    print "Using IP address:", PYRO_HOST
    
    # Urban network/map
    Map = GenMap(Data.mapX,Data.mapY)
    Map.map(Data.numStreets,Data.Nuisance)
    randNodes=[]
    for i in range(Data.numTargets):
        randNodes.append(Map.RandNode())
    
    # Create PYRO remote object daemon
    daemon = Pyro4.Daemon(host=PYRO_HOST, port=PYRO_PORT)
    ns = Pyro4.locateNS()    
    
    # Create CAOC/HMINT, will be separate process started by Controller
    caoc = initCAOC(randNodes,Data)
    caocInQ = LPInputQueue()
    caocInQ.setLocalTime(0)
    caocInQ.setLPID(caoc.LPID)
    caocInQ_uri = daemon.register(caocInQ)
    ns.register("inputqueue.caoc", caocInQ_uri)    
    
    # Create IMINT, will be separate process started by Controller
    imint = initIMINT(Data.heuristic)
    imintInQ = LPInputQueue()
    imintInQ.setLocalTime(0)
    imintInQ.setLPID(imint.LPID)
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
    for i in range(Data.numDrones):
        dronename = i
        drone = createNewDrone(dronename, Data.typeOfDrone,Data.heuristic)
        drones.append(drone)
        controller.addDrone(drone)
        droneInQs.addDroneInputQueue(dronename)
    droneInQs.setLPIDs(drones)
    droneInQs_uri = daemon.register(droneInQs)
    ns.register("inputqueue.drones", droneInQs_uri)    

    #creating semaphore
#a=threading.Semaphore(numDrones)



    # Start Controller process, which starts everything else
    pController = Process(group=None, target=controller, name='Drone Sim Controller Process')
    print 'starting controller'
    pController.start()
    
    # Drones
    pDrones = []
    for i in range(0, len(drones)):
        # a.acquire()
        pDrone = Process(group=None, target=drones[i], name='drone'+str(drones[i].uid), args=(Map.MapEntryPt,)) 
        pDrones.append(pDrone)
        #a.release()
        pDrone.start()    
    
    
    # HMINT/CAOC
    pCAOC = Process(group=None, target=caoc, name='HMINT/CAOC Process')
    pCAOC.start()        

    # IMINT
    pIMINT = Process(group=None, target=imint, name='IMINT Process')
    pIMINT.start()
    
    # Run shared object requests loop
    print 'starting shared objects request loop'
    daemon.requestLoop()
        
#
# Start of Execution
#
#if __name__ == '__main__':
 #   main()
