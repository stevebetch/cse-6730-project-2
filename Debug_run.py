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

b=a.MapEntryPt
b=b.nextNode
pp=Target(b)
pp.movement()