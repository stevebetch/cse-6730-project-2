from DroneType1 import *
from DroneSimController import *
from HMINT import *
from IMINT import *
from CAOC import *
from multiprocessing import *
import math, time, sys

#
# Function definitions
#

def createNewDroneLP(droneType):
    print('Creating new drone of type ' + droneType)
    return Drone(droneType)

def initEnv():
    print('Environment initialized')
    
def initIMINT():
    print('IMINT initialized')
    return IMINT()
    
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
    
    #
    # initialization
    #
    
    # Urban network/map
    initEnv()
    
    # CAOC/HMINT
    caoc = CAOC()
    hmint = HMINT(caoc)
    caoc.setHMINT(hmint)
    
    # IMINT
    imint = initIMINT()
    
    # Simulation Controller
    controller = DroneSimController(caoc, imint)
    imint.setController(controller)
    caoc.setController(controller)
    
    # create drone entities
    for i in range(numDrones):
        drone = createNewDroneLP(typeOfDrone)
        controller.addDrone(drone)
        
    # Run simulation
    pController = Process(group=None, target=controller, name='Drone Sim Controller Process')
    pController.start()
    
    print "Time elapsed: ", time.time() - start_time, "s"
    #job_server.print_stats()
        