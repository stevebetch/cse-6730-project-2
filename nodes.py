import random


class streetNode:
    def __init__(self,obj,mid):
    # Input: map node, nuisence factor
    # Output: A street node object  
    # Description: This is a map object. These nodes contain all of the data for the doubly linked list undirected graph. Contain probabilities, links to other nodes and coordinates.

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
    # Input: map node, 
    # Output: NONE
# Description:SETS the next node on the map

        self.nextNode=obj
    
    def setPrevNode(self,obj):
    #see above. sets previous node.
        self.prevNode=obj
    
    def setProb(self,probNum):
      #Input: probability value. Output: None: decription: sets node probabilities
        self.prob=probNum
    
    def setLeng(self,obj):
        self.length=obj

class intersecNode:     
 #This class houses the intersection nodes. This class houses most of the same info as the street nodes. The only diference is this class handles more links than a street node

    def __init__(self,obj,mid):
    # Input: map node, nuisence factor
    # Output: An intersection node object  
    # Description: This is a map object. These nodes contain all of the data for the doubly linked list undirected graph. Contain probabilities, links to other nodes and coordinates.

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
#Input: x/y coordinates. Output: None. Description: Sets the x and y coordinates of the inetersection node.
        self.xpos=x
        self.ypos=y
    
    def getRoadnode(self):
#Input: none Output: an array of nodes connected to the intersection. Description: Gets all of the roads connected to an intersection

        nodeout=[]
        for i in self.Nodes:
            nodeout.append(i)
        return nodeout
    
    def setRoadnode(self,obj): 
#Input: a road (street or intersection) node Output: none. Description: Appends another node to the intersection list. Sets the number of roads connected.

        nodeout=[]
        count=0
        for i in self.Nodes:
            nodeout.append(i)
            count+=1
        nodeout.append(obj)
        self.Nodes=nodeout
        self.setnumRoads(count)
    
    def setLeng(self,obj): 
#Input: distance from intersection to another interection Output:None Description: Appends the distance to another intersection array
        lengths=[]
        for i in self.NodeLeng:
            lengths.append([i])
        lengths.append(obj)
        self.NodeLeng=lengths

    def setProb(self,obj): 
 #Input: probability Output: none. Description: sets node probability
        self.prob=obj

    def setnumRoads(self,num):
#Input: num roads Output: none. Description: Sets the number of roads
    
        self.numRoads=num

class EntryNode:
#This class is a specialty class. It is the entry node through which the drones enter the map. Initialization takes in a map object and creates the entry node. 
    def __init__(self,obj):
        self.nextNode=obj
        self.xpos=0
        self.ypos=0
        self.nodeType=2
        self.prob=0
    
    def setNextNode(self,obj):
#Input: roadobject Output: none. Description: Sets the object that the entry node is connected to. as well as its probability
        self.nextNode=obj
        self.prob=self.nextNode.prob #Nuisance value


class EndNode: 
#this node is a terminator node for the outskirts of the map. it redirects targets back into the map.
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
    #Input: road object Output: none. Description: Sets the connecting nodes for the end node.
        self.mapNode=obj
        self.nextNode=obj
        self.prevNode=obj









