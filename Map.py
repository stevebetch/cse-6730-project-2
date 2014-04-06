#this function will generate the map for the simulation. Also creates the map class and the nodes and intersections.
# the map function probably needs to broken into multiple sub functions for clarity

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
        
        random.seed(3) #PUT IN FOR DEBUGGING ONLY!!!

    def map(self, numStreets):

        EW=math.floor(numStreets/2.0)
        NS=math.ceil(numStreets/2.0)

        print '\nNumber of East\West streets',EW
        print '\nNumber of North\South streets:',NS

        for i in range(0,int(NS)):
            point=random.randint(0,self.xleng)
            self.NSpos.append(point)
        #print 'NS Street ',i,' is at position ', point
        # print '\n'
        for j in range(0,int(EW)) :
            point=random.randint(0,self.yleng)
            self.EWpos.append(point)
        #   print 'EW Street ', j,' is at position ', point
        # print '\n'
        b=EntryNode(0)
        b.setProb(random.random()) #NEED TO MAKE THIS A BOUNDED PROBABILITY. CURRENTLY (0,1)
        self.MapEntryPt=b

        self.NSpos.sort() # get the lists sorted into the correct order
        self.EWpos.sort()

        for k in self.NSpos: #create all of the intersection nodes
            for l in self.EWpos:
                a=intersecNode(0)
                a.setXY(k,l)
                self.intersectionNodes.append(a)
        
        
        icount=0
        jcount=0
        # print 'NS pos',self.NSpos
        #print '\n'
        for i in self.NSpos:
            jcount=0
            for j in self.EWpos:
                if(icount==0):
                    length=i
                elif(icount==int(NS)):
                    length=i-self.NSpos[icount-1]
                    length2=self.xleng-i
                else:
                    length=i-self.NSpos[icount-1]


                modnum=4.0 #min number of nodes in a street length
                modmax=20.0 #max number of nodes

                while(modnum<=modmax): #figure out an ideal, round number of nodes that makes the nodes equidistant
                    
        
                    if(modnum==modmax): #cant devide the length by an even number. Crap. pick a rough length we want and go with it.
                        if(length>20):
                            modnum=length/10.0 #have a node every 10 feet.
                        elif(length<10):
                            modnum=length/2.0
                        else: #need to capture where the length is between 4 and 20 and prime.
                            modnum=length/3.0 #need to decide still. Discussions may be needed.
                    
                        break
                    if(length%modnum==0 and length!=int(modnum)):
                    
                        break
                    else:
                        modnum+=1
            
                print 'number of street nodes:',modnum
                if(icount<int(NS)): #not the edge case
                    for k in range(int(modnum),0,-1): #create each node for each street length
                        
                        a=streetNode(0)
                        nextNum=len(self.streetNodes)-1 # fencepost error
                        self.streetNodes.append(a)
                        nNum=len(self.streetNodes)
                        #  print 'Next number', nextNum, 'total number:', nNum
                        
                        if(k==0 & icount==0): #node is at the edge of the sim
                            prevNd=EndNode(a) #point next node to end nodes outside of the sim
                            self.streetNodes[nextNum+1].prevNode=prevNd
                            self.streetNodes[nextNum+1].nextNode=self.streetNodes[nextNum]
                        elif(k==int(modnum)): #connect up to the correct intersection
                            for a in self.intersectionNodes:
                                if(a.xpos==i and a.ypos==j):
                            ######## STOPPING POINT ##### need to locate the intersection and connect back up
                            #Then take care of the corner case in the next set of else statement,
                            # Then copy/paste code and run thru the N/S streets.
                            self.streetNodes[nextNum+1].nextNode=#intersection
                            
                        
                        else:
                            self.streetNodes[nextNum+1].nextNode=self.streetNodes[nextNum]
                            self.streetNodes[nextNum].prevNode=self.streetNodes[nextNum+1]
                        
                else: #need 2 for loops for this case. need to go rigth and left of the intersection
                    for k in range(0,int(modnum)): #create each node for each street length
                        a=streetNode(0)
                        
                        if(k==int(modnum)): #node is at the edge of the sim
                            nextNd=EndNode(a) #point next node to end nodes outside of the sim


                        
                        
    
        
                jcount+=1
            icount+=1


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
        self.Nodes=[obj]
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
            nodeout.append([i,self.Nodes[i]])

    def setRoadnode(self,obj): #Most likely need to change this
        self.Nodes=obj

    def setProb(self,obj):
        self.prob=obj


class EntryNode:
    def __init__(self,obj):
        self.nextNode=obj
        self.prob=1.0
        self.length=10.0

    def setNextNode(self,obj):
        self.nextNode=obj

    def setProb(self,probNum):
        self.prob=probNum

    def setLeng(self,obj):
        self.length=obj


class EndNode: #this node is a terminator node for the outskirts of the map. it allows targets to move out of the map
    def __init__(self,obj):
        self.mapNode=obj
    def setNode(self,obj):
        self.mapNode=obj









