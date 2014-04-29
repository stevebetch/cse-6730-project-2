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
    
    #x=5
    #a=[2,4,6,8]
    #if x>=a[len(a)-1]:
        #a.append(x)    
    #else:
        #for i in range(len(a)):
            #if x<a[i]:
                #a.insert(i,x)
                #break
    #print a
    #print a.pop()
    
    for i in range(3):
        print ''
        print '############################# Heuristic ' + str(i+1) + ' #############################'
        random.seed(1)
        mapX=50
        mapY=50
        numStreets=10
        numTargets=9
        numDrones=3
        heuristic=i+1
        seedNum=1
        Nuisance=0.8    
        
        print 'Heuristic: ' + str(heuristic)
        
        print '-------------Generate Map-------------'
        Map = GenMap(mapX,mapY)
        Map.map(numStreets,Nuisance)
        randNodes=[]
        for i in range(numTargets+numDrones):
            randNodes.append(Map.RandNode())
        print 'Node List: ' + str(randNodes)
        
        print '-------------Generate HMINT, CAOC, IMINT, Drone-------------'
        
        hmint = HMINT(numTargets, randNodes)
        hmintInQ = LPInputQueue()    
        
        caoc=CAOC(numDrones,heuristic)
        caocInQ = LPInputQueue()    
        
        imint=IMINT(heuristic,numTargets)
        imintInQ = LPInputQueue()
        
        drone=Drone(0,0,heuristic)
        droneInQ=LPInputQueue()
        
        lp=[hmint,caoc,imint]
        
        print '-------------Initialize Target and Drone Data -------------'
        tData=[]
        for i in range(numTargets):
            tData.append([i,10+i,random.random(),'Vehicle',1,1,randNodes[i],10*random.random(),0,0])
        print 'Target Data: ' + str(tData)
        
        dData=[]
        for i in range(numDrones):
            dData.append([i,'Idle',randNodes[numTargets+i]])
        print 'Drone Data: ' + str(dData)          

        print '-------------Generate Messages-------------'
        dMsg=[]
        for i in range(numDrones):
            dMsg.append(Message(3,dData[i],dData[i][0],'CAOC',0))
        print 'Drone Messages: ' + str(dMsg)
        
        tMsg=[]
        for i in range(numTargets):
            tMsg.append(Message(2,tData[i],'HMINT','CAOC',i+1))
        print 'Target Messages: ' + str(tMsg)
        
        print '-------------Send Messages-------------'
        for i in range(numDrones):
            print 'Drone ' + str(dMsg[i].data[0]) + ' Location: ' + str(dMsg[i].data[2].xpos) + ', ' +str(dMsg[i].data[2].ypos)
        
        for i in range(numTargets):
            print 'Tgt ' + str(tMsg[i].data[0]) + ' Location: ' + str(tMsg[i].data[6].xpos) + ', ' +str(tMsg[i].data[6].ypos)
        
        for i in range(numDrones):
            print 'CAOC handling Drone ' + str(dMsg[i].data[0]) + ' Status Msg...'
            caoc.testHandleMessage(dMsg[i])
            print 'CAOC Priority Queue: ' + str(caoc.priorityQueue)
            print 'CAOC Drone Status Queue: ' + str(caoc.drones)
        
        for i in range(numTargets):
            print 'CAOC handling Tgt ' + str(tMsg[i].data[0]) + ' Msg from HMINT...'
            caoc.testHandleMessage(tMsg[i])
            print 'CAOC Priority Queue: ' + str(caoc.priorityQueue)
            print 'CAOC Drone Status Queue: ' + str(caoc.drones)
    
        while (len(caoc.priorityQueue)>0):
            for i in range(numDrones):
                print 'CAOC handling Drone ' + str(dMsg[i].data[0]) + ' Status Msg...'
                caoc.testHandleMessage(dMsg[i])
                print 'CAOC Priority Queue: ' + str(caoc.priorityQueue)
                print 'CAOC Drone Status Queue: ' + str(caoc.drones)    

    print ''
    print 'End'

main()
