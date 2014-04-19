#!/usr/env/ python

from Map import *
from Drone import *
from Target import *

a=GenMap(480,480)
a.map(50,.8)
ger=LogicalProcess()

drone=Drone(3,ger)
drone.setJokerBingo()

drone.setEntry(a.MapEntryPt)
moo=a.RandNode()
drone.target=Target(moo)
drone.saveState()
drone.updateTime(800)
drone.saveState()
drone.restoreState(0)
#drone.run(a.MapEntryPt)
#for i in range(50):
#    b=a.RandNode()
#    pp=Target(b)
#    pp.movement()
#    count=0
#    start_time = time.time()
#    cntmax=50000
#    try:
#        while(count<cntmax):
#            count+=1
#            pp.movement()
#
#    except:
#        print pp.node

#    print "Time elapsed to move a target",cntmax,"times on the map: ", time.time() - start_time, "s"




