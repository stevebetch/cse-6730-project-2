from DroneType1 import *
from HMINT import *
from CAOC import *

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
    