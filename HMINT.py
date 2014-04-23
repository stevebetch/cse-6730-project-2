import sys
from CAOC import *
from Target import *
import random
class HMINT:
    "Human intelligence"
    
    # Instance Variable List
    # caoc: instance of CAOC
    # running: false or true to describe if HMINT is currently generating targets
    # numTargets: Total number of targets to be created
    # seedNum: seed for random number generator for this sim replication
    # count: number of targets created
    # msgTimestamp: timestamp of next target assignment to be sent to CAOC for prioritization
    # mapNodes: number of nodes in the map
    
    # Initialize HMINT
    # Input: numTargets=total number of targets that might need to be targeted, seedNum=seed for this sim replication
    # Output: Initializes HMINT class object
    # Description: Intialization of parameters that control target generation    
    def __init__(self, numTargets, randNodes, seedNum):       
        running = 'false'
        self.numTargets = numTargets
        self.count = 0
        self.msgTimestamp = 0
        self.randNodes = randNodes
        self.randSeed = seedNum
        random.seed(seedNum)
    
    # Set CAOC
    # Input: None
    # Output: None
    # Description: Identifies CAOC (part of local logical process)
    def setCAOC(self, caoc):
        self.caoc = caoc
    
    # Generate Target
    # Input: None
    # Output: Adds new target assignment message to CAOC input queue
    # Description: Randomly generates target attributes of a new target and sends that target to the CAOC input queue
    #    Tgt ID: unique integer id for targets counting up from 0
    #    Tgt Intel Value: Real number from a [10,100,80] triangular distribution
    #    Tgt Intel Priority: Initialized to Tgt Intel Value
    #    Tgt Type: "Vehicle" or "Pedestrian" with equal likelihood
    #    Tgt Stealth: Real number from a [0.5,1,0.8] or [1,2,1.5] triangular distribution (based on tgt type)
    #    Tgt Speed: Real number from a [0.5,1,0.8] or [1,2,1.5] triangular distribution (based on tgt type)
    #    Tgt Predicted Location: Node pointer from node vector from DroneSim1 Map object, randomly selected
    #    Tgt Goal Track Time: Real number from a[10,360,30] triangular distribution
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
        tgtGoalTrackTime=random.triangular(10,360,30)
        tgtActualTrackTime=0
        tgtTrackAttempts=0
        self.msgTimestamp=self.msgTimestamp+random.triangular(23,70,35)
        tgtData = [tgtID,tgtIntelValue,tgtIntelPriority,tgtType,tgtStealth,tgtSpeed,tgtPredLoc,tgtGoalTrackTime,tgtActualTrackTime,tgtTrackAttempts]
        tgtMsg=Message(2,tgtData,'CAOC','CAOC',self.msgTimestamp)
        self.caoc.sendMessage(tgtMsg) # will this mess up the anti-message process?
        self.count = self.count + 1
    
    # Start
    # Input: None
    # Output: Generates and adds all required targets to CAOC input queue
    # Description: Changes running status to true, generates targets
    def start(self):
        self.running = 'true'
        while self.count < self.numTargets:
            # generate targets and add to CAOC input queue
            self.generateNextTarget()
        self.stop()

    # Stop
    # Input: None
    # Output: None
    # Description: Changes running status to false  
    def stop(self):
        self.running = 'false'