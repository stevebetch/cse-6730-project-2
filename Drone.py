import sys
from LogicalProcess import *
from Map import GenMap
from nodes import EntryNode
from multiprocessing import Lock
from state import *
import random
from Message import *

import Pyro4

class Drone (LogicalProcess):

    # instance argument list
    #id - unique id of drone
    #droneType - descriptive

    def __init__(self, uid, droneType,heuristic):
        self.uid = uid
        self.heuristic=heuristic
        LogicalProcess.__init__(self)
        self.droneType = droneType

        self.LocalSimTime=0 #current simulation time for the drone

        self.MaintenanceActionTime=75600 #MTBF 21 hrs based on DoD study, here in seconds
        self.Joker=0 #how much time we have to search
        self.jokerflag=0

        self.Bingo=0 #time until we have to leave the map

        self.DistEntry=0.0 #distance from the entry node

        self.FlightSpeed=random.randint(10,50)#Random flight speed of the drone, m/s
        self.DroneLegs=41760 #11.6hrs = 41760s max endurance, 5.8hrs = 20880s median endurance

        self.xpos=0 #current x location
        self.ypos=0 #current y location

        self.EntNode=[]
        self.currentNode=[]

        self.target=42
        self.detectBool=0 # Boolian used for detection logic
        self.sNeedBool=1 #boolian to determine if we need to activate the search logic.
        self.timeOnNode=0 #how long have we been on the current node?
        self.nodeTime=0 #how long should it take the target to traverse the node?
        self.searchTime=60 #It takes 20 seconds to search the area.
        self.searchdwell=0
        self.TarTime=0
        self.startNode=[]
            
        self.droneRadLim= 50 # The search radius is only 50 m
    
    def __call__(self, mapObj):
        self.run(mapObj)
        
    def getCurrentState(self):
        return None        

    # Mark: SHOULD MOVE THIS TO run() METHOD OR CALL IT FROM run() METHOD
    #Stephan: moved old run() up here and renamed start() to run()
    
    def run(self,mapObj):
        # Begin process of selecting target from CAOC priority queue, tracking, check when refueling needed, etc.
        print('Drone process running')
        
        self.saveState()

        
        # Get the message queue objects from Pyro
        nameserver = Pyro4.locateNS()
        controllerInQ_uri = nameserver.lookup('inputqueue.controller')
        self.controllerInQ = Pyro4.Proxy(controllerInQ_uri)
        caocInQ_uri = nameserver.lookup('inputqueue.caoc')
        self.caocInQ = Pyro4.Proxy(caocInQ_uri)
        imintInQ_uri = nameserver.lookup('inputqueue.imint')
        self.imintInQ = Pyro4.Proxy(imintInQ_uri)
        droneInQs_uri = nameserver.lookup('inputqueue.drones')
        self.droneInQs = Pyro4.Proxy(droneInQs_uri)
        self.inputQueue = self.droneInQs.getInputQueue(self.uid)

        # Event loop iteration
        #while True:
            #print 'Drone %d event loop iteration' % (self.uid)
            #msg = self.getNextMessage()
        #if msg:
            #self.handleMessage(msg)
        # Begin process of selecting target from CAOC priority queue, tracking, check when refueling needed, etc.
        # Begin at entry node. aka, only pass drone the entry node!!!
        
        self.setEntry(mapObj) #MUST PASS THE ENTRY NODE!!! (map.MapEntryPt)
        self.currentNode=mapObj #the only time we directly set the current node.
        self.LocalSimTime=0
        
        
        if(self.heuristic==1): #Naive heuristic
            while(1):

                if(self.target==42): #NO TARGET IN QUEUE
                    self.getNewTgt()
                
         # Check fuel before anything else!!
                if(not(self.jokerflag)): #joker not set yet. can search for targets
                    if(not(self.detectBool)): #dont have a detection
                        self.search()
                        self.detection()
                        self.searchdwell+=self.searchTime
                    
                    else: #we have a detection! woooo
                        self.detection()
                        self.searchdwell=0
            
                else: # joker flag set.
                    if(not(detectBool)):
                        #dont have an active detection. RTB.
                        self.ReturnToBase()
                    else: # detection flag set. We have a target in active track.
                        if(self.Bingo>0): #we still have fuel!
                        # We have fuel and can still start tracking.
                            self.detection()
                        else:
                            self.ReturnToBase()
            
                if(self.TarTime>=self.target.ObsTime):# Observation time is larger than needed time. Target satisfied.
                    self.SendIMINT()
                    self.removeTgt()
                    self.getNewTgt()
    ################################################
    
        elif(self.heuristic==2): # Local Heuristic
            while(1):
                
                if(self.target==42): #NO TARGET IN QUEUE
                    self.getNewTgt()
                
                # Check fuel before anything else!!
                if(not(self.jokerflag)): #joker not set yet. can search for targets
                    if(not(self.detectBool)): #dont have a detection
                        self.search()
                        self.detection()
                        self.searchdwell+=self.searchTime
                    
                    else: #we have a detection! woooo
                        self.detection()
                        self.searchdwell=0
                
                
                else: # joker flag set.
                    if(not(detectBool)):
                        #dont have an active detection. RTB.
                        self.ReturnToBase()
                    else: # detection flag set. We have a target in active track.
                        if(self.Bingo>0): #we still have fuel!
                            # We have fuel and can still start tracking.
                            self.detection()
                        else:
                            self.ReturnToBase()

                droneRad=math.sqrt((self.xpos-self.node.xpos)**2+(self.ypos-self.node.ypos)**2)
                                    
                if(droneRad>self.droneRadLim): # searched for the target within the local area
                    self.SendIMINT()
                    self.removeTgt()
                    self.getNewTgt()
                
                if(self.TarTime>=self.target.ObsTime):# Observation time is larger than needed time. Target satisfied.
                    self.SendIMINT()
                    self.removeTgt()
                    self.getNewTgt()

################################################

        else: # Impatient Heuristic
            while(1):
                
                if(self.target==42): #NO TARGET IN QUEUE
                    self.getNewTgt()
                
                # Check fuel before anything else!!
                if(not(self.jokerflag)): #joker not set yet. can search for targets
                    if(not(self.detectBool)): #dont have a detection
                        self.search()
                        self.detection()
                        self.searchdwell+=self.searchTime
                    
                    else: #we have a detection! woooo
                        self.detection()
                        self.searchdwell=0
                
                
                else: # joker flag set.
                    if(not(detectBool)):
                        #dont have an active detection. RTB.
                        self.ReturnToBase()
                    else: # detection flag set. We have a target in active track.
                        if(self.Bingo>0): #we still have fuel!
                            # We have fuel and can still start tracking.
                            self.detection()
                        else:
                            self.ReturnToBase()
                                
                                
                if(self.searchdwell>=5*self.searchTime): # searched for the target 5 times Why 5? Why not!
                    self.ReturnTgt()
                    self.removeTgt()
                    self.getNewTgt()
                
                if(self.TarTime>=self.target.ObsTime):# Observation time is larger than needed time. Target satisfied.
                    self.SendIMINT()
                    self.removeTgt()
                    self.getNewTgt()
                


    def setTarget(self,obj):
        # This function will take in the target object created by the message handler and assign it to the drone. 
        self.target=obj
        self.TarTime=0 #amount of target tracking time.
        self.startNode=obj.node

    def updateTime(self,timeDif): # timeDif= time delta. How much you want to update the clock by,
        #Update the timers with each timestep
        #timeDif=newDroneSimTime-self.LocalSimTime
        self.Joker-=timeDif
        if(self.Joker<=0):
            self.jokerflag=1
        self.Bingo-=timeDif
        self.MaintenanceActionTime-=timeDif
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

        print "\nNew Joker:", self.Joker, "New Bingo:",self.Bingo
        if(self.Bingo<=0): # Reached bingo. need to RTB.
            self.ReturnToBase()

    def setJokerBingo(self):
    # Call this funtion after the drone returns from a maintainance action, refuleing or at the start of the sim
        if(self.DroneLegs<self.MaintenanceActionTime):#We have less fuel time than maintainance time
            self.Joker=self.DroneLegs*0.8 # Joker is set at 6 hrs 24 min. Ensures we have enough time (48 min) to track another target before bingo

            self.Bingo=self.DroneLegs*0.9 # 45 minutes flight time to return to base

        else: #assuming we have more than 4 hours of flight time. If less than 4 hours, we should be premptively performing maintainance
            self.Joker=self.MaintenanceActionTime - 7200 # 2 hour joker
            self.Bingo=self.MaintenanceActionTime - 3600 # 1 hour bingo

        print "\nJoker set to:", self.Joker, "Bingo set to:",self.Bingo


    def resetMaintenanceTimer(self):
        self.MaintenanceActionTime=75600

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
        elif(self.currentNode.nodeType==1):
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
        self.updateTime(flightTime)
        if(self.detectBool):
            self.startNode=obj


       # 
    
    def subclassHandleMessage(self, msg):
        # tgtData = [tgtID 0,tgtIntelValue 1,tgtIntelPriority 2,tgtType 3,tgtStealth 4,tgtSpeed 5,tgtPredLoc 6,tgtGoalTrackTime 7,tgtActualTrackTime 8,tgtTrackAttempts 9]
        Data=msg[1]
        tgt=Target(Data[6])
        tgt.ID=Data[0]
        tgt.intelVal=Data[1]
        tgt.intelPriority=Data[1]
        tgt.Type=Data[3]
        tgt.Stealth=Data[4]
        tgt.speed=Data[5]
        tgt.ObsTime=Data[7]-Data[8]
        tgt.ActTractTime=Data[8]
        tgt.goalTime=Data[7]
        tgt.trackAttempts=Data[9]
        
        
        self.Target=tgt
    

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
            if(self.xpos!=self.target.node.xpos or self.ypos!=self.target.node.ypos): # tracking, but not looking at the right node
                self.updateCurNode(self.target.node)
                #We are on a new node. Need to roll the dice to see if we keep a track.
            if(self.probTest(self.currentNode.Trackprob)): #if we maintain track
                self.detectBool=1 #reaffirming the value
                self.sNeedBool=0
                self.TarTime+=self.searchTime

            else:
                self.detectBool=0
                self.sNeedBool=1
        else: # we dont have a track yet.
            if(self.xpos!=self.target.node.xpos or self.ypos!=self.target.node.ypos):
                self.detectBool=0 #we arnt even looking at the right node!
                self.sNeedBool=1
            elif(self.probTest(self.currentNode.Trackprob)): #looking at the right node, have a detection!
                self.detectBool=1 #reaffirming the value
                self.sNeedBool=0
                self.TarTime+=self.searchTime

            else: #looking at the right node, but no detection
                self.detectBool=0
                self.sNeedBool=0
        self.updateTime(self.searchTime) # the cost of doing one search operation


    def search(self): # this function needs a lot of work. How are we actually doing the search method?!?
        if(self.xpos!=self.target.node.xpos or self.ypos!=self.target.node.ypos): # we know we arnt looking at the right node.
            #Assume our intel came with a direction of movement and speed
            choice=random.random()
            if(choice>=.2): #80% chance we choose the correct direction. Assuming Intel keeps us updated and is usually right
                if(self.currentNode.nodeType==0): #curent node is a street
                    if(self.target.node.xpos>self.xpos):
                        self.updateCurNode(self.currentNode.nextNode)
                        # Only need flight time here. We will have to be more elegant when actually tracking.
                    else:
                        self.updateCurNode(self.currentNode.prevNode)
                elif(self.currentNode.nodeType==1): # an intersection.
                    for i in self.currentNode.Nodes:
                        if(self.currentNode.ypos==i.ypos):
                            if(self.target.node.xpos>self.currentNode.xpos and i.xpos>self.currentNode.xpos):
                            #Mouth full.... but correct dir.
                                self.updateCurNode(i)
                                break
                            elif(self.target.node.xpos<self.currentNode.xpos and i.xpos<self.currentNode.xpos):
                                self.updateCurNode(i)
                                break
                        elif(self.currentNode.xpos==i.xpos):
                            if(self.target.node.ypos>self.currentNode.ypos and i.ypos>self.currentNode.ypos):
                                #Mouth full.... but correct dir.
                                self.updateCurNode(i)
                                break
                            elif(self.target.node.ypos<self.currentNode.ypos and i.ypos<self.currentNode.ypos):
                                self.updateCurNode(i)
                                break
            else:
                if(self.currentNode.nodeType==0): #curent node is a street
                    if(self.target.node.xpos>self.xpos):
                        self.updateCurNode(self.currentNode.prevNode)
                    # Only need flight time here. We will have to be more elegant when actually tracking.
                    else:
                        self.updateCurNode(self.currentNode.NextNode)
                elif(self.currentNode.nodeType==1): # an intersection.
                    for i in self.currentNode.Nodes:
                        if(self.currentNode.ypos==i.ypos):
                            if(self.target.node.xpos>self.currentNode.xpos and i.xpos<self.currentNode.xpos):
                                #Mouth full.... but correct dir.
                                self.updateCurNode(i)
                                break
                            elif(self.target.node.xpos<self.currentNode.xpos and i.xpos>self.currentNode.xpos):
                                self.updateCurNode(i)
                                break
                        elif(self.currentNode.xpos==i.xpos):
                            if(self.target.node.ypos>self.currentNode.ypos and i.ypos<self.currentNode.ypos):
                                #Mouth full.... but correct dir.
                                self.updateCurNode(i)
                                break
                            elif(self.target.node.ypos<self.currentNode.ypos and i.ypos>self.currentNode.ypos):
                                self.updateCurNode(i)
                                break


    def ReturnToBase(self):
    #cant have any new assignments durning this time. May need to look at the messages to reject taskers.
    # need to delete target, return it to the queue.
        self.ReturnTgt()

        self.DistEntry=math.sqrt((self.xpos-self.EntNode.xpos)**2 +(self.ypos-self.EntNode.ypos)**2)
        timeToentry=int(self.DistEntry/self.FlightSpeed)
        self.updateTime(timeToentry) #update sim time

        if(self.MaintenanceActionTime<=75600): #MTBF
            self.resetMaintenanceTimer()
            self.updateTime(10800) #3 hrs for MTTR based on DoD study
        self.setJokerBingo()
        self.updateCurNode(self.EntNode)

    def flyTotgt(self,tgtx,tgty):
    # code to move the drone from the current location to the target's intel location. assuming the intel location is within 1 node of actual.
        distTgt=math.sqrt((self.xpos-tgtx)**2 +(self.ypos-tgty)**2) #distance to the intel location x,y
        TOT=int(distTgt/self.FlightSpeed)
        self.updateTime(TOT)

    def saveState(self):
        saver=DRONEState(self)
        self.stateQueue.append(saver)
#        print self.LocalSimTime


    def restoreState(self,timeStamp):
        #Get the old state:
        temp=[]
        for i in self.stateQueue:
            if(i.LocalSimTime<=timeStamp):
                #incase the time stamp is not exactly the correct one. Find the closest, previous state save
                temp=i
#                print i.LocalSimTime
        self.Restore(i)

    def Restore(self,obj):
    #restore drone to old state.
        self.uid = obj.uid
        self.droneType = obj.droneType
        self.LocalSimTime=obj.LocalSimTime
        self.MaintenanceActionTime=obj.MaintenanceActionTime
        self.Joker=obj.Joker
        self.jokerflag=obj.jokerflag
        self.Bingo=obj.Bingo
        self.DistEntry=obj.DistEntry
        self.FlightSpeed=obj.FlightSpeed
        self.DroneLegs= obj.DroneLegs
        self.xpos=obj.xpos
        self.ypos=obj.ypos
        self.EntNode=obj.EntNode
        self.currentNode=obj.currentNode
        
        self.target=obj.target #Stephan: How are we handling this? On roll back, will we just restore to this time stamp and roll with it?
        
        self.detectBool=obj.detectBool
        self.sNeedBool=obj.sNeedBool
        self.timeOnNode=obj.timeOnNode
        self.nodeTime=obj.nodeTime
        self.searchTime=obj.searchTime
        self.searchdwell=obj.searchdwell
        self.TarTime=obj.TarTime

    def ReturnTgt(self):
        #update the target
        self.target.ActTractTime+=self.TarTime
        self.target.trackAttempts+=1
        
        
        retTgt=Message(2,self.target,self.uid,'IMINT',self.LocalSimTime) #create message
        self.sendMessage(retTgt)   # sends message
        self.removeTgt()

    def SendIMINT(self):
        #update the target
        self.target.ActTractTime+=self.TarTime
        self.target.trackAttempts+=1
        
        sendMsg=Message(2,self.target,self.uid,'IMINT',self.LocalSimTime)
        self.sendMessage(sendMsg)
        self.removeTgt()

    def removeTgt(self):
        self.target=42

    def getNewTgt(self):
        while(1): #Wait for a new message to come in
            msg=self.getNextMessage() # Gets a new target
            if(not(msg==None)):
                self.subclassHandleMessage(msg)
                print "New target aquired"
                break



