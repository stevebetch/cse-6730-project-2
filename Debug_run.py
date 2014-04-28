#!/usr/env/ python

from Map import *
from Drone import *
from Target import *

a=GenMap(600,600)
a.map(100,.8)
#ger=LogicalProcess()
#
#drone=Drone(3,ger,1,41760)
#drone.setJokerBingo()
#
#drone.setEntry(a.MapEntryPt)
#moo=a.RandNode()
#drone.target=Target(moo)
#drone.saveState()
#drone.updateTime(800)
#drone.saveState()
#drone.restoreState(0)
#drone.setEntry(mapObj) #MUST PASS THE ENTRY NODE!!! (map.MapEntryPt)
#drone.currentNode=a.MapEntryPt #the only time we directly set the current node.
#drone.LocalSimTime=drone.localTime
#drone.setJokerBingo()
#drone.flyTotgt(drone.target.node.xpos,drone.target.node.ypos)
#start_time = time.time()
#targetcount=0
#targetnum=5000000
#while(targetcount<targetnum):
#    
#    if(drone.Bingo<0):
#        drone.ReturnToBase()
#    
##    print drone.target
#    if(drone.target==42): #NO TARGET IN QUEUE
#        moo=a.RandNode()
#        drone.target=Target(moo)
##        print " Target created at:",drone.target.node.xpos,",",drone.target.node.ypos
#
#    
#    # Check fuel before anything else!!
#    if(not(drone.target==42)):
#        if(not(drone.jokerflag)): #joker not set yet. can search for targets
#            if(not(drone.detectBool)): #dont have a detection
#                drone.search()
#                drone.detection()
#                drone.searchdwell+=drone.searchTime
#            
#            else: #we have a detection! woooo
#                drone.detection()
#                drone.searchdwell=0
#        
#        else: # joker flag set.
#            if(not(drone.detectBool)):
#                #dont have an active detection. RTB.
#                drone.ReturnToBase()
#            else: # detection flag set. We have a target in active track.
#                if(drone.Bingo>0): #we still have fuel!
#                    # We have fuel and can still start tracking.
#                    drone.detection()
#                else:
#                    drone.ReturnToBase()
#        if(not(drone.target==42)):
#            if(drone.TarTime>=drone.target.ObsTime):# Observation time is larger than needed time. Target satisfied.
##                drone.SendIMINT()
##                print"Target tracked! Tracked target for:",drone.TarTime,"sec"
#                drone.removeTgt()
#                targetcount+=1


#drone.run(a.MapEntryPt)
for i in range(50):
    b=a.RandNode()
    pp=Target(b)
    pp.movement()
    count=0
    start_time = time.time()
    cntmax=50000
    try:
        while(count<cntmax):
            count+=1
            pp.movement()

    except:
        print pp.node
print "Time elapsed to move",cntmax,"targets", time.time() - start_time, "s"




