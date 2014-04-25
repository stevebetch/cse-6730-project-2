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
    
    imint=IMINT(heuristic)
    imintInQ = LPInputQueue()
    print 'IMINT total value: ' + str(imint.totalValue)
    
    print '---Generate Messages---'
    m2Data=[0,80,80,'Vehicle',1,1,randNodes[0],30,0,0]
    m2=Message(2,m2Data,'CAOC','IMINT',0)
    m3Data=[0,'Idle',randNodes[1]]
    m3=Message(3,m3Data,'IMINT','CAOC',1)    
    
    print '---Save and Restore State---'
    hmint.localTime=3
    caoc.localTime=3
    imint.localTime=3    
    print 'HMINT Local Time: ' + str(hmint.localTime)
    print 'CAOC Local Time: ' + str(caoc.localTime)
    print 'IMINT Local Time: ' + str(imint.localTime)
    hmint.saveState()
    caoc.saveState()
    imint.saveState()
    hmint.localTime=7
    caoc.localTime=7
    imint.localTime=7      
    hmint.saveState()   
    caoc.saveState()
    imint.saveState()
    hmint.localTime=12
    caoc.localTime=12
    imint.localTime=12      
    hmint.saveState()   
    caoc.saveState()
    imint.saveState()        
    print 'HMINT state queue: ' + str(hmint.stateQueue)    
    print 'CAOC state queue: ' + str(caoc.stateQueue)    
    print 'IMINT state queue: ' + str(imint.stateQueue)

    print 'HMINT state queue length: ' + str(len(hmint.stateQueue))
    print 'HMINT state queue[0]: ' + str(hmint.stateQueue[0])
    print 'CAOC state queue length: ' + str(len(caoc.stateQueue))
    print 'CAOC state queue[0]: ' + str(caoc.stateQueue[0])
    print 'IMINT state queue length: ' + str(len(imint.stateQueue))
    print 'IMINT state queue[0]: ' + str(imint.stateQueue[0])
    print 'IMINT state queue[0].localTime: ' + str(imint.stateQueue[0].localTime)

    hmint.restoreState(7)
    caoc.restoreState(2)
    imint.restoreState(13)

    print 'HMINT state queue: ' + str(hmint.stateQueue)   
    print 'CAOC state queue: ' + str(caoc.stateQueue)    
    print 'IMINT state queue: ' + str(imint.stateQueue)
    print 'HMINT Local Time: ' + str(hmint.localTime)
    print 'CAOC Local Time: ' + str(caoc.localTime)
    print 'IMINT Local Time: ' + str(imint.localTime)    
    
    
    print 'End'

main()
