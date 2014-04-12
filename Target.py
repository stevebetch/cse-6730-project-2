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
        self.loitertime= random.uniform(180,600) #loiter at first node for 2-10 min
        self.node=obj #pass the target the pointer to the map node.
        self.stay=.3 #probability a person will loiter on a node
        self.intel=1 #set at one for now, but will likely be a discrete distribution
        self.ObsTime=90 # set the default time for sucessful tracking at 90sec,
        self.speed=random.randint(10,20) #ft/s
        self.transitTime=0
        
    def movement(self):
        random.seed() # this is for debugging only. Should be removed in the final code.
# step1: check what kind of node. 0= street, 1= intersection, 2=entry node, 3=End node
# Can only move on street and road nodes. If in entry or end, remove self from sim. Send message to caoc
        if(self.node.nodeType==2):
            length=math.sqrt((self.node.xpos-self.node.nextNode.xpos)**2 +(self.node.ypos-self.node.nextNode.ypos)**2)
            self.node=self.node.nextNode # move onto the map
            self.transitTime=int(length/self.speed)
        
        elif(self.node.nodeType==3):
            return 999 #need to figure out what to do in this case.
                       #Probs will delete the target.
                       
                       
        elif(self.node.nodeType==0): # can only move forward, back, or stay in current node.
            stayHere=random.uniform(0,1) #if stayHere<=self.stay, loiter at the current node.
            if(self.stay>=stayHere):
                self.transitTime=int(self.node.length/self.speed)#keeping constant time blocks.
                return
            else:
                nextPrev=random.uniform(0,.5) # equal chance of going right or left.Probably will want to change this
                if(nextPrev<random.uniform(0,1)):
                    self.node=self.node.nextNode
                    self.transitTime=int(self.node.length/self.speed)
                    #print "Going Right!"
                else:
                    self.node=self.node.prevNode
                    self.transitTime=int(self.node.length/self.speed)
                #   print "Going Left!"
        else: #its an intersection. Randomly choose a new direction. We will not loiter in an intersection node.
            dir=random.uniform(0,1)
            #print "At an intersection"
            num=len(self.node.Nodes)
            #print "Num",num
            for a in range(num):
                #   print "a:",a,"dir:",dir, "if val:",((1./num)*(a+1))
                if(dir<((1.0/num)*(a+1))):
                      self.node=self.node.Nodes[a]
                      self.transitTime=int(self.node.length/self.speed) #use the new node length to calc dist and time.
                      break

    def setObsTime(self,time):
        self.ObsTime=time
