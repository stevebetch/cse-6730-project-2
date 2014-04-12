#this function will generate the map for the simulation. Also creates the map class and the nodes and intersections.
# the map function probably needs to broken into multiple sub functions for clarity

import os
import math
import random, time
from nodes import *



class GenMap:
    def __init__(self,XgridSize,YgridSize):
        self.streetNodes=[] #array containing all of the street nodes
        self.intersectionNodes=[] #array containing all of the intersection nodes
        #self.endNodes=[]
        self.NSpos=[] # physical mapping to the grid. will say North/south street 1,2,3... is at position x
        self.EWpos=[] #physical mapping to grid. Will say E/W street 1,2,3.... is at position y
        self.xleng=XgridSize #limit on grid size
        self.yleng=YgridSize
        self.MapEntryPt=[]
        visGrid=[[]] #probably wont be used. For Growth.
        
        random.seed(3) #PUT IN FOR DEBUGGING ONLY!!!

    def map(self, numStreets):
        
        start_time = time.time()
        EW=math.floor(numStreets/2.0)
        NS=math.ceil(numStreets/2.0)
        
        print '\nNumber of East\West streets',EW
        print '\nNumber of North\South streets:',NS
        
        self.NSpos=random.sample(xrange(self.xleng),int(NS))
        #print 'NS Street ',i,' is at position ', point
        # print '\n'
        
        self.EWpos=random.sample(xrange(self.yleng),int(EW))
        #   print 'EW Street ', j,' is at position ', point
        # print '\n'
        b=EntryNode(0)
        # b.setProb(random.random()) #NEED TO MAKE THIS A BOUNDED PROBABILITY. CURRENTLY (0,1)
        self.MapEntryPt=b
        
        self.NSpos.sort() # get the lists sorted into the correct order
        self.EWpos.sort()
        
        for k in self.NSpos: #create all of the intersection nodes
            for l in self.EWpos:
                a=intersecNode(0)
                a.setXY(k,l)
                self.intersectionNodes.append(a)
        self.connectNSNodes(NS,EW)
        self.connectEWNodes(NS,EW)
        
        xmin=1000
        ymin=1000
        mindist=math.sqrt(xmin**2+ymin**2)
        #self.MapEntryPt.nextNode=self.endNodes[1] #Attach entry point to an end node
        for node in self.intersectionNodes:
            xpo=node.xpos
            ypo=node.ypos
            if(math.sqrt(xpo**2+ypo**2)<mindist):
                xmin=xpo
                ymin=ypo
                mindist=math.sqrt(xmin**2+ymin**2)
                minNode=node
        
        self.MapEntryPt.nextNode=minNode
        self.MapEntryPt.xpos=xmin
        self.MapEntryPt.ypos=ymin
        print "Map Entry point at:",xmin,",",ymin
        print "Time elapsed to generate map: ", time.time() - start_time, "s"
        

    def connectNSNodes(self,NS,EW):
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
                    length2=self.xleng-i #2nd length that should be used to calc length from last intersection to sim wall
                else:
                    length=i-self.NSpos[icount-1]
                
                
                modnum=4.0 #min number of nodes in a street length
                modmax=20.0 #max number of nodes
                
                while(modnum<=modmax): #figure out an ideal, round number of nodes that makes the nodes equidistant
                    
                    
                    if(int(modnum)==int(modmax)): #cant devide the length by an even number. Crap. pick a rough length we want and go with it.
                        if(length>20):
                            modnum=length/10.0 #have a node every 10 feet.
                        elif(length==1):
                            modnum=1
                        elif(length<10):
                            modnum=length/2.0

                        else: #need to capture where the length is between 4 and 20 and prime.
                            modnum=length/3.0 #need to decide still. Discussions may be needed.
                        
                        break
                    if(length%modnum==0 and length!=int(modnum)):
                        
                        break
                    else:
                        modnum+=1
            #print 'number of street nodes:',modnum, ' Length:', length,
                if(icount==int(NS)):
                    modnum=4.0 #min number of nodes in a street length
                    modmax=20.0 #max number of nodes
                    while(modnum<=modmax): #figure out an ideal, round number of nodes that makes the nodes equidistant
                    
                    
                        if(int(modnum)==int(modmax)): #cant devide the length by an even number. Crap. pick a rough length we want and go with it.
                            if(length2>20):
                                modnum=length/10.0 #have a node every 10 feet.
                            elif(length2==1):
                                modnum=1
                            elif(length2<10):
                                modnum=length/2.0
                        
                            else: #need to capture where the length is between 4 and 20 and prime.
                                    modnum=length/3.0 #need to decide still. Discussions may be needed.
                        
                                    break
                        if(length2%modnum==0 and length2!=int(modnum)):
                        
                            break
                        else:
                            modnum+=1
        #print 'number of street nodes:',modnum, ' Length2:', length2,
                        #print 'number of street nodes:',modnum, ' Length:', length,
                if(icount<=int(NS) and modnum>1): #not the edge case
                    for k in range(int(modnum),1,-1): #create each node for each street length
                        
                        a=streetNode(0)
                        a.xpos=i-(length/modnum)*k
                        a.ypos=j
                        a.setLeng(length)
                        
                        nextNum=len(self.streetNodes)-1 # fencepost error
                        self.streetNodes.append(a)
                        nNum=len(self.streetNodes)
                        #  print 'Next number', nextNum, 'total number:', nNum
                        
                        if(k==1 and icount==0): #node is at the edge of the sim
                            prevNd=EndNode(a) #point next node to end nodes outside of the sim
                            self.streetNodes[nextNum+1].prevNode=prevNd
                            self.streetNodes[nextNum+1].nextNode=self.streetNodes[nextNum]
                            self.streetNodes[nextNum].prevNode=self.streetNodes[nextNum+1]
                        elif(k==int(modnum)): #connect up to the correct intersection
                            for a in self.intersectionNodes:
                                if(a.xpos==i and a.ypos==j):
                                    index=self.intersectionNodes.index(a)
                            
                            self.streetNodes[nextNum+1].nextNode=self.intersectionNodes[index]#intersection
                            self.intersectionNodes[index].setRoadnode(self.streetNodes[nextNum+1])
                            self.intersectionNodes[index].setLeng(length)
                                #b=self.intersectionNodes[index].getRoadnode
                                # print b
                
                        elif(k==1 and icount !=0): # connect the road to the other intersection
                            for a in self.intersectionNodes:
                                if(a.xpos==self.NSpos[icount-1] and a.ypos==j):
                                    index=self.intersectionNodes.index(a)
                            self.streetNodes[nextNum+1].nextNode=self.intersectionNodes[index]#intersection
                            self.intersectionNodes[index].setRoadnode(self.streetNodes[nextNum+1])
                            self.intersectionNodes[index].setLeng(length)
                            #  b=self.intersectionNodes[index].getRoadnode
                            #           print b
                        
                        else:
                            self.streetNodes[nextNum+1].nextNode=self.streetNodes[nextNum]
                            self.streetNodes[nextNum].prevNode=self.streetNodes[nextNum+1]
                
                if(icount==int(NS) and modnum>1): # need to go rigth and left of the intersection at the furthest right intersection
                    for k in range(1,int(modnum)): #create each node for each street length
                        
                        a=streetNode(0)
                        a.xpos=i+(length2/modnum)*k
                        a.ypos=j
                        a.setLeng(length2)

                        nextNum=len(self.streetNodes)-1 # fencepost error
                        self.streetNodes.append(a)
                        nNum=len(self.streetNodes)
                        
                        if(k==int(modnum)): #node is at the edge of the sim
                                nextNd=EndNode(a) #point next node to end nodes outside of the sim
                                if(k==int(modnum)): #node is at the edge of the sim
                                    nextNd=EndNode(a) #point next node to end nodes outside of the sim
                                    nextNd.mapNode=self.streetNodes[nextNum+1]
                                    # self.endNodes.append(nextNd)
                                    self.streetNodes[nextNum+1].nextNode=nextNd
                                    self.streetNodes[nextNum+1].prevNode=self.streetNodes[nextNum]
                                    self.streetNodes[nextNum].nextNode=self.streetNodes[nextNum+1]
                                elif(k==1): #connect up to the correct intersection
                                    for a in self.intersectionNodes:
                                        if(a.xpos==i and a.ypos==j):
                                            index=self.intersectionNodes.index(a)
                                    
                                    ######## STOPPING POINT #####
                                    # Then copy/paste code and run thru the N/S streets.
                                    self.streetNodes[nextNum+1].prevNode=self.intersectionNodes[index]#intersection
                                    self.intersectionNodes[index].setRoadnode(self.streetNodes[nextNum+1])
                                    self.intersectionNodes[index].setLeng(length2)
                    #b=self.intersectionNodes[index].getRoadnode
                    # print b
                    
                                else:
                                    self.streetNodes[nextNum].nextNode=self.streetNodes[nextNum+1]
                                    self.streetNodes[nextNum+1].prevNode=self.streetNodes[nextNum]
                if(modnum==1 and icount==0):
                #Need to connect the intersection to an end pont? or do we just act like its a T-section? Im thinking we act like its a T intersection
                    a=1
                elif(modnum==1 and icount!=int(NS)): #and icount==int(NS)):
                # Need to connect to another intersection
                    for a in self.intersectionNodes: #current intersection node
                        if(a.xpos==i and a.ypos==j):
                            index=self.intersectionNodes.index(a)
                    
                    for b in self.intersectionNodes:
                        if(b.xpos==self.NSpos[icount-1] and b.ypos==j):
                            indexb=self.intersectionNodes.index(b)
                                
                    self.intersectionNodes[index].prevNode=self.intersectionNodes[indexb]
                    self.intersectionNodes[indexb].nextNode=self.intersectionNodes[index]
                
        
                
                
                
                
                jcount+=1
            icount+=1

    def connectEWNodes(self,NS,EW):
        icount=0
        jcount=0
        # print 'NS pos',self.NSpos
        #print '\n'
        for i in self.EWpos:
            jcount=0
            for j in self.NSpos:
                if(icount==0):
                    length=i
                elif(icount==int(EW)):
                    length=i-self.EWpos[icount-1]
                    length2=self.xleng-i #2nd length that should be used to calc length from last intersection to sim wall
                else:
                    length=i-self.EWpos[icount-1]
                
                
                modnum=4.0 #min number of nodes in a street length
                modmax=20.0 #max number of nodes
                
                while(modnum<=modmax): #figure out an ideal, round number of nodes that makes the nodes equidistant
                    
                    
                    if(int(modnum)==int(modmax)): #cant devide the length by an even number. Crap. pick a rough length we want and go with it.
                        if(length>20):
                            modnum=length/10.0 #have a node every 10 feet.
                        elif(length==1):
                            modnum=1
                        elif(length<10):
                            modnum=length/2.0
                        
                        else: #need to capture where the length is between 4 and 20 and prime.
                            modnum=length/3.0 #need to decide still. Discussions may be needed.
                        
                        break
                    if(length%modnum==0 and length!=int(modnum)):
                        
                        break
                    else:
                        modnum+=1
            #print 'number of street nodes:',modnum, ' Length:',length
                if(icount==int(EW)):
                    modnum=4.0 #min number of nodes in a street length
                    modmax=20.0 #max number of nodes
                    while(modnum<=modmax): #figure out an ideal, round number of nodes that makes the nodes equidistant
                    
                    
                        if(int(modnum)==int(modmax)): #cant devide the length by an even number. Crap. pick a rough length we want and go with it.
                            if(length2>20):
                                modnum=length/10.0 #have a node every 10 feet.
                            elif(length2==1):
                                modnum=1
                            elif(length2<10):
                                modnum=length/2.0
                        
                            else: #need to capture where the length is between 4 and 20 and prime.
                                modnum=length/3.0 #need to decide still. Discussions may be needed.
                        
                                break
                        if(length2%modnum==0 and length2!=int(modnum)):
                        
                                break
                        else:
                                modnum+=1
                
                # print 'number of street nodes:',modnum, ' Length2:',length2
                if(icount<=int(EW) and modnum>1): #not the edge case
                    for k in range(int(modnum),1,-1): #create each node for each street length
                        
                        a=streetNode(0)
                        a.ypos=j-(length/modnum)*k
                        a.xpos=i
                        a.setLeng(length)

                        nextNum=len(self.streetNodes)-1 # fencepost error
                        self.streetNodes.append(a)
                        nNum=len(self.streetNodes)
                        #  print 'Next number', nextNum, 'total number:', nNum
                        
                        if(k==1 and icount==0): #node is at the edge of the sim
                            prevNd=EndNode(a) #point next node to end nodes outside of the sim
                            self.streetNodes[nextNum+1].prevNode=prevNd
                            self.streetNodes[nextNum+1].nextNode=self.streetNodes[nextNum]
                            self.streetNodes[nextNum].prevNode=self.streetNodes[nextNum+1]
                        elif(k==int(modnum)): #connect up to the correct intersection
                            for a in self.intersectionNodes:
                                if(a.xpos==j and a.ypos==i):
                                    index=self.intersectionNodes.index(a)
                            
                            self.streetNodes[nextNum+1].nextNode=self.intersectionNodes[index]#intersection
                            self.intersectionNodes[index].setRoadnode(self.streetNodes[nextNum+1])
                            self.intersectionNodes[index].setLeng(length)
                #b=self.intersectionNodes[index].getRoadnode
                # print b
                
                        elif(k==1 and icount !=0): # connect the road to the other intersection
                            for a in self.intersectionNodes:
                                if(a.xpos==i and a.ypos==self.EWpos[jcount-1]):
                                    index=self.intersectionNodes.index(a)
                            self.streetNodes[nextNum+1].nextNode=self.intersectionNodes[index]#intersection
                            self.intersectionNodes[index].setRoadnode(self.streetNodes[nextNum+1])
                            self.intersectionNodes[index].setLeng(length)
                            #b=self.intersectionNodes[index].getRoadnode
                            #  print b
                        
                        else:
                            self.streetNodes[nextNum+1].nextNode=self.streetNodes[nextNum]
                            self.streetNodes[nextNum].prevNode=self.streetNodes[nextNum+1]
                
                if(icount==int(EW) and modnum>1): # need to go rigth and left of the intersection at the furthest right intersection
                    for k in range(1,int(modnum)): #create each node for each street length
                        
                        a=streetNode(0)
                        a.ypos=j+(length2/modnum)*k
                        a.xpos=i
                        a.setLeng(length2)
                        
                        nextNum=len(self.streetNodes)-1 # fencepost error
                        self.streetNodes.append(a)
                        nNum=len(self.streetNodes)
                        
                        if(k==int(modnum)): #node is at the edge of the sim
                                nextNd=EndNode(a) #point next node to end nodes outside of the sim
                                if(k==int(modnum)): #node is at the edge of the sim
                                    nextNd=EndNode(a) #point next node to end nodes outside of the sim
                                    #self.endNodes.append(nextNd)
                                    self.streetNodes[nextNum+1].nextNode=nextNd
                                    self.streetNodes[nextNum+1].prevNode=self.streetNodes[nextNum]
                                    self.streetNodes[nextNum].nextNode=self.streetNodes[nextNum+1]
                                elif(k==1): #connect up to the correct intersection
                                    for a in self.intersectionNodes:
                                        if(a.xpos==j and a.ypos==i):
                                            index=self.intersectionNodes.index(a)
                                    
                                    ######## STOPPING POINT #####
                                    # Then copy/paste code and run thru the N/S streets.
                                    self.streetNodes[nextNum+1].prevNode=self.intersectionNodes[index]#intersection
                                    self.intersectionNodes[index].setRoadnode(self.streetNodes[nextNum+1])
                                    self.intersectionNodes[index].setLeng(length2)
                    #b=self.intersectionNodes[index].getRoadnode
                                        #print b
                                
                                else:
                                    self.streetNodes[nextNum].nextNode=self.streetNodes[nextNum+1]
                                    self.streetNodes[nextNum+1].prevNode=self.streetNodes[nextNum]
                
                
                if(modnum==1 and icount==0):
                #Need to connect the intersection to an end pont? or do we just act like its a T-section? Im thinking we act like its a T intersection
                    a=1
                
                elif(modnum==1 and icount!=0): #and icount==int(NS)):
                    # Need to connect to another intersection
                    for a in self.intersectionNodes: #current intersection node
                        if(a.xpos==j and a.ypos==i):
                            index=self.intersectionNodes.index(a)
                    
                    for b in self.intersectionNodes:
                        if(b.ypos==self.EWpos[icount-1] and b.xpos==j):
                            indexb=self.intersectionNodes.index(b)
                    
                    self.intersectionNodes[index].prevNode=self.intersectionNodes[indexb]
                    self.intersectionNodes[indexb].nextNode=self.intersectionNodes[index]


                
                
                jcount+=1
            icount+=1





