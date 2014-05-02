import sys
import random

class Target:
    #"Target"
    #node = predicted location (random variate)
    #intel = strength of intelligence (random variate)
    #loitertime = idle time (random variate)
    #stay = probability of loiter at any new node

    def __init__(self,obj):
        # initialize parameters for target
        self.loitertime= random.uniform(60,600) #loiter at first node for 1-10 min, based on survey data for length of average face-to-face conversation
        self.node=obj #pass the target the pointer to the map node.
        self.stay=.3 #probability a person will loiter on a node
        self.intelVal=1 #set at one for now, but will likely be a discrete distribution
        self.intelPriority=1
        
        self.ObsTime=90 # set the default time for sucessful tracking at 90sec,
        self.goalTime=100
        self.speed=1 #m/s for default
        self.transitTime=10
        self.loiterbit=1
        self.timeOnNode=0
        
        self.ID=0
        self.Type='Pedestrian'
        self.Stealth=0
        self.ActTracTime=0
        self.trackAttempts=0
    
        
    def movement(self):
# step1: check what kind of node. 0= street, 1= intersection, 2=entry node, 3=End node
# Can only move on street and road nodes. If in entry or end, remove self from sim. Send message to caoc
        if(self.node.nodeType==2):
            length=math.sqrt((self.node.xpos-self.node.nextNode.xpos)**2 +(self.node.ypos-self.node.nextNode.ypos)**2)
            self.node=self.node.nextNode # move onto the map
            self.transitTime=int(length/self.speed)
        
        elif(self.node.nodeType==3):
            print"At an END NODE!!"
            #Treating as a culd-a-sac
            self.transitTime=int(self.node.nextNode.length/self.speed)
            self.node=self.node.nextNode
        
                       
        elif(self.node.nodeType==0): # can only move forward, back, or stay in current node.
            stayHere=random.uniform(0,1) #if stayHere<=self.stay, loiter at the current node.
            if(self.stay>=stayHere):
                self.transitTime=int(self.node.length/self.speed)#keeping constant time blocks.
            
            else:
                nextPrev=.5 # equal chance of going right or left.Probably will want to change this
                if(nextPrev<random.uniform(0,1)):
                    self.transitTime=int(self.node.length/self.speed)
                    self.node=self.node.nextNode
            
                    print "Going Right!"
                else:
                    self.transitTime=int(self.node.length/self.speed)
                    self.node=self.node.prevNode
                    
                    print "Going Left!"
        else: #its an intersection. Randomly choose a new direction. We will not loiter in an intersection node.
            dir=random.uniform(0,1)
            #print "At an intersection"
            num=len(self.node.Nodes)
            #print "Num",num
            for a in range(num):
                print "a:",a,"dir:",dir, "if val:",((1./num)*(a+1))
                if(dir<((1.0/num)*(a+1))):
                    
                      if(self.node.Nodes[a].nodeType==1): #Going to another intersection.
                          length=math.sqrt((self.node.xpos-self.node.Nodes[a].xpos)**2 +(self.node.ypos-self.node.Nodes[a].ypos))
                          self.node=self.node.Nodes[a]
                          self.transitTime=int(self.node.length/self.speed) #use the new node length to calc dist and time.
                      else:
                          self.node=self.node.Nodes[a]
                          self.transitTime=int(self.node.length/self.speed) #use the new node length to calc dist and time.
                      break
        print "Moved to:",self.node.xpos,",",self.node.ypos," Node type:",self.node.nodeType
            
            
    def setObsTime(self,time):
        self.ObsTime=time
