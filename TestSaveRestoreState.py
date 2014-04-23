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
 
    print '---Generate CAOC and IMINT---'
    caoc=CAOC(numDrones,heuristic)
    hmint = HMINT(numTargets, seedNum, randNodes)
    caoc.setHMINT(hmint)
    hmint.setCAOC(caoc)
    caocInQ = LPInputQueue()
    
    imint=IMINT(heuristic)
    imintInQ = LPInputQueue()
    print 'IMINT total value: ' + str(imint.totalValue)

    
    print '---Generate and Add Messages---'
    m2Data=[0,80,80,'Vehicle',1,1,randNodes[0],30,0,0]
    m2=Message(2,m2Data,'CAOC','IMINT',0)
    m3Data=[0,'Idle',randNodes[1]]
    m3=Message(3,m3Data,'IMINT','CAOC',1)    
    
    print '---Save and Restore State---'
    print 'CAOC Local Time: ' + str(caoc.localTime)
    print 'IMINT Local Time: ' + str(imint.localTime)
    caoc.saveState()
    imint.saveState()
    caoc.saveState()
    imint.saveState()    
    print 'CAOC state queue: ' + str(caoc.stateQueue)    
    print 'IMINT state queue: ' + str(imint.stateQueue)

    print 'CAOC state queue length: ' + str(len(caoc.stateQueue))
    print 'CAOC state queue[0]: ' + str(caoc.stateQueue[0])
    print 'IMINT state queue length: ' + str(len(imint.stateQueue))
    print 'IMINT state queue[0]: ' + str(imint.stateQueue[0])
    print 'IMINT state queue[0].localTime: ' + str(imint.stateQueue[0].localTime)

    imint.restoreState(9)
    caoc.restoreState(7)
    print 'CAOC state queue: ' + str(caoc.stateQueue)    
    print 'IMINT state queue: ' + str(imint.stateQueue)
    
    
    print 'End'

main()
