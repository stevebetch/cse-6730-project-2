import sys
from LogicalProcess import *
from Map import GenMap
from nodes import EntryNode
from multiprocessing import Lock
import random
from Message import *

class Drone (LogicalProcess):

    # instance argument list
    #id - unique id of drone
    #controller - the simulation executive
    #droneType - descriptive

    def __init__(self, id, droneType, caoc):
        LogicalProcess.__init__(self)
        self.droneType = droneType
        self.caoc = caoc
        self.id = id
     
        self.LocalSimTime=0 #current simulation time for the drone
        
        self.MaintenanceActionTime=144000 #how much time until we need to land for maintainance (40 hr engine overhaul (yes andrew it should be 100hr), ect)
        self.Joker=0 #how much time we have to search
        self.jokerflag=0
        
        self.Bingo=0 #time until we have to leave the map
        
        self.DistEntry=0.0 #distance from the entry node

        self.FlightSpeed=random.randint(50,200)#Random flight speed of the drone, ft/s? something/s
        self.DroneLegs=28800 # Assuming the drone has 8hr legs (8*3600=28800 sec) We can change this later if we want

        self.xpos=0 #current x location
        self.ypos=0 #current y location

        self.EntNode=[]
        self.currentNode=[]

        self.target=[]
        self.detectBool=0 # Boolian used for detection logic
        self.sNeedBool=1 #boolian to determine if we need to activate the search logic.
        self.timeOnNode=0 #how long have we been on the current node?
        self.nodeTime=0 #how long should it take the target to traverse the node?
        self.searchTime=20 #It takes 20 seconds to search the area.
    
    def __call__(self,obj):
        self.run(obj)
    
    def setController(self, controller):
        self.controller = controller
            
    def handleMessage(self, msg):
        # determine message type and process accordingly
        pass
    
    def start(self,mapObj):
        # Begin process of selecting target from CAOC priority queue, tracking, check when refueling needed, etc.
        # Begin at entry node. aka, only pass drone the entry node!!!
        self.setEntry(mapObj)
        self.currentNode=mapObj #the only time we directly set the current node.
        self.getNewTargetFromCAOC()
        self.LocalSimTime=0 ############## HOW ARE WE SETTING THIS??? ############
    
        while(1):
    # Check fuel before anything else!!
            if(not(self.jokerflag)): #joker not set yet. can search for targets
                if(not(detectBool)): #dont have a detection
                    self.search()
                    self.detection()
                else: #we have a detection! woooo
                    self.detection()

            else: # joker flag set.
                if(not(detectBool)):
                    #dont have an active detection. RTB.
                    self.ReturnToBase()
                else: # detection flag set. We have a target in active track.
                    if(self.Bingo>0): #we still have fuel!
                    # We have fuel and can still start tracking.
                        self.detection()
                        if(self.sNeedBool):# need to search for the target.
                            self.search()
                            self.detection()
                    else:
                        self.ReturnToBase()
                    
                    
    
    def setTarget(self,obj):
        # This function will take in the target object and assign it to the drone. Looks like it will not be used. Propose we drop it.
        self.target=obj
    
    def updateTime(self,timeDif): # timeDif= time delta. How much you want to update the clock by,
        #Update the timers with each timestep
        #timeDif=newDroneSimTime-self.LocalSimTime
        self.Joker-=timeDif
        if(self.Joker<=0):
            self.jokerflag=1
        self.Bingo-=timeDif
        self.MatenanceActionTime-=timeDif
        self.LocalSimTime+=timeDif
        self.timeOnNode+=timeDif
        if(self.timeOnNode>=self.target.transitTime): #The target has had enough time to move.
            if(self.target.loiterbit):
                self.target.loitertime-=self.timeOnNode
                self.timeOnNode=0
                if(self.target.loitertime<0):
                    self.timeOnNode=self.target.loitertime*-1
                    self.target.loiterbit=0
            else:
                self.target.movement()
                self.timeOnNode=self.timeOnNode-self.target.transitTime
                    
        #print "\nNew Joker:", self.Joker, "New Bingo:",self.Bingo
        if(self.Bingo<=0): # Reached bingo. need to RTB.
            self.ReturnToBase()

    def setJokerBingo(self):
    # Call this funtion after the drone returns from a maintainance action, refuleing or at the start of the sim
            if(self.DroneLegs<self.MatenanceActionTime):#We have less fuel time than maintainance time
                self.Joker=self.DroneLegs*0.8 # Joker is set at 6 hrs 24 min. Ensures we have enough time (48 min) to track another target before bingo
                
                self.Bingo=self.DroneLegs*0.9 # 45 minutes flight time to return to base
            
            else: #assuming we have more than 4 hours of flight time. If less than 4 hours, we should be premptively performing maintainance
                self.Joker=self.MatenanceActionTime - 7200 # 2 hour joker
                self.Bingo=self.MatenanceActionTime - 3600 # 1 hour bingo

            print "\nJoker set to:", self.Joker, "Bingo set to:",self.Bingo


    def resetMaintenanceTimer(self):
        self.MaintenanceActionTime=144000

    def setEntry(self,obj):
        self.EntryNode=obj
        #print "Map entry at:" , self.EntryNode.xpos,",",self.EntryNode.ypos

    def updateCurNode(self,obj):
        oldnode=self.currentNode
        self.currentNode=obj #may not be needed, but may be expanded later if needed.
        self.xpos=self.currentNode.xpos
        self.ypos=self.currentNode.ypos
        if(self.currentNode.nodeType==0):
            flightTime=int(self.currentNode.length/self.FlightSpeed)
        elif(self.current.nodeType==1):
            #intersection. Use old node length
            if(oldnode.nodeType==1 or oldnode.nodeType==2): #either an intersection or entry node
                length=math.sqrt((self.xpos-oldnode.xpos)**2 +(self.ypos-oldnode.ypos)**2)
            elif(oldnode.nodeType==0):
                #the old node was a street. use that distance.
                length=oldnode.length
            flightTime=int(length/self.FlightSpeed)
            
        elif(self.currentNode==3): #end node. Only attached to streets.
            length=oldnode.length
            flightTime=int(length/self.FlightSpeed)
        updateTime(flightTime)
    

    def getNewTargetFromCAOC(self):
        lock = Lock()
        self.target=self.caoc.getNextTarget(lock, None, None)
        del lock
    
    def run(self):
        # Begin process of selecting target from CAOC priority queue, tracking, check when refueling needed, etc.
        print('Drone process running')    


    def probTest(self,probVal):
        #This function will be called to determine if we get a positive detection on the target
        testprob=random.uniform(0,1)
        if(probVal<=testprob):
            # Weve got a positive hit!
            return 1
        else:
            return 0


    def detection(self):
        # Begin by seeing if we already have a track
        if(self.detectBool==1): #we have a track!
            # Check to see if we are on the same node as the target.
            if(self.xpos!=self.target.xpos or self.ypos!=self.target.ypos): # tracking, but not looking at the right node
                self.updateCurNode(self.target.currentNode)
                #We are on a new node. Need to roll the dice to see if we keep a track.
            if(self.probTest(self.node.Trackprob)): #if we maintain track
                    self.detectBool=1 #reaffirming the value
                    self.sNeedBool=0
                    
            else:
                    self.detectBool=0
                    self.sNeedBool=1
        else: # we dont have a track yet.
            if(self.xpos!=self.target.xpos or self.ypos!=self.target.ypos):
                    self.detectBool=0 #we arnt even looking at the right node!
                    self.sNeedBool=1
            elif(self.probTest(self.node.Trackprob)): #looking at the right node, have a detection!
                    self.detectBool=1 #reaffirming the value
                    self.sNeedBool=0

            else: #looking at the right node, but no detection
                self.detectBool=0
                self.sNeedBool=0
        self.updateTime(self.searchTime) # the cost of doing one search operation
            
            
    def search(self): # this function needs a lot of work. How are we actually doing the search method?!?
        if(self.xpos!=self.target.xpos or self.ypos!=self.target.ypos): # we know we arnt looking at the right node.
            #Assume our intel came with a direction of movement and speed
            choice=random.random()
            if(choice>=.2): #80% chance we choose the correct direction. Why 80? I have no clue.
                if(self.currentNode.nodeType==0): #curent node is a street
                    if(self.target.xpos>self.xpos):
                        self.updateCurNode(self.currentNode.nextNode)
                        # Only need flight time here. We will have to be more elegant when actually tracking.
                    else:
                        self.updateCurNode(self.currentNode.prevNode)
                elif(self.currentNode.nodeType==1): # an intersection.
                    for i in self.currentNode.nodes:
                        if(self.currentNode.ypos==i.ypos):
                            if(self.target.xpos>self.currentNode.xpos and i.xpos>self.currentNode.xpos):
                            #Mouth full.... but correct dir.
                                self.updateCurNode(i)
                                break
                            elif(self.target.xpos<self.currentNode.xpos and i.xpos<self.currentNode.xpos):
                                self.updateCurNode(i)
                                break
                        elif(self.currentNode.xpos==i.xpos):
                            if(self.target.ypos>self.currentNode.ypos and i.ypos>self.currentNode.ypos):
                                #Mouth full.... but correct dir.
                                self.updateCurNode(i)
                                break
                            elif(self.target.ypos<self.currentNode.ypos and i.ypos<self.currentNode.ypos):
                                self.updateCurNode(i)
                                break
            else:
                if(self.currentNode.nodeType==0): #curent node is a street
                    if(self.target.xpos>self.xpos):
                        self.updateCurNode(self.currentNode.prevNode)
                    # Only need flight time here. We will have to be more elegant when actually tracking.
                    else:
                        self.updateCurNode(self.currentNode.NextNode)
                elif(self.currentNode.nodeType==1): # an intersection.
                    for i in self.currentNode.nodes:
                        if(self.currentNode.ypos==i.ypos):
                            if(self.target.xpos>self.currentNode.xpos and i.xpos<self.currentNode.xpos):
                                #Mouth full.... but correct dir.
                                self.updateCurNode(i)
                                break
                            elif(self.target.xpos<self.currentNode.xpos and i.xpos>self.currentNode.xpos):
                                self.updateCurNode(i)
                                break
                        elif(self.currentNode.xpos==i.xpos):
                            if(self.target.ypos>self.currentNode.ypos and i.ypos<self.currentNode.ypos):
                                #Mouth full.... but correct dir.
                                self.updateCurNode(i)
                                break
                            elif(self.target.ypos<self.currentNode.ypos and i.ypos>self.currentNode.ypos):
                                self.updateCurNode(i)
                                break


    def ReturnToBase(self):
    #cant have any new assignments durning this time. May need to look at the messages to reject taskers.
    # need to delete target, return it to the queue.
        retTgt=Message(getNextMessageID(),2,self.target,self.id,self.caoc.id,self.LocalSimTime) #THIS IS AN INCORRECT CALL!!! HELP!!!!
        
        self.DistEntry=math.sqrt((self.xpos-self.EntNode.xpos)**2 +(self.ypos-self.EntNode.ypos)**2)
        timeToentry=int(self.DistEntry/self.FlightSpeed)
        self.updateTime(timeToentry) #update sim time
        
        if(self.MaintenanceActionTime<=14400): #the drone is within 4 hours of needing prevenative ma
            self.resetMaintenanceTimer()
            self.updateTime(18000) #5 hours for maintenance. IS THIS REASONABLE?
        self.setJokerBingo()
        self.updateCurNode(self.EntNode)

    def flyTotgt(self,tgtx,tgty):
    # code to move the drone from the current location to the target's intel location. assuming the intel location is within 1 node of actual.
        distTgt=math.sqrt((self.xpos-tgtx)**2 +(self.ypos-tgty)**2) #distance to the intel location x,y
        TOT=int(distTgt/self.FlightSpeed)
        self.updateTime(TOT)




