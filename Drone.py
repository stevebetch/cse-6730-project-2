import sys,math
from LogicalProcess import *
from Map import GenMap
from nodes import EntryNode
from multiprocessing import Lock
from state import *
import random
from Message import *
from Target import *
import copy

import Pyro4

dLock=threading.Lock()

class Drone (LogicalProcess):

    # instance argument list
    #id - unique id of drone
    #droneType - descriptive

    def __init__(self, uid, droneType,heuristic,Legs):
        self.uid = uid
        self.heuristic=heuristic
        LogicalProcess.__init__(self)
        self.droneType = droneType

        self.LocalSimTime=5 #current simulation time for the drone

        self.MaintenanceActionTime=75600 #MTBF 21 hrs based on DoD study, here in seconds
        self.Joker=0 #how much time we have to search
        self.jokerflag=0

        self.Bingo=0 #time until we have to leave the map
        self.DistEntry=0 # distance from entry node
        self.FlightSpeed=random.randint(46,54)#Random flight speed of the drone based on loiter and top speed, m/s
        self.DroneLegs=Legs #11.6hrs = 41760s max endurance, 5.8hrs = 20880s median endurance

        self.xpos=0 #current x location
        self.ypos=0 #current y location
        self.entryX=0
        self.entryY=0
        self.EntNode=[]
        self.currentNode=[]

        self.target=42
        self.detectBool=0 # Boolian used for detection logic
        self.sNeedBool=1 #boolian to determine if we need to activate the search logic.
        self.timeOnNode=0 #how long have we been on the current node?
        self.nodeTime=0 #how long should it take the target to traverse the node?
        self.searchTime=10 #It takes 20 seconds to search the area.
        self.searchdwell=0
        self.TarTime=0
        self.startNode=[]
        self.IMINTtgt=None
    
        self.droneRadLim= 50 # The search radius is only 50 m
    
    
    def __call__(self, mapObj):
        self.run(mapObj)
        
    def getCurrentState(self):
        return None
    
    def run(self,mapObj):
        # Begin process of selecting target from CAOC priority queue, tracking, check when refueling needed, etc.
        
        dLock.acquire()
        
        print('Drone process running')
        self.saveState()
       
        # Get the message queue objects from Pyro
        nameserver = Pyro4.locateNS()
        LPIDs = []
        
        # Pyro4 startup code
        controllerInQ_uri = nameserver.lookup('inputqueue.controller')
        self.controllerInQ = Pyro4.Proxy(controllerInQ_uri)
        
        hmintInQ_uri = nameserver.lookup('inputqueue.hmint')
        self.hmintInQ = Pyro4.Proxy(hmintInQ_uri)
        LPIDs.append(self.hmintInQ.LPID)        
        
        caocInQ_uri = nameserver.lookup('inputqueue.caoc')
        self.caocInQ = Pyro4.Proxy(caocInQ_uri)     
        LPIDs.append(self.caocInQ.LPID)
        
        imintInQ_uri = nameserver.lookup('inputqueue.imint')
        self.imintInQ = Pyro4.Proxy(imintInQ_uri)
        LPIDs.append(self.imintInQ.LPID)
        
        droneInQs_uri = nameserver.lookup('inputqueue.drones')
        self.droneInQs = Pyro4.Proxy(droneInQs_uri)
        LPIDs.extend(self.droneInQs.getLPIDs())

        loopInQs_uri = nameserver.lookup('inL.loop')
        self.Loopcont = Pyro4.Proxy(loopInQs_uri)
    
        self.initGVTCounts(LPIDs)  
        dLock.release()
        
        count=0
        #Start setting up the drone
        self.setEntry(mapObj) #MUST PASS THE ENTRY NODE!!! (map.MapEntryPt)
        self.currentNode=mapObj #the only time we directly set the current node.
        self.LocalSimTime=self.localTime
        self.setJokerBingo() # fuel settings
#        need to send a message that tells caoc where the drones are. Not ready for a target, therefore, busy.
        initMes=Message(3,[self.uid,'Busy',self.currentNode],self.uid,'CAOC',self.localTime)
        self.sendMessage(initMes)

        # Begin process of selecting target from CAOC priority queue, tracking, check when refueling needed, etc.
        # Begin at entry node. aka, only pass drone the entry node!!!
        

        if(self.heuristic==1): #Naive heuristic
            while(self.Loopcont.getCon()==1):
                
                if(self.Bingo<0):
                    self.ReturnToBase()
                if(debug==1):
                    print self.target
                if(self.target==42): #NO TARGET IN QUEUE
                    try:
                        self.getNewTgt()
                    except:
                        if(self.Loopcont.getCon()==0):
                            break
                
                
                
         # Check fuel before anything else!!
                if(not(self.target==42)): #make sure we have a target
                    if(not(self.jokerflag)): #joker not set yet. can search for targets
                        if(not(self.detectBool)): #dont have a detection
                            self.search()
                            self.detection()
                            self.searchdwell+=self.searchTime #keep track of time
                        
                        else: #we have a detection! woooo
                            self.detection()
                            self.searchdwell=0
                
                    else: # joker flag set.
                        if(not(self.detectBool)):
                            #dont have an active detection. RTB.
                            self.ReturnToBase()
                        else: # detection flag set. We have a target in active track.
                            if(self.Bingo>0): #we still have fuel!
                            # We have fuel and can still start tracking.
                                self.detection()
                            else:
                                self.ReturnToBase()
                    if(not(self.target==42)):
                        if(self.TarTime>=self.target.ObsTime):# Observation time is larger than needed time. Target satisfied.
                            self.ReturnTgt()
#                            self.removeTgt()

    ################################################
    
        elif(self.heuristic==2): # Local Heuristic
            while(self.Loopcont.getCon()==1):
                
                if(self.Bingo<0):
                    self.ReturnToBase()
                if(debug==1):
                    print self.target
                if(self.target==42): #NO TARGET IN QUEUE
                    try:
                        self.getNewTgt()
                    except:
                        if(self.Loopcont.getCon()==0):
                            break
                
                # Check fuel before anything else!!
                if(not(self.target==42)):
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

                if(not(self.target==42)):
                
                    droneRad=math.sqrt((self.xpos-mapObj.xpos)**2+(self.ypos-mapObj.ypos)**2)
                                        
                    if(droneRad>self.droneRadLim): # searched for the target within the local area
                        self.ReturnTgt()
    #                    self.removeTgt()
                    elif(self.TarTime>=self.target.ObsTime):# Observation time is larger than needed time. Target satisfied.
                        self.ReturnTgt()
    #                    self.removeTgt()


################################################

        else: # Impatient Heuristic
            while(self.Loopcont.getCon()==1):
                if(self.Bingo<0):
                    self.ReturnToBase()
                if(debug==1):
                    print self.target
                if(self.target==42): #NO TARGET IN QUEUE
                    try:
                        self.getNewTgt()
                    except:
                        if(self.Loopcont.getCon()==0):
                            break
                if(not(self.target==42)):
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

                if(not(self.target==42)):
                    if(self.searchdwell>=10*self.searchTime*(self.target.intelVal/100)): # searched for the target 10*percentMaxValue (i.e. 1 to 10 times)
                        self.ReturnTgt()
    #                    self.removeTgt()
                    elif(self.TarTime>=self.target.ObsTime):# Observation time is larger than needed time. Target satisfied.
                        self.ReturnTgt()
#                    self.removeTgt()

        self.reset()
        


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
        if debug==1:
            print 'drone %d updated LocalSimTime to %d' % (self.uid, self.LocalSimTime)
        self.timeOnNode+=timeDif
        if(not(self.target==42)):
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
        if(debug==1):
            print "\nNew Joker:", self.Joker, "New Bingo:",self.Bingo
#        if(self.Bingo<=0): # Reached bingo. need to RTB.
#            self.ReturnToBase()





    def setJokerBingo(self):
    # Call this funtion after the drone returns from a maintainance action, refuleing or at the start of the sim
        if(self.DroneLegs<self.MaintenanceActionTime):#We have less fuel time than maintainance time
            self.Joker=self.DroneLegs*0.8 # Joker is set at 6 hrs 24 min. Ensures we have enough time (48 min) to track another target before bingo

            self.Bingo=self.DroneLegs*0.9 # 45 minutes flight time to return to base

        else: #assuming we have more than 4 hours of flight time. If less than 4 hours, we should be premptively performing maintainance
            self.Joker=self.MaintenanceActionTime - 7200 # 2 hour joker
            self.Bingo=self.MaintenanceActionTime - 3600 # 1 hour bingo
        if(debug==1):
            print "\nJoker set to:", self.Joker, "Bingo set to:",self.Bingo





    def resetMaintenanceTimer(self):
        #call this to reset the maintenance clock
        self.MaintenanceActionTime=75600





    def setEntry(self,obj):
# set the entry node on the drone
        self.EntNode=obj
        if(debug==1):
            print "\n Drone set Map entry at:" , self.EntNode.xpos,",",self.EntNode.ypos
            print ""
        self.entryX=self.EntNode.xpos
        self.entryY=self.EntNode.ypos




    def updateCurNode(self,obj):
        #update the current node the drone is at. Also update time with how long it takes to fly.
        oldnode=self.currentNode
        flightTime=0
        length=0
        self.currentNode=obj #may not be needed, but may be expanded later if needed.
        if(self.currentNode==2): #entry node. need to get it on the map.
            self.currentNode=self.currentNode.nextNode
        
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
        #handle incoming target messages. only care about type 2 messages.
        if(msg.msgType==2): # New target
            # tgtData = [tgtID 0,tgtIntelValue 1,tgtIntelPriority 2,tgtType 3,tgtStealth 4,tgtSpeed 5,tgtPredLoc 6,tgtGoalTrackTime 7,tgtActualTrackTime 8,tgtTrackAttempts 9]
            Data=msg.data
            if(debug==1):
                msg.printData(1)
            
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
            
            
            self.target=tgt
            self.updateTime(msg.timestamp - self.LocalSimTime)
     
     
     
     
            

    def probTest(self,probVal):
        #This function will be called to determine if we get a positive detection on the target

        testprob=random.uniform(0,1)
        #Fuseing the probVal, which is the map Nusicnce factor, with target properties.
        TotProb= probVal*self.target.Stealth
        # This is the probability of detect.
        
        if(TotProb<=testprob):
            # Weve got a positive hit!
            return 1
        else:
            return 0






    def detection(self):
        # Begin by seeing if we already have a track
        if(self.target.node.nodeType==3):#entry node....
            self.target.node=self.target.node.nextNode
        if(self.currentNode.nodeType==3):#entry node....
            self.updateCurNode(self.currentNode.nextNode)
        if(self.detectBool==1): #we have a track!
            if(1):
                print "Have a track!"
                print self.TarTime
            # Check to see if we are on the same node as the target.
            if(self.xpos!=self.target.node.xpos or self.ypos!=self.target.node.ypos): # tracking, but not looking at the right node
                self.updateCurNode(self.target.node)
                #We are on a new node. Need to roll the dice to see if we keep a track.
            if(self.probTest(self.currentNode.prob)): #if we maintain track
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
            elif(self.probTest(self.currentNode.prob)): #looking at the right node, have a detection!
                self.detectBool=1 #reaffirming the value
                self.sNeedBool=0
                self.TarTime+=self.searchTime

            else: #looking at the right node, but no detection
                self.detectBool=0
                self.sNeedBool=0
        self.updateTime(self.searchTime) # the cost of doing one search operation








    def search(self):
        #this is the search method.
        if(self.xpos!=self.target.node.xpos or self.ypos!=self.target.node.ypos): # we know we arnt looking at the right node.
            #Assume our intel came with a direction of movement and speed
            choice=random.random()
            if(choice>=.2): #80% chance we choose the correct direction. Assuming Intel keeps us updated and is usually right
                if(self.currentNode.nodeType==0): #curent node is a street
                    if(self.target.node.xpos>self.xpos):
                        self.updateCurNode(self.currentNode.nextNode)
                        # Only need flight time here. We will be more elegant when actually tracking.
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
                        self.updateCurNode(self.currentNode.nextNode)
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
    #cant have any new assignments durning this time.
    # need to delete target, return it to the queue.
        if(not(self.target==42)):
            self.ReturnTgt()
        if(debug==1):
            print "xpos:",self.xpos
            print "ypos:",self.ypos
            print "Entry xpos:",self.entryX
            print "Entry ypos:",self.entryY
            sys.stdout.flush()
        self.DistEntry=math.sqrt((self.xpos-self.entryX)**2 +(self.ypos-self.entryY)**2)
        timeToentry=int(self.DistEntry/self.FlightSpeed)
        self.updateTime(timeToentry) #update sim time

        if(self.MaintenanceActionTime<=75600): #MTBF
            self.resetMaintenanceTimer()
            self.updateTime(10800) #3 hrs for MTTR based on DoD study
        self.setJokerBingo()
        self.updateCurNode(self.EntNode)
        self.removeTgt()





    def flyTotgt(self,tgtx,tgty):
    # code to move the drone from the current location to the target's intel location. assuming the intel location is within 1 node of actual.
        self.updateCurNode(self.target.node)





    def saveState(self):
        saver=DRONEState(self)
        print 'Drone %d saving state for timestamp %d' % (self.uid, saver.localTime)
        self.stateQueue.append(saver)






    def restoreState(self,timestamp):
        print 'restoring to last Drone state stored <= %d' % (timestamp)

        a=[]
        for i in self.stateQueue:
            if(timestamp>=i.key):
#                print "Key:",i.key
                index=i
                a.append(i)
        
        self.restore(index)
        self.stateQueue=a




    def restore(self,obj):
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
        
        self.target=obj.target
        
        self.detectBool=obj.detectBool
        self.sNeedBool=obj.sNeedBool
        self.timeOnNode=obj.timeOnNode
        self.nodeTime=obj.nodeTime
        self.searchTime=obj.searchTime
        self.searchdwell=obj.searchdwell
        self.TarTime=obj.TarTime






    def ReturnTgt(self):
        #update the target
        self.target.ActTracTime+=self.TarTime
        self.target.trackAttempts+=1
        # tgtData = [tgtID 0,tgtIntelValue 1,tgtIntelPriority 2,tgtType 3,tgtStealth 4,tgtSpeed 5,tgtPredLoc 6,tgtGoalTrackTime 7,tgtActualTrackTime 8,tgtTrackAttempts 9]
        self.removeTgt()
        #self.setLocalTime(self.LocalSimTime)



    def removeTgt(self):
        self.IMINTtgt=self.target
        self.target=42
        self.TarTime=0
        #self.setLocalTime(self.LocalSimTime)


    def getNewTgt(self):
       # self.setLocalTime(self.LocalSimTime)
        if(not(self.IMINTtgt==None)): #Return the target to imint.
            tgtData=[self.IMINTtgt.ID,self.IMINTtgt.intelVal,self.IMINTtgt.intelPriority,self.IMINTtgt.Type,self.IMINTtgt.Stealth,self.IMINTtgt.speed,self.IMINTtgt.node,self.IMINTtgt.goalTime,self.IMINTtgt.ActTracTime,self.IMINTtgt.trackAttempts]
            if(debug==1):
                   print "Target Data:", tgtData
            retTgt=Message(2,tgtData,self.uid,'IMINT',self.LocalSimTime) #create message
            self.sendMessage(retTgt)   # sends message

        data=[self.uid,'Idle',self.currentNode]
        sendMes=Message(3,data,self.uid,'CAOC',self.LocalSimTime)
       #        sendMes.printData(1)
        self.sendMessage(sendMes)
        count=0
        
    
        while(1): #Wait for a new message to come in
            count+=1
            try:
                msg=self.getNextMessage() # Gets a new target

                if not(msg is None):
#                    print "Valid Message passed to drone! Message Type:",msg.msgType
                    if(debug==1):
                        msg.printData(1)
                        sys.stdout.flush()
#                    if(msg.msgType==2):
                    break
            except:
                pass
            if(count%5000==0):
                print "Drone is in the getNewTgt loop. Count=:",count
            if(self.Loopcont.getCon()==0):
                print "ENDING THE SIM!!!!!"
                break
    
            if(count>1000):
                updateTime(100) #penalty
                data=[self.uid,'Idle',self.currentNode]
                sendMes=Message(3,data,self.uid,'CAOC',self.LocalSimTime)
                #        sendMes.printData(1)
                self.sendMessage(sendMes)
                count=0
        if(self.Loopcont.getCon()==0):
            return
                    
        self.handleMessage(msg)
        if(msg.msgType==2):
            print "New target aquired"
            timedif=(self.LocalSimTime-msg.timestamp)
            print 'LocalSimTime is %d' % self.LocalSimTime
            print 'msg.timestamp is %d' % msg.timestamp
            print 'timedif is %d' % timedif
            if(timedif<0):#message is in the future
                self.updateTime(timedif*-1)
        if(not(self.target==42)):
            self.updateCurNode(self.target.node)



