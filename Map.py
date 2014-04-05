#this function will generate the map for the simulation. Also creates the map class and the nodes and intersections.

import thread, multiprocessing
import os
import math
import random



class GenMap:
    def __init__(self,XgridSize,YgridSize):
        self.streetNodes=[] #array containing all of the street nodes
        self.intersectionNodes=[] #array containing all of the intersection nodes
        self.NSpos=[] # physical mapping to the grid. will say North/south street 1,2,3... is at position x
        self.EWpos=[] #physical mapping to grid. Will say E/W street 1,2,3.... is at position y
        self.xleng=XgridSize #limit on grid size
        self.yleng=YgridSize
        self.MapEntryPt=[]
        random.seed(3)

    def map(self, numStreets):

        EW=math.floor(numStreets/2.0)
        NS=math.ceil(numStreets/2.0)

        print '\nNumber of East\West streets',EW
        print '\nNumber of North\South streets:',NS



class streetNode:
    def __init__(obj):
        self.nextNode=obj
        self.prevNode=obj
        self.prob=1.0
        self.targets=[] #Probabily will not use this. Or needs to be changed to a queue of some sort
        self.length=25.0

    def setNextNode(obj):
        self.nextNode=obj

    def setPrevNode(obj):
        self.prevNode=obj

    def setProb(probNum):
        self.prob=probNum

class intersecNode:
    def __init__(obj):
        self.numRoads=4.0 #number of road nodes connected to an intersection
        self.Nodes=[obj]
        self.prob=1.0
        self.targets=[] #Probabily will not use this. Or needs to be changed to a queue of some sort






