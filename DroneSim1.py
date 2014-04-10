from DroneType1 import *
from DroneSimController import *
from HMINT import *
from IMINT import *
from CAOC import *
from multiprocessing import Process, Queue
from multiprocessing.managers import SyncManager
import math, time, sys

class QueueManager(SyncManager): pass

LOCAL_HOST = 'localhost'
REMOTE_HOST = '192.168.0.3'
IMINT_PORT = 50012
PORT = 50011
AUTHKEY = 'max'

#
# Function definitions
#

def getIMINTInputQueue():
    return IMINTInputQueue

def getInputQueues():
    return inputQueues

def CreateQueueServer(p_host, p_port, p_authkey, p_name, p_description):
    QueueManager.register('get_imint_input_queue', callable = getIMINTInputQueue)
    QueueManager.register('get_queues', callable = getInputQueues)
    manager = QueueManager(address = (p_host, p_port), authkey = p_authkey)
    manager.start()
    return manager

def createNewDrone(id, droneType):
    print('Creating new drone of type ' + droneType)
    droneref = Drone(id, droneType)
    droneref.setConnectionParams(REMOTE_HOST, PORT, AUTHKEY)
    return droneref

def initEnv():
    print('Environment initialized')
    
def initIMINT():
    imintref = IMINT()
    imintref.setConnectionParams(REMOTE_HOST, PORT, AUTHKEY)
    print('IMINT initialized')
    return imintref

def initCAOC():
    caocref = CAOC()
    hmint = HMINT(numTargets)
    caocref.setHMINT(hmint)
    hmint.setCAOC(caocref)
    caocref.setConnectionParams(REMOTE_HOST, PORT, AUTHKEY)
    print('HMINT/CAOC initialized')
    return caocref
    
#
# Execution
#

# Prevent error on Windows
if __name__ == '__main__':
    
    #Start the timer
    start_time = time.time()
    
    # parameters (later get from file)
    numDrones = 3
    typeOfDrone = "DroneType1"
    startTime = 1
    endTime = 7*24*60
    numTargets = 10
    
    #
    # initialization
    #
    
    # Urban network/map
    initEnv()
    
    # Start queue server
    global inputQueues
    global IMINTInputQueue
    manager = CreateQueueServer(LOCAL_HOST, PORT, AUTHKEY, \
                                        'DroneSimMsgServer', 'Drone Simulation Message Server')  
    inputQueues = manager.dict()
    IMINTInputQueue = manager.list()
    
    # CAOC/HMINT
    caoc = initCAOC()
    caocInQ = manager.Queue()   
    inputQueues['caoc'] = caocInQ
    
    # IMINT
    imint = initIMINT()
    imintInQ = manager.Queue()
    inputQueues['imint'] = imintInQ    
    
    # Simulation Controller
    controller = DroneSimController(caoc, imint)
    controller.setConnectionParams(REMOTE_HOST, PORT, AUTHKEY)
    controllerInQ = manager.Queue()
    inputQueues['controller'] = controllerInQ
    
    # create drone entities
    droneInQs = {}
    for i in range(numDrones):
        dronename = 'drone', i
        drone = createNewDrone(dronename, typeOfDrone)
        controller.addDrone(drone)
        droneInQ = manager.Queue()
        droneInQs[dronename] = droneInQ
    inputQueues['drones'] = droneInQs              
        
    # Run simulation
    pController = Process(group=None, target=controller, name='Drone Sim Controller Process')
    pController.start()
    pController.join()
    
    print "Time elapsed: ", time.time() - start_time, "s"
    #job_server.print_stats()
        