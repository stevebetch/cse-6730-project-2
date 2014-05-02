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

ll = threading.Lock()

#
# Function definitions
#
PYRO_HOST = ''
PYRO_PORT = 12778


def createNewDrone(uid, droneType,heuristic,Legs):
#Input: Drone id, type, heuristic, and fuel flight time. 
# Output: a drone object
#Description: This function initalizes a drone for the simulation.

    print('Creating new drone of type ' + droneType)
    droneref = Drone(uid, droneType,heuristic,Legs)
    droneref.setConnectionParams(PYRO_HOST, PYRO_PORT)
    return droneref
    
def initIMINT(heuristic,numTargets):
#Input: heuristic, and number of targets Output: Imint object
#Description: This function initalizes the imint object.

    imintref = IMINT(heuristic,numTargets)
    imintref.setConnectionParams(PYRO_HOST, PYRO_PORT)
    print('IMINT initialized')
    return imintref

def initHMINT(randNodes,Data):
#Input: A random node on the map, and the simulation data class Output: HMINT object
#Description: This function initalizes the HMINT object.


    hmintref = HMINT(Data.numTargets, randNodes,Data.tarType)
    hmintref.setConnectionParams(PYRO_HOST, PYRO_PORT)
    print('HMINT initialized')
    return hmintref

def initCAOC(Data,MapEntryPt):
#Input: the simulation data class and the map entry point Output: CAOC object
#Description: This function initalizes the CAOC object


    caocref = CAOC(Data.numDrones,Data.heuristic,MapEntryPt.xpos,MapEntryPt.ypos)
    caocref.setConnectionParams(PYRO_HOST, PYRO_PORT)
    print('CAOC initialized')
    return caocref

def Loop():
#Input: none Output: loop controlelr object
#Description: This function initalizes the loop control object.


    loopref = Loops()
    loopref.setConnectionParams(PYRO_HOST, PYRO_PORT)
    print('Loopref initialized')
    return loopref

def get_local_ip_address():
#Input: none Output: local ip address
#Description: This function gets your computer's IP address. Needed for PYRO.


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

def main(Data,daemon,ns):
    LogicalProcess.nextLPID = 0
    
    #
    # initialization
    #
    print 'Starting run'
    
    random.seed(Data.seedNum)

    # Urban network/map
    Map = GenMap(Data.mapX,Data.mapY)
    Map.map(Data.numStreets,Data.Nuisance)
    randNodes=[]
    for i in range(Data.numTargets):
        randNodes.append(Map.RandNode())


    # Create HMINT, will be separate process started by Controller
    hmint = initHMINT(randNodes,Data)
    hmintInQ = LPInputQueue()
    hmintInQ.setLocalTime(0)
    hmintInQ.setLPID(hmint.LPID)
    hmintInQ_uri = daemon.register(hmintInQ)
    hmintInQ_uri = daemon.uriFor(hmintInQ)
    
    ns.register("inputqueue.hmint", hmintInQ_uri)        
    
    # Create CAOC, will be separate process started by Controller
    caoc = initCAOC(Data,Map.MapEntryPt)
    caocInQ = LPInputQueue()
    caocInQ.setLocalTime(0)
    caocInQ.setLPID(caoc.LPID)
    caocInQ_uri = daemon.register(caocInQ)
    caocInQ_uri = daemon.uriFor(caocInQ)
    ns.register("inputqueue.caoc", caocInQ_uri)    
    
    # Create IMINT, will be separate process started by Controller
    imint = initIMINT(Data.heuristic,Data.numTargets)
    imintInQ = LPInputQueue()
    imintInQ.setLocalTime(0)
    imintInQ.setLPID(imint.LPID)
    imintInQ_uri = daemon.register(imintInQ)
    imintInQ_uri = daemon.uriFor(imintInQ)
    ns.register("inputqueue.imint", imintInQ_uri)    
    
    # Create Simulation Controller
    controller = DroneSimController(hmint, caoc, imint)
    controller.setConnectionParams(PYRO_HOST, PYRO_PORT)
    controllerInQ = LPInputQueue()
    controllerInQ.setLocalTime(0)
    controllerInQ_uri = daemon.register(controllerInQ)
    controllerInQ_uri = daemon.uriFor(controllerInQ)
    ns.register("inputqueue.controller", controllerInQ_uri)
    
    # Create drone entities, each will be separate process started by Controller
    droneInQs = DroneInputQueueContainer()
    drones = []
    for i in range(Data.numDrones):
        dronename = i
        print 'dronename is %s' % dronename
        drone = createNewDrone(dronename, Data.typeOfDrone,Data.heuristic,Data.Legs)
        drones.append(drone)
        controller.addDrone(drone)
        droneInQs.addDroneInputQueue(dronename)
    droneInQs.setLPIDs(drones)
    droneInQs_uri = daemon.register(droneInQs)
    droneInQs_uri = daemon.uriFor(droneInQs)
    ns.register("inputqueue.drones", droneInQs_uri)    

    #Shared loop controler
    loopInQs=Loops()
    loopInQs_uri = daemon.register(loopInQs)
    loopInQs_uri = daemon.uriFor(loopInQs)
    ns.register("inL.loop", loopInQs_uri)

    # Start Controller process
    pController = Process(group=None, target=controller, name='Drone Sim Controller Process')
    print 'starting controller'
    pController.start()
    while not(pController.is_alive):
        time.sleep(0.1)
    print 'Controller process is alive'
    sys.stdout.flush()
    
    # HMINT
    print 'starting hmint'
    pHMINT = Process(group=None, target=hmint, name='HMINT Process')
    pHMINT.start()
    while not(pHMINT.is_alive):
        time.sleep(0.1) 
    print 'HMINT process is alive'
    
    # CAOC
    print 'starting caoc'
    pCAOC = Process(group=None, target=caoc, name='CAOC Process')
    pCAOC.start()
    while not(pCAOC.is_alive):
        time.sleep(0.1) 
    print 'CAOC process is alive'    
    
    # Drones
    print 'starting drones'
    pDrones = []
    for i in range(0, len(drones)):
        pDrone = Process(group=None, target=drones[i], name='drone'+str(drones[i].uid), args=(Map.MapEntryPt,)) 
        pDrones.append(pDrone)
        pDrone.start()
        while not(pDrone.is_alive):
            time.sleep(0.1) 
        print 'Drone %d process is alive'  % drones[i].uid       

    # IMINT
    print 'starting imint'
    pIMINT = Process(group=None, target=imint, name='IMINT Process')
    pIMINT.start()
    while not(pIMINT.is_alive):
        time.sleep(0.1) 
    print 'IMINT process is alive'    
    
    # Run shared object requests loop
    print 'starting shared objects request loop'
    daemon.requestLoop(loopCondition=lambda:loopInQs.loopC())

    # Request loop exited, simulation complete, release resources
    daemon.unregister("inL.loop")
    daemon.unregister("inputqueue.drones")
    daemon.unregister("inputqueue.controller")
    daemon.unregister("inputqueue.caoc")
    daemon.unregister("inputqueue.caoc")
    daemon.unregister("inputqueue.hmint")

    try:
        del hmint
        print "Deleted hmint!"
        del hmintInQ
        print "Deleted hmintInq!"
        del caoc
        print "Deleted caoc!"
        del caocInQ
        print "Deleted caocInQ!"
        del drones
        print "Deleted drones!"
        del droneInQs
        print "Deleted dronesInQs!"
        del imint
        print "Deleted imint!"
        del imintInQ
        print "Deleted imint!"
        del controller
        print "Deleted controller!"
        del controllerInQ
        print "Deleted controller!"
        print "Deleted all variables!"

    except:
        print "Failed to delete all variables"


    daemon.close()
    print "\n\n\n"

class Loops:
#Input: none Output: none
#Description: This class is a shared memeory object used to end the simulation when IMINT gets enough targets.
    def __init__(self):
        self.control=1
    def getCon(self):
        return self.control
    def setCon(self,obj):
        ll.acquire()
        self.control=obj
        ll.release()
    def loopC(self):
        if(self.getCon()==1):
            return True
        else:
            return False

