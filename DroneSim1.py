from DroneType1 import *
from HMINT import *
from CAOC import *
import math, time, thread, sys
import pp


#setup the parallel python
# tuple of all parallel python servers to connect with
ppservers = ()
#ppservers = ("10.0.0.1",)


job_server = pp.Server(ppservers=ppservers)
print "Starting pp with", job_server.get_ncpus(), "workers"

#Start the timer
start_time = time.time()

# parameters (later get from file)
numDrones = 3
typeOfDrone = "DroneType1"
startTime = 1
endTime = 7*24*60

# initialization
initEnv() # urban network
caoc = CAOC()
hmint = HMINT(caoc)
caoc.setHMINT(hmint)
imint = initIMINT()
controller = DroneSimController(caoc, imint)

# create drone entities
for i in range(numDrones):
    drone = createNewDroneLP(typeOfDrone)
    controller.addDrone(drone)
    
# Run simulation
controller.run()




def createNewDroneLP():
    pass









print "Time elapsed: ", time.time() - start_time, "s"
job_server.print_stats()
    