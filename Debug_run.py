#!/usr/env/ python

from Map import *
from Drone import *
from Target import *

a=GenMap(480,480)
a.map(50)

#drone=Drone(3)
#drone.setJokerBingo()
#drone.updateTime(800)
#drone.setEntry(a.MapEntryPt)
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

    print "Time elapsed to move a target",cntmax,"times on the map: ", time.time() - start_time, "s"