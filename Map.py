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
        #        visGrid=[[]] #probably wont be used. For Growth.
        self.Nuisance=0
        
        #random.seed(3) #PUT IN FOR DEBUGGING ONLY!!!

    def map(self, numStreets,Nuisance):
        self.Nuisance=Nuisance
        
        start_time = time.time()
        EW=math.floor(numStreets/2.0)
        NS=math.ceil(numStreets/2.0)
        
        print '\nNumber of East\West streets',EW
        print '\nNumber of North\South streets:',NS

        self.NSpos=random.sample(xrange(self.xleng),int(NS))
        #print 'NS Street ',i,' is at position ', point
        # print '\n'
       
        
        self.EWpos=random.sample(xrange(self.yleng),int(EW))

#        print 'EW Street ', j,' is at position ', point
        # print '\n'
        b=EntryNode(23)
        self.MapEntryPt=b
        
        self.NSpos.sort() # get the lists sorted into the correct order
        self.EWpos.sort()
        
        for k in self.NSpos: #create all of the intersection nodes
            for l in self.EWpos:
                a=intersecNode(42,self.Nuisance)
                a.setXY(l,k)
                self.intersectionNodes.append(a)
        for a in self.NSpos:
            print "NS Street at:", a
        for a in self.EWpos:
            print "EW Street at:", a
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
        EWfcount=0
        NSfcount=0
        # print 'NS pos',self.NSpos
        #print '\n'
        for NSf in self.NSpos:
            NSfcount=0
            for EWf in self.EWpos:
                if(EWfcount==0):
                    length=EWf
                elif(EWfcount==int(EW)):
                    length=EWf-self.EWpos[EWfcount-1]
                    length2=self.xleng-EWf#2nd length that should be used to calc length from last intersection to sim wall
                else:
                    length=EWf-self.EWpos[EWfcount-1]
                
                
                modnum=4.0 #min number of nodes in a street length
                modmax=20.0 #max number of nodes
                
                while(modnum<=modmax): #figure out an ideal, round number of nodes that makes the nodes equidistant
                    
                    
                    if(int(modnum)==int(modmax)): #cant devide the length by an even number. Crap. pick a rough length we want and go with it.
                        if(length>20):
                            modnum=length/10.0 #have a node every 10 m.
                        elif(length==1):
                            modnum=1
                        elif(length<10):
                            modnum=length/2.0

                        else: #need to capture where the length is between 4 and 20 and prime.
                            modnum=length/3.0
                        
                        break
                    if(length%modnum==0 and length!=int(modnum)):
                        
                        break
                    else:
                        modnum+=1
            #print 'number of street nodes:',modnum, ' Length:', length,
                if(EWfcount==int(EW)):
                    modnum=4.0 #min number of nodes in a street length
                    modmax=20.0 #max number of nodes
                    while(modnum<=modmax): #figure out an ideal, round number of nodes that makes the nodes equidistant
                    
                    
                        if(int(modnum)==int(modmax)): #cant devide the length by an even number. Crap. pick a rough length we want and go with it.
                            if(length2>20):
                                modnum=length/10.0 #have a node every 10 m.
                            elif(length2==1):
                                modnum=1
                            elif(length2<10):
                                modnum=length/2.0
                        
                            else: #need to capture where the length is between 4 and 20 and prime.
                                    modnum=length/3.0
                        
                                    break
                        if(length2%modnum==0 and length2!=int(modnum)):
                        
                            break
                        else:
                            modnum+=1
        #print 'number of street nodes:',modnum, ' Length2:', length2,
                        #print 'number of street nodes:',modnum, ' Length:', length,
                if(EWfcount<=int(EW) and modnum>1): #not the edge case
                    for k in range(int(modnum),0,-1): #create each node for each street length
                        
                        a=streetNode(44,self.Nuisance)
                        a.xpos=EWf-(length/modnum)*k
                        a.ypos=NSf
                        a.setLeng(length)
                     
                        nextNum=len(self.streetNodes)-1 # fencepost error
                        self.streetNodes.append(a)
                        nNum=len(self.streetNodes)
                        #  print 'Next number', nextNum, 'total number:', nNum
                        
                        if(k==1 and EWfcount==0): #node is at the edge of the sim
                            prevNd=EndNode(a,self.Nuisance) #point next node to end nodes outside of the sim
                            self.streetNodes[nextNum+1].prevNode=prevNd
                            self.streetNodes[nextNum+1].nextNode=self.streetNodes[nextNum]
                            self.streetNodes[nextNum].prevNode=self.streetNodes[nextNum+1]
                        elif(k==int(modnum)): #connect up to the correct intersection
                            for newNode in self.intersectionNodes:
                                if(newNode.xpos==EWf and newNode.ypos==NSf):
                                    index=self.intersectionNodes.index(newNode)
                        
                            self.streetNodes[nextNum+1].nextNode=self.intersectionNodes[index]#intersection
                            self.intersectionNodes[index].setRoadnode(self.streetNodes[nextNum+1])
                            self.intersectionNodes[index].setLeng(length)
                                #b=self.intersectionNodes[index].getRoadnode
                                # print b
                
                        elif(k==1 and EWfcount !=0): # connect the road to the other intersection
                            for a in self.intersectionNodes:
                                if(a.xpos==self.EWpos[EWfcount-1] and a.ypos==NSf):
                                    index=self.intersectionNodes.index(a)
                            self.streetNodes[nextNum+1].nextNode=self.intersectionNodes[index]#intersection
                            self.intersectionNodes[index].setRoadnode(self.streetNodes[nextNum+1])
                            self.intersectionNodes[index].setLeng(length)
                            #  b=self.intersectionNodes[index].getRoadnode
                            #           print b
                        
                        else:
                            self.streetNodes[nextNum+1].nextNode=self.streetNodes[nextNum]
                            self.streetNodes[nextNum].prevNode=self.streetNodes[nextNum+1]
                
                if(EWfcount==int(EW) and modnum>1): # need to go rigth and left of the intersection at the furthest right intersection
                    for k in range(0,int(modnum)): #create each node for each street length
                        
                        a=streetNode(67,self.Nuisance)
                        a.xpos=EWf+(length2/modnum)*k
                        a.ypos=NSf
                        a.setLeng(length2)
#                        if(a.xpos<0):
#                                print "x,y pos of node", a.xpos,",",a.ypos, "NSf pos",NSf,"leng",(length/modnum)*k
                        nextNum=len(self.streetNodes)-1 # fencepost error
                        self.streetNodes.append(a)
                        nNum=len(self.streetNodes)
                        
                        if(k==int(modnum)): #node is at the edge of the sim
                                nextNd=EndNode(a,self.Nuisance) #point next node to end nodes outside of the sim
                                if(k==int(modnum)): #node is at the edge of the sim
                                    nextNd=EndNode(a,self.Nuisance) #point next node to end nodes outside of the sim
                                    nextNd.mapNode=self.streetNodes[nextNum+1]
                                    # self.endNodes.append(nextNd)
                                    self.streetNodes[nextNum+1].nextNode=nextNd
                                    self.streetNodes[nextNum+1].prevNode=self.streetNodes[nextNum]
                                    self.streetNodes[nextNum].nextNode=self.streetNodes[nextNum+1]
                                elif(k==1): #connect up to the correct intersection
                                    for a in self.intersectionNodes:
                                        if(a.xpos==EWf and a.ypos==NSf):
                                            index=self.intersectionNodes.index(a)
                                    
                                  
                                    self.streetNodes[nextNum+1].prevNode=self.intersectionNodes[index]#intersection
                                    self.intersectionNodes[index].setRoadnode(self.streetNodes[nextNum+1])
                                    self.intersectionNodes[index].setLeng(length2)
                    #b=self.intersectionNodes[index].getRoadnode
                    # print b
                    
                                else:
                                    self.streetNodes[nextNum].nextNode=self.streetNodes[nextNum+1]
                                    self.streetNodes[nextNum+1].prevNode=self.streetNodes[nextNum]
                if(modnum==1 and EWfcount==0):
                #we act like its a T intersection
                    a=1
                elif(modnum==1 and EWfcount!=int(EW)): #and EWfcount==int(NS)):
                # Need to connect to another intersection
                    for a in self.intersectionNodes: #current intersection node
                        if(a.xpos==EWf and a.ypos==NSf):
                            index=self.intersectionNodes.index(a)
                    
                    for b in self.intersectionNodes:
                        if(b.xpos==self.EWpos[EWfcount-1] and b.ypos==NSf):
                            indexb=self.intersectionNodes.index(b)
                                
                    self.intersectionNodes[index].prevNode=self.intersectionNodes[indexb]
                    self.intersectionNodes[indexb].nextNode=self.intersectionNodes[index]
                
        
                
                
                
                
                NSfcount+=1
            EWfcount+=1

    def connectEWNodes(self,NS,EW):
        EWfcount=0
        NSfcount=0
        # print 'NS pos',self.NSpos
        #print '\n'
        for EWf in self.EWpos:
            NSfcount=0
            for NSf in self.NSpos:
                if(NSfcount==0):
                    length=NSf
                elif(NSfcount==int(NS)):
                    length=NSf-self.NSpos[NSfcount-1]
                    length2=self.yleng-NSf#2nd length that should be used to calc length from last intersection to sim wall
                else:
                    length=NSf-self.NSpos[NSfcount-1]
                
                
                modnum=4.0 #min number of nodes in a street length
                modmax=20.0 #max number of nodes
                
                while(modnum<=modmax): #figure out an ideal, round number of nodes that makes the nodes equidistant
                    
                    
                    if(int(modnum)==int(modmax)): #cant devide the length by an even number. Crap. pick a rough length we want and go with it.
                        if(length>20):
                            modnum=length/10.0 #have a node every 10 m.
                        elif(length==1):
                            modnum=1
                        elif(length<10):
                            modnum=length/2.0
                        
                        else: #need to capture where the length is between 4 and 20 and prime.
                            modnum=length/3.0
                        
                        break
                    if(length%modnum==0 and length!=int(modnum)):
                        
                        break
                    else:
                        modnum+=1
            #print 'number of street nodes:',modnum, ' Length:',length
                if(NSfcount==int(NS)):
                    modnum=4.0 #min number of nodes in a street length
                    modmax=20.0 #max number of nodes
                    while(modnum<=modmax): #figure out an ideal, round number of nodes that makes the nodes equidistant
                    
                    
                        if(int(modnum)==int(modmax)): #cant devide the length by an even number. Crap. pick a rough length we want and go with it.
                            if(length2>20):
                                modnum=length/10.0 #have a node every 10 m.
                            elif(length2==1):
                                modnum=1
                            elif(length2<10):
                                modnum=length/2.0
                        
                            else: #need to capture where the length is between 4 and 20 and prime.
                                modnum=length/3.0
                        
                                break
                        if(length2%modnum==0 and length2!=int(modnum)):
                        
                                break
                        else:
                                modnum+=1
                
                # print 'number of street nodes:',modnum, ' Length2:',length2
                if(NSfcount<=int(NS) and modnum>1): #not the edge case
                    for k in range(int(modnum),0,-1): #create each node for each street length
                        
                        a=streetNode(89,self.Nuisance)
                        a.ypos=NSf-(length/modnum)*k
                        a.xpos=EWf
                        a.setLeng(length)
                        

                        nextNum=len(self.streetNodes)-1 # fencepost error
                        self.streetNodes.append(a)
                        nNum=len(self.streetNodes)-1
                        
                        #  print 'Next number', nextNum, 'total number:', nNum
                        
                        if(NSfcount==0): #node is at the edge of the sim
                            if(k==1):
                                prevNd=EndNode(self.streetNodes[nextNum+1],self.Nuisance) #point next node to end nodes outside of the sim
                                self.streetNodes[nextNum+1].prevNode=prevNd
                                self.streetNodes[nextNum+1].nextNode=self.streetNodes[nextNum]
                                self.streetNodes[nextNum].prevNode=self.streetNodes[nextNum+1]
                        
                        elif(k==int(modnum)): #connect up to the correct intersection
                            for a in self.intersectionNodes:
                                if(a.xpos==EWf and a.ypos==NSf):
                                    index=self.intersectionNodes.index(a)
                        
                            self.streetNodes[nextNum+1].nextNode=self.intersectionNodes[index]#intersection
                            
                            self.intersectionNodes[index].setRoadnode(self.streetNodes[nextNum+1])
                            self.intersectionNodes[index].setLeng(length)
                #b=self.intersectionNodes[index].getRoadnode
                # print b
                
                        elif(k==1): # connect the road to the other intersection
                            for a in self.intersectionNodes:
                                if(a.xpos==EWf and a.ypos==self.NSpos[NSfcount-1]):
                                    index=self.intersectionNodes.index(a)
                                    if(nextNum==6879):
                                        print index

                            self.streetNodes[nextNum].prevNode=self.streetNodes[nextNum+1]
                            self.streetNodes[nextNum+1].prevNode=self.intersectionNodes[index]#intersection
                            self.streetNodes[nextNum+1].nextNode=self.streetNodes[nextNum]


                            
                            self.intersectionNodes[index].setRoadnode(self.streetNodes[nextNum+1])
                            self.intersectionNodes[index].setLeng(length)
                            #b=self.intersectionNodes[index].getRoadnode
                            #  print b
                        
                        else:
                            self.streetNodes[nextNum].prevNode=self.streetNodes[nextNum+1]
                            
                            self.streetNodes[nextNum+1].nextNode=self.streetNodes[nextNum]
                        
                        #print "k",k,"nextNum",nextNum,self.streetNodes[nextNum],",",self.streetNodes[nextNum].prevNode,",",self.streetNodes[nextNum].nextNode
                        
                        
                        
#                        if(self.streetNodes[nextNum].prevNode==89 ):
# 
#                            print "k",k, "modnum", modnum, "nextnum",nextNum,"NSfcount",NSfcount, self.streetNodes[nextNum].prevNode
#                            print EWf,NSf,NS,EW, EWfcount

                if(NSfcount==int(NS) and modnum>1): # need to go rigth and left of the intersection at the furthest right intersection
                    for k in range(0,int(modnum)): #create each node for each street length
                        
                        a=streetNode(5280,self.Nuisance)
                        a.ypos=NSf+(length2/modnum)*k
                        a.xpos=EWf
                        a.setLeng(length2)
                        
                        nextNum=len(self.streetNodes)-1 # fencepost error
                        self.streetNodes.append(a)
                        nNum=len(self.streetNodes)
                        
                        if(k==int(modnum)): #node is at the edge of the sim
                                
                                if(k==int(modnum)): #node is at the edge of the sim
                                    nextNd=EndNode(a,self.Nuisance) #point next node to end nodes outside of the sim
                                    #self.endNodes.append(nextNd)
                                    nextNd.setNode(self.streetNodes[nextNum])
                                    self.streetNodes[nextNum+1].nextNode=nextNd
                                    self.streetNodes[nextNum+1].prevNode=self.streetNodes[nextNum]
                                    self.streetNodes[nextNum].nextNode=self.streetNodes[nextNum+1]
                                elif(k==1): #connect up to the correct intersection
                                    for a in self.intersectionNodes:
                                        if(a.xpos==EWf and a.ypos==NSf):
                                            index=self.intersectionNodes.index(a)
                                    
                                 
                                    self.streetNodes[nextNum+1].prevNode=self.intersectionNodes[index]#intersection
                                    self.intersectionNodes[index].setRoadnode(self.streetNodes[nextNum+1])
                                    self.intersectionNodes[index].setLeng(length2)
                    #b=self.intersectionNodes[index].getRoadnode
                                        #print b
                                
                                else:
                                    self.streetNodes[nextNum].nextNode=self.streetNodes[nextNum+1]
                                    self.streetNodes[nextNum+1].prevNode=self.streetNodes[nextNum]
                
                
                if(modnum==1 and NSfcount==0):

                    pass
                
                elif(modnum==1 and NSfcount!=0): #and EWfcount==int(NS)):
                    # Need to connect to another intersection
                    for a in self.intersectionNodes: #current intersection node
                        if(a.xpos==EWf and a.ypos==NSf):
                            index=self.intersectionNodes.index(a)
                    
                    for b in self.intersectionNodes:
                        if(b.ypos==self.NSpos[NSfcount-1] and b.xpos==EWf):
                            indexb=self.intersectionNodes.index(b)
                    
                    self.intersectionNodes[index].prevNode=self.intersectionNodes[indexb]
                    self.intersectionNodes[indexb].nextNode=self.intersectionNodes[index]


                
                
                NSfcount+=1
            EWfcount+=1


    def RandNode(self):
        RDvINT=random.random()
        if(RDvINT>.5): # use a road
            moo=len(self.streetNodes)
            mpnode=random.randint(0,moo-1)
            return self.streetNodes[mpnode]
        else:
            moo=len(self.intersectionNodes)
            mpnode=random.randint(0,moo-1)
            return self.intersectionNodes[mpnode]

