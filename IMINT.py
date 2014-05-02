import sys, time, csv,os
import Pyro4
from LogicalProcess import *
from random import *
from state import IMINTState
from HMINT import *
from multiprocessing import Queue, Lock
from Message import *
from nodes import *
from Map import *


csvLock=threading.Lock()

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
    def __init__(self,heuristicNum,numTargets):
        LogicalProcess.__init__(self)
        self.id = LogicalProcess.IMINT_ID
        self.heuristic=heuristicNum
        self.high=30
        self.low=10
        self.mode=15
        self.priorityAdjust=0.5
        self.totalValue=0
        self.targetsTracked=0
        self.numTargets=numTargets
        self.fname = os.path.abspath(os.path.join('DATA_FROM_'+str(time.time())+'.csv'))

    # Call function
    def __call__(self):
        self.run()
    
    # Save State
    # Input: None
    # Output: Saves current state of IMINT logical process
    # Description: Saves all parameters needed to describe state of LP
    def saveState(self):
        if(debug==1):
            print 'Saving current IMINT state'
        saver=IMINTState(self)
        self.stateQueue.append(saver)        
    
    # Restore State
    # Input: timestamp to restore to
    # Output: Restores past state of IMINT logical process
    # Description: Restores all parameters needed to describe state of LP    
    def restoreState(self, timestamp):
        if(debug==1):
            print 'restoring to last IMINT state stored <= %d' % (timestamp)
        index=0
        for i in range(len(self.stateQueue)-1,-1,-1):
            if(timestamp>=self.stateQueue[i].key):
                index=i
                break
            else:
                self.stateQueue.pop(i)            
        self.restore(self.stateQueue[index])
        
    # restores IMINT state to values contained in passed State object
    def restore(self,obj):
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
#            msg.data[9]+=1 # this is done in the drone.
            # check hueristic number
            if self.heuristic==1:
                # if goal track time has not been achieved, send updated tgt assignment to CAOC after processing time
                if (msg.data[8]/msg.data[7])<random.random():
                    # send message to CAOC process
                    newTgtData=msg.data
                    newTgtMsg=Message(2,newTgtData,self.id,'CAOC',self.localTime+random.triangular(self.high,self.low,self.mode))
                    self.sendMessage(newTgtMsg)
                else:
                    # if goal track time has been achieved, update the total value and number of tracked targets 
                    #    In the current implementation we allow IMINT to clear out it's backlog of unprocessed images at the sim end time
                    self.totalValue+=msg.data[1] # this isn't quite right - we don't really get this value until AFTER the processing time...but I'm trying to avoid a message here
                    self.targetsTracked+=1
                    if(debug==1):
                        print 'Total Value: ' + str(self.totalValue)
                        print 'Total Targets Tracked: ' + str(self.targetsTracked)
                    csvLock.acquire()
                    oufile=open(self.fname, "a")
                    c = csv.writer(oufile)
                    c.writerow([msg.data[0],msg.sender,msg.data[1],msg.data[2],msg.data[3],msg.data[4],msg.data[5],msg.data[7],msg.data[8],msg.data[9],self.heuristic,msg.timestamp])
                    oufile.close()
                    csvLock.release()
            elif self.heuristic==3 or self.heuristic==2:
                if (msg.data[8]/msg.data[7])<random.random():
                    # if goal track time has not been achieved, adjsut priority and send updated tgt assignment to CAOC after processing time
                    newTgtData=[msg.data[0],msg.data[1],self.priorityAdjust*msg.data[2],msg.data[3],msg.data[4],msg.data[5],msg.data[6],msg.data[7],msg.data[8],msg.data[9]]
                    newTgtMsg=Message(2,newTgtData,self.id,'CAOC',self.localTime+random.triangular(self.high,self.low,self.mode))
                    self.sendMessage(newTgtMsg)
                else:
                    # if goal track time has been achieved, update the total value and number of tracked targets 
                    #    In the current implementation we allow IMINT to clear out it's backlog of unprocessed images at the sim end time                    
                    self.totalValue+=msg.data[1] # this isn't quite right - we don't really get this value until AFTER the processing time...but I'm trying to avoid a message here
                    self.targetsTracked+=1
                    if(debug==1):
                        print 'Total Value: ' + str(self.totalValue)
                        print 'Total Targets Tracked: ' + str(self.targetsTracked)
                    csvLock.acquire()
                    oufile=open(self.fname, "a")
                    c = csv.writer(oufile)
                    c.writerow([msg.data[0],msg.sender,msg.data[1],msg.data[2],msg.data[3],msg.data[4],msg.data[5],msg.data[7],msg.data[8],msg.data[9],self.heuristic,msg.timestamp])
                    oufile.close()
                    csvLock.release()
                        
        elif msg.msgType==3:
            # print error message
            print 'IMINT Error: Received Message Type 3 from ' + str(msg.sender) + ' at ' + str(msg.recipient)
        if(debug==1):
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
        
        hmintInQ_uri = nameserver.lookup('inputqueue.hmint')
        self.hmintInQ = Pyro4.Proxy(hmintInQ_uri)
        LPIDs.append(self.hmintInQ.LPID)        
        
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
        
        loopInQs_uri = nameserver.lookup('inL.loop')
        self.Loopcont = Pyro4.Proxy(loopInQs_uri)
        
        self.initGVTCounts(LPIDs)
        print "Writing out to:",self.fname
        sys.stdout.flush()
        #setup output
        csvLock.acquire()
        oufile=open(self.fname, "w+")
        c = csv.writer(oufile)
        c.writerow(["Tgt ID","DroneId","Tgt Intel Value","Tgt Intel Priority","Tgt Type","Tgt Stealth","Tgt Speed","Tgt Goal Track Time","Tgt Actual Track Time","Tgt Track Attempts","heuristic", "Timestamp"])
        oufile.close()
        csvLock.release()
        
        
        ## Event loop iteration
        count=0
        while self.targetsTracked*2<self.numTargets :
            count+=1
            if(count%5000==0):
                print 'IMINT loop iteration'
                print "Imint has tracked", self.targetsTracked,"Targets.",self.numTargets-self.targetsTracked,"Targets to go."
            msg = self.getNextMessage()
            #print msg
            if msg:
                self.handleMessage(msg)
                if msg.msgType==2:
                    if(debug==1):
                        print "IMINT passed a traget"
            

        self.Loopcont.setCon(0)
        if(debug==1):
            print "IMINT IS DONE!!!!! FINISHED!!!! WOOOO!!!"

        time.sleep(2)

