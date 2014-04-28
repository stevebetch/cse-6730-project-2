import sys
from CAOC import *
from LogicalProcess import *
from Target import *
import random
from state import HMINTState

class HMINT (LogicalProcess):
    "Human intelligence"
    
    INF = 999999999999
    
    # Instance Variable List
    # numTargets: Total number of targets to be created
    # count: number of targets created
    # msgTimestamp: timestamp of next target assignment to be sent to CAOC for prioritization
    # mapNodes: number of nodes in the map
    
    # Initialize HMINT
    # Input: numTargets=total number of targets that might need to be targeted, randNodes is a vector of nodes from the map
    # Output: Initializes HMINT class object
    # Description: Intialization of parameters that control target generation    
    def __init__(self, numTargets, randNodes,Tartype):
        LogicalProcess.__init__(self)
        self.id = LogicalProcess.HMINT_ID        
        self.numTargets = numTargets
        self.count = 0
        self.currTargetTimestamp = 0
        self.targetTimestamps = []
        self.targets = {}
        self.randNodes = randNodes
        self.tarCont=
        
    # Call function
    def __call__(self):
        self.run()

    def saveState(self):
        print 'Saving current HMINT state'
        saver=HMINTState(self)
        self.stateQueue.append(saver)

    def restoreState(self,timestamp):
        print 'restoring to last HMINT state stored <= %d' % (timestamp)
        index=0
        for i in range(len(self.stateQueue)-1,-1,-1):
            if(timestamp>=self.stateQueue[i].key):
                index=i
                break
            else:
                self.stateQueue.pop(i)
        self.restore(self.stateQueue[index])    

    def restore(self,obj):
        self.id = obj.id
        self.localTime=obj.localTime
        self.numTargets = obj.numTargets
        self.count = obj.count
        self.currTargetTimestamp = obj.currTargetTimestamp
        self.randNodes = obj.randNodes     
    
    # Generate Target
    # Input: None
    # Output: Adds new target assignment message to CAOC input queue
    # Description: Randomly generates target attributes of a new target and sends that target to the CAOC input queue
    #    Tgt ID: unique integer id for targets counting up from 0
    #    Tgt Intel Value: Real number from a [10,100,80] triangular distribution
    #    Tgt Intel Priority: Initialized to Tgt Intel Value
    #    Tgt Type: "Vehicle" or "Pedestrian" with equal likelihood
    #    Tgt Stealth: Real number from a [0.5,.95,0.8] or [0.1,0.9,0.5] triangular distribution (based on tgt type)
    #    Tgt Speed: Real number from a [11.11, 19.44, 15.28] triangular or [1.44,0.288] normal distribution (based on tgt type)
    #    Tgt Predicted Location: Node pointer from node vector from DroneSim1 Map object, randomly selected
    #    Tgt Goal Track Time: Real number from a[60,600,300] triangular distribution
    #    Tgt Actual Track Time: Initialized to 0 seconds
    #    Tgt Track Attempts: Initialized to 0 seconds
    #    Msg Timestamp: Real number from a last_msg_time+[1380,4200,2100] triangular distribution in seconds,
    #          HMINT generation rate [1200,3600,1800] + pre-calc of CAOC server processing time [180,600,300]
    def generateNextTarget(self):
        tgtID=self.count
        tgtIntelValue=random.triangular(1,100,60)
        tgtIntelPriority=tgtIntelValue
        r=random.random()
        if r<0.5:
            tgtType='Vehicle'
            tgtStealth=random.triangular(0.5, 0.95, 0.8)
            tgtSpeed=random.triangular(11.11, 19.44, 15.28)#based on average urban speed for several countries
        else:
            tgtType='Pedestrian'
            tgtStealth=random.triangular(0.1, 0.9, 0.5)
            tgtSpeed=random.normalvariate(1.44, 0.288)#based on project 1 data
        tgtPredLoc=self.randNodes[self.count]
        tgtGoalTrackTime=random.triangular(60,600,300)
        tgtActualTrackTime=0
        tgtTrackAttempts=0
        self.currTargetTimestamp=self.currTargetTimestamp+random.triangular(1380,4200,2100)
        tgtData = [tgtID,tgtIntelValue,tgtIntelPriority,tgtType,tgtStealth,tgtSpeed,tgtPredLoc,tgtGoalTrackTime,tgtActualTrackTime,tgtTrackAttempts]
        self.targetTimestamps.append(self.currTargetTimestamp)
        self.targets[self.currTargetTimestamp] = tgtData
        self.count = self.count + 1
        
        
    def subclassHandleMessage(self, msg):
        
        if msg.msgType == 4 and isinstance(msg.data, TargetRequest):
            timestamp = msg.data.timestamp
            print 'HMINT: Received target request with timestamp %d' % timestamp
            self.sendTargets(timestamp)
        
        
    def sendTargets(self, timestamp):
        
        # separate out targets with ts <= passed timestamp value
        sendTimestamps = []
        remainingTimestamps = []
        minTimestamp = HMINT.INF
        for ts in self.targetTimestamps:
            if ts <= timestamp:
                sendTimestamps.append(ts)
            else:
                remainingTimestamps.append(ts)
            if ts < minTimestamp:
                minTimestamp = ts
                
        # send target message with targets in lowest to highest timestamp order
        sendTimestamps.sort()
        responseData = TargetResponse()
        msgTimestamp = 0
        if len(sendTimestamps) == 0:
            if not(minTimestamp == HMINT.INF):
                responseData.addTarget(self.targets[minTimestamp])
                msgTimestamp = minTimestamp
                print 'HMINT: No targets found with timestamp < %d, adding target with smallest timestamp response data' % timestamp
                remainingTimestamps.remove(minTimestamp)
            else:
                print 'HMINT: No targets remaining'
        for ts in sendTimestamps:
            responseData.addTarget(self.targets[ts])
            msgTimestamp = ts
            print 'HMINT: Adding target with timestamp %d to response data' % ts
        tgtMsg = Message(5, responseData, LogicalProcess.HMINT_ID, LogicalProcess.CAOC_ID, msgTimestamp)        
        self.sendMessage(tgtMsg) 
        
        # update target timestamps list and cleanup
        self.targetTimestamps = remainingTimestamps
        if len(self.targetTimestamps) == 0:
            self.targets = {}
    
    # run
    # Input: None
    # Output: Generates and adds all required targets to CAOC input queue
    # Description: Changes running status to true, generates target messages
    def run(self):
        
        print('HMINT Running')
        
        # Get the message queue objects from Pyro    
        nameserver = Pyro4.locateNS()
        LPIDs = []
        
        controllerInQ_uri = nameserver.lookup('inputqueue.controller')
        self.controllerInQ = Pyro4.Proxy(controllerInQ_uri)
        
        hmintInQ_uri = nameserver.lookup('inputqueue.hmint')
        self.inputQueue = Pyro4.Proxy(hmintInQ_uri)
        self.hmintInQ = None
        LPIDs.append(self.inputQueue.LPID)        
        
        caocInQ_uri = nameserver.lookup('inputqueue.caoc')
        self.caocInQ = Pyro4.Proxy(caocInQ_uri)
        LPIDs.append(self.inputQueue.LPID)        
        
        imintInQ_uri = nameserver.lookup('inputqueue.imint')
        self.imintInQ = Pyro4.Proxy(imintInQ_uri)
        LPIDs.append(self.imintInQ.LPID)
        
        droneInQs_uri = nameserver.lookup('inputqueue.drones')
        self.droneInQs = Pyro4.Proxy(droneInQs_uri)
        LPIDs.extend(self.droneInQs.getLPIDs()) 
        
        loopInQs_uri = nameserver.lookup('inL.loop')
        self.Loopcont = Pyro4.Proxy(loopInQs_uri)        
        
        self.initGVTCounts(LPIDs) 
            
        while self.count < self.numTargets:
            # generate targets and add to CAOC input queue
            time.sleep(0.1)
            self.generateNextTarget()
        
        # Event loop
        count=0
        while (self.Loopcont.getCon()==1):
            count+=1
            if(count%5000==0):
                print 'HMINT iteration. Local time:', self.localTime            
            msg = self.getNextMessage()
            if msg:
                self.handleMessage(msg)
            time.sleep(0.1)
            sys.stdout.flush()        


class TargetResponse():
    
    def __init__(self):
        self.targetData = []
        
    def addTarget(self, tgtData):
        self.targetData.append(tgtData)