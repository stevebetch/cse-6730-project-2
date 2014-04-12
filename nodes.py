import random


class streetNode:
    def __init__(self,obj):
        self.nextNode=obj
        self.prevNode=obj
        self.Detectprob=random.uniform(0,.8)#justification for limiting to 80%? - Jane
        self.Trackprob=random.uniform(0,.6)############# NEED TO CHANGE THIS TO THE CORRECT TYPE OF DISTRIBUTION!!! should vary with the type of drone/sensor - Jane
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
    def __init__(self,obj):
        self.numRoads=4.0 #number of road nodes connected to an intersection
        self.Nodes=[]
        self.NodeLeng=[]
        self.Detectprob=random.uniform(0,.8)
        self.Trackprob=random.uniform(0,.6)
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
            nodeout.append([i])
        return nodeout
    
    def setRoadnode(self,obj): #Most likely need to change this
        nodeout=[]
        count=0
        for i in self.Nodes:
            nodeout.append([i])
            count+=1
        nodeout.append(obj)
        self.Nodes=nodeout
        self.setnumRoads(count)
    
    def setLeng(self,obj):
        lengths=[]
        for i in self.NodeLeng:
            lengths.append([i])
        length.append(obj)
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
    
    def setNextNode(self,obj):
        self.nextNode=obj


class EndNode: #this node is a terminator node for the outskirts of the map. it allows targets to move out of the map
    def __init__(self,obj):
        self.mapNode=obj
        self.nodeType=3
    def setNode(self,obj):
        self.mapNode=obj










