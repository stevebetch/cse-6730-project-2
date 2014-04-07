


class streetNode:
    def __init__(self,obj):
        self.nextNode=obj
        self.prevNode=obj
        self.prob=1.0
        self.targets=[] #Probabily will not use this. Or needs to be changed to a queue of some sort
        self.length=25.0
        self.xpos=0.0
        self.ypos=0.0
    
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
        self.prob=1.0
        self.targets=[] #Probabily will not use this. Or needs to be changed to a queue of some sort
        self.xpos=0.0
        self.ypos=0.0
    
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
        for i in self.Nodes:
            nodeout.append([i])
        nodeout.append(obj)
        self.Nodes=nodeout
    
    def setProb(self,obj):
        self.prob=obj


class EntryNode:
    def __init__(self,obj):
        self.nextNode=obj
        self.xpos=0
        self.ypos=0
    
    def setNextNode(self,obj):
        self.nextNode=obj


class EndNode: #this node is a terminator node for the outskirts of the map. it allows targets to move out of the map
    def __init__(self,obj):
        self.mapNode=obj
    def setNode(self,obj):
        self.mapNode=obj










