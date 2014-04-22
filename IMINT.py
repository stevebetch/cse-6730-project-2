import sys, time
import Pyro4
from LogicalProcess import *
from random import *
from state import IMINTState
from HMINT import *
from multiprocessing import Queue, Lock
from Message import *
from nodes import *
from Map import *

class IMINT (LogicalProcess):

    # Instance Variable List
    # id: unique id for component
    # heuristic: identifies which heuristic for target-drone assignments is being used
    # high, low, mode: inputs for triangular distribution of service time in minutes
    # priorityAdjust: reduction in prioirity for rework in heuristic 3 (0.5 = 50% reduciton in prioirity)
    # totalValue: total intel value of all targets that have been succesfully tracked
    # targetsTracked: total number of targets that have been succesfully tracked

    # Initialize IMINT
    # Input: heuristicNum=1,2, or 3 (naive, local, or timer heuristic)
    # Output: Initializes IMINT logical process
    # Description: Intialization of parameters that control assignment data collection and re-work decisions 
    def __init__(self,heuristicNum):
        LogicalProcess.__init__(self)
        self.id = 'IMINT'
        self.heuristic=heuristicNum
        self.high=30
        self.low=10
        self.mode=15
        self.priorityAdjust=0.5
        self.totalValue=0
        self.targetsTracked=0

    # Call function
    def __call__(self):
        self.run()
    
    # Save State
    # Input: None
    # Output: Saves current state of IMINT logical process
    # Description: Saves all parameters needed to describe state of LP
    def saveState(self):
        print 'Saving current IMINT state'
        saver=IMINTState(self)
        self.stateQueue.append(saver)        
    
    # Restore State
    # Input: timestamp to restore to
    # Output: Restores past state of IMINT logical process
    # Description: Restores all parameters needed to describe state of LP    
    def restoreState(self, timestamp):
        print 'restoring to last IMINT state stored <= %d' % (timestamp)
        index=0
        for i in range(len(self.stateQueue)-1,-1,-1):
            if(timestamp>=self.stateQueue[i].key):
                index=i
                break
        self.Restore(self.stateQueue[index])
        
    def Restore(self,obj):
        self.key=obj.localTime
        self.id=obj.id
        self.heuristic=obj.heuristic
        self.totalValue=obj.totalValue
        self.targetsTracked=obj.targetsTracked
        self.localTime=obj.localTime 

    # Handle Message [IN PROGRESS]
    # Input: Message data structure (see Message.py for documentation)
    # Output: Updates target attributes, reporting attributes and may send target assignment to CAOC [or TBD for msg type 1]
    # Description: Handles message based on message type
    #    Msg Type 1: [TBD]
    #    Msg Type 2: Calls addTarget function for Target Data attribute of input Message
    #    Msg Type 3: Error if IMINT receives this message type
    def subclassHandleMessage(self, msg):
        # check message type
        if msg.msgType==1:
            # TBD
            pass
        elif msg.msgType==2:
            # update target track attempts for target data
            msg[1][9]+=1
            # check hueristic number
            if self.heuristic==1:
                # if goal track time has not been achieved, send updated tgt assignment to CAOC after processing time
                if msg[1][8]-msg[1][7]<0:
                    # send message to CAOC process
                    newTgtData=msg[1]
                    newTgtMsg=Message(2,newTgtData,self.id,'CAOC',self.localTime+random.triangular(self.high,self.low,self.mode))
                    self.sendMessage(newTgtMsg)
                else:
                    # if goal track time has been achieved, update the total value and number of tracked targets 
                    #    In the current implementation we allow IMINT to clear out it's backlog of unprocessed images at the sim end time
                    self.totalValue+=msg[1][1] # this isn't quite right - we don't really get this value until AFTER the processing time...but I'm trying to avoid a message here
                    self.targetsTracked+=1
            elif self.heuristic==3 or self.heuristic==2:
                if msg[1][8]-msg[1][7]<0:
                    # if goal track time has not been achieved, adjsut priority and send updated tgt assignment to CAOC after processing time
                    newTgtData=[targetData[0],targetData[1],self.priorityAdjust*targetData[2],targetData[3],targetData[4],targetData[5],targetData[6],targetData[7],targetData[8],targetData[9]]
                    newTgtMsg=Message(2,newTgtData,self.id,'CAOC',self.localTime+random.triangular(self.high,self.low,self.mode))
                    self.sendMessage(newTgtMsg)
                else:
                    # if goal track time has been achieved, update the total value and number of tracked targets 
                    #    In the current implementation we allow IMINT to clear out it's backlog of unprocessed images at the sim end time                    
                    self.totalValue+=msg[1][1] # this isn't quite right - we don't really get this value until AFTER the processing time...but I'm trying to avoid a message here
                    self.targetsTracked+=1
                    print 'Total Value: ' + str(self.totalValue)
                    print 'Total Targets Tracked: ' + str(self.targetsTracked)
        elif msg.msgType==3:
            # print error message
            print 'IMINT Error: Received Message Type 3 from ' + str(msg[2]) + ' at ' + str(msg[4])
        msg.printData(1)
        # Mark: below line for test only
        #self.sendMessage(Message(1, ['Data1'], 'IMINT', 'CAOC', 9))

    # Run
    # Input: None
    # Output: Starts associated objects and queues
    # Description: Save state, start queues  
    def run(self):

        print('IMINT Running')
        
        self.saveState()

        # Get the message queue objects from Pyro    
        nameserver = Pyro4.locateNS()
        LPIDs = []
        
        controllerInQ_uri = nameserver.lookup('inputqueue.controller')
        self.controllerInQ = Pyro4.Proxy(controllerInQ_uri)
        
        caocInQ_uri = nameserver.lookup('inputqueue.caoc')
        self.caocInQ = Pyro4.Proxy(caocInQ_uri)     
        LPIDs.append(self.caocInQ.LPID)
        
        imintInQ_uri = nameserver.lookup('inputqueue.imint')
        self.inputQueue = Pyro4.Proxy(imintInQ_uri)
        self.imintInQ = None
        LPIDs.append(self.inputQueue.LPID)
        
        droneInQs_uri = nameserver.lookup('inputqueue.drones')
        self.droneInQs = Pyro4.Proxy(droneInQs_uri)
        LPIDs.extend(self.droneInQs.getLPIDs())
        
        self.initGVTCounts(LPIDs)

        ## Event loop iteration
        while True:
            print 'IMINT loop iteration'
            msg = self.getNextMessage()
            #print msg
            if msg:
                self.handleMessage(msg)
                if msg.msgType==2:
                    print "IMINT passed a traget"
            
            time.sleep(2)
            sys.stdout.flush()

