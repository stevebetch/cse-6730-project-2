import random


class streetNode:
    def __init__(self,obj,mid):
        self.nextNode=self
        self.prevNode=self
        self.prob=random.triangular(mid-.1,mid+.1,mid) #Nuisance value
        #        self.Trackprob=random.triangular(mid-.1,mid+.1,mid)
        self.targets=[] #Probabily will not use this. Or needs to be changed to a queue of some sort
        self.length=25.0
        self.xpos=0.0
        self.ypos=0.0
        self.nodeType=0
    
    def setNextNode(self,obj):
        self.nextNode=obj
    
    def setPrevNode(self,obj):
        self.prevNode=obj
    
    def setProb(self,probNum):
        self.prob=probNum
    
    def setLeng(self,obj):
        self.length=obj

class intersecNode:
    def __init__(self,obj,mid):
        self.numRoads=4.0 #number of road nodes connected to an intersection
        self.Nodes=[]
        self.NodeLeng=[]
        self.prob=random.triangular(mid-.1,mid+.1,mid) #Nuisance value
    #        self.Trackprob=random.triangular(mid-.1,mid+.1,mid)

        self.targets=[] #Probabily will not use this. Or needs to be changed to a queue of some sort
        self.xpos=0.0
        self.ypos=0.0
        self.nodeType=1
    
    def setXY(self,x,y):
        self.xpos=x
        self.ypos=y
    
    def getRoadnode(self):
        nodeout=[]
        for i in self.Nodes:
            nodeout.append(i)
        return nodeout
    
    def setRoadnode(self,obj): #Most likely need to change this
        nodeout=[]
        count=0
        for i in self.Nodes:
            nodeout.append(i)
            count+=1
        nodeout.append(obj)
        self.Nodes=nodeout
        self.setnumRoads(count)
    
    def setLeng(self,obj):
        lengths=[]
        for i in self.NodeLeng:
            lengths.append([i])
        lengths.append(obj)
        self.NodeLeng=lengths

    def setProb(self,obj):
        self.prob=obj

    def setnumRoads(self,num):
        self.numRoads=num

class EntryNode:
    def __init__(self,obj):
        self.nextNode=obj
        self.xpos=0
        self.ypos=0
        self.nodeType=2
        self.prob=0
    
    def setNextNode(self,obj):
        self.nextNode=obj
        self.prob=self.nextNode.prob #Nuisance value

class EndNode: #this node is a terminator node for the outskirts of the map. it allows targets to move out of the map
    def __init__(self,obj,mid):
        self.mapNode=obj
        self.nextNode=obj
        self.prevNode=obj
        self.nodeType=3
        self.xpos=0
        self.ypos=0
        self.prob=random.triangular(mid-.1,mid+.1,mid) #Nuisance value
    #        self.Trackprob=random.triangular(mid-.1,mid+.1,mid)


    def setNode(self,obj):
        self.mapNode=obj
        self.nextNode=obj
        self.prevNode=obj









