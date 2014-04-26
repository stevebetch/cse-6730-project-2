from random import *
from multiprocessing import Queue, Lock
from Map import *
from nodes import *
from Target import *
from CAOC import *
from HMINT import *
from Drone import *
from IMINT import *
from LogicalProcess import *
from LPInputQueue import *
from state import *


def main():
    print 'Start'
 
    random.seed(1)
    mapX=300
    mapY=300
    numStreets=50
    numTargets=10
    numDrones=3
    heuristic=1
    seedNum=1
    Nuisance=0.8    
    
    print '---Generate Map---'
    Map = GenMap(mapX,mapY)
    Map.map(numStreets,Nuisance)
    randNodes=[]
    for i in range(numTargets):
        randNodes.append(Map.RandNode())
 
    print '---Generate HMINT, CAOC, IMINT---'
    
    hmint = HMINT(numTargets, randNodes)
    hmintInQ = LPInputQueue()    
    
    caoc=CAOC(numDrones,heuristic)
    caocInQ = LPInputQueue()    
    
    imint=IMINT(heuristic,numTargets)
    imintInQ = LPInputQueue()
    print 'IMINT total value: ' + str(imint.totalValue)
    
    drone=Drone(0,0,1)
    droneInQ=LPInputQueue()
    
    lp=[hmint,caoc,imint]
    
    print '---Generate Messages---'
    m2Data=[0,80,80,'Vehicle',1,1,randNodes[0],30,0,0]
    m2=Message(2,m2Data,'CAOC','IMINT',0)
    m3Data=[0,'Idle',randNodes[1]]
    m3=Message(3,m3Data,'IMINT','CAOC',1)    
    
    print '---Save and Restore State---'
    
    for i in lp:
        i.localTime=0
        drone.LocalSimTime=0
        i.saveState()
        i.localTime=3
        drone.LocalSimTime=3
        i.saveState()
        i.localTime=7
        drone.LocalSimTime=7
        i.saveState()
        i.localTime=12
        drone.LocalSimTime=12
        i.saveState()
        print str(i.LPID) + ' state queue: ' + str(i.stateQueue)
        print str(i.LPID) + ' state queue length: ' + str(len(i.stateQueue))
    

    #for i in drone.stateQueue:
        #print 'Drone LocalSimTime: ' + str(i.LocalSimTime)
    
    hmint.restoreState(6)
    caoc.restoreState(6)
    imint.restoreState(6)
    drone.restoreState(6)

    for i in lp:
        print str(i.LPID) + ' state queue: ' + str(i.stateQueue)
        print str(i.LPID) + ' local time: ' + str(i.localTime)
        print 'Drone actual local time: ' + str(drone.LocalSimTime)
        i.localTime=13
        i.saveState()
        print str(i.LPID) + ' state queue: ' + str(i.stateQueue)        
    
    
    print 'End'

main()
