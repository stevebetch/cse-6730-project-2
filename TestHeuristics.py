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
    
    for i in range(3):
        print ''
        print '############################# Heuristic ' + str(i+1) + ' #############################'
        random.seed(1)
        mapX=30
        mapY=30
        numStreets=5
        numTargets=1
        numDrones=1
        heuristic=i+1
        seedNum=1
        Nuisance=0.8    
        
        print 'Heuristic: ' + str(heuristic)
        
        print '---Generate Map---'
        Map = GenMap(mapX,mapY)
        Map.map(numStreets,Nuisance)
        randNodes=[]
        for i in range(numTargets+numDrones):
            randNodes.append(Map.RandNode())
        
        print '---Generate HMINT, CAOC, IMINT, Drone---'
        
        hmint = HMINT(numTargets, randNodes)
        hmintInQ = LPInputQueue()    
        
        caoc=CAOC(numDrones,heuristic)
        caocInQ = LPInputQueue()    
        
        imint=IMINT(heuristic,numTargets)
        imintInQ = LPInputQueue()
        print 'IMINT total value: ' + str(imint.totalValue)
        
        drone=Drone(0,0,heuristic)
        droneInQ=LPInputQueue()
        
        lp=[hmint,caoc,imint]
        
        print '---Initialize Target and Drone Data ---' 
        t0Data=[0,10,10,'Vehicle',1,1,randNodes[0],10,0,0]
        #t1Data=[1,11,11,'Vehicle',1,1,randNodes[1],11,0,0]
        #t2Data=[2,12,12,'Vehicle',1,1,randNodes[2],12,0,0]
        #t3Data=[3,13,13,'Vehicle',1,1,randNodes[3],13,0,0]
        #t4Data=[4,14,14,'Vehicle',1,1,randNodes[4],14,0,0]
        #tData=[t0Data,t1Data,t2Data,t3Data,t4Data]
        
        d0Data=[0,'Idle',randNodes[numDrones]]
        #d1Data=[1,'Idle',randNodes[numDrones+1]]
        #d2Data=[2,'Idle',randNodes[numDrones+2]]
        #dData=[d0Data,d1Data,d2Data]
        
        print '---Generate Messages---'  
        m0=Message(3,d0Data,d0Data[0],'CAOC',0)
        m1=Message(2,t0Data,'HMINT','CAOC',1)
        
        print '---Send Messages---'  
        print 'Drone Location: ' + str(m0.data[2].xpos) + ', ' +str(m0.data[2].ypos)
        print 'Tgt Location: ' + str(m1.data[6].xpos) + ', ' +str(m1.data[6].ypos)
        
        print 'CAOC handling Drone Status Msg from Drone ' + str(m0.data[0]) + '...'
        caoc.testHandleMessage(m0)
        print 'CAOC Priority Queue: ' + str(caoc.priorityQueue)
        print 'CAOC Drone Status Queue: ' + str(caoc.drones)
        
        print 'CAOC handling Tgt Msg from HMINT...'
        caoc.testHandleMessage(m1)
        print 'CAOC Priority Queue: ' + str(caoc.priorityQueue)
        print 'CAOC Drone Status Queue: ' + str(caoc.drones)

    
    print 'End'

main()
