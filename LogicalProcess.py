import sys
from Message import *
from SharedMemoryClient import *


class LogicalProcess(SharedMemoryClient):
    # Implements Time Warp Local Control Mechanism
    
    # instance variable list
    #inputQueue - FIFO queue for incoming messages
    #stateQueue - dictionary of timestamp (keys) to state object (values)
    #outputQueue - dictionary of message id (keys) to antimessage (values)
    #localTime - current time logical process is at
    #gvt - last gvt value received from controller
    
    
    def __init__(self):      
        self.stateQueue = {}
        self.outputQueue = {}
        self.localTime = 0
        self.gvt = 0
    
    def rollback(self, msg):
        
        print 'ROLLBACK!!'
        # restore state to that at time of straggler message
        self.restoreState(msg.timestamp) # define restoreState(timestamp) in subclass
        
        # send anti-messages for all messages sent after straggler message
        for uid in self.outputQueue:
            if self.outputQueue[uid].timestamp >= msg.timestamp:
                self.sendMessage(outputQueue[uid])
                
        # set local time to time of straggler, 
        # TODO: also need to ensure messages processed after this time will be re-processed
        self.localTime = msg.timestamp
        
        # process straggler
        self.handleMessage(msg)
    
    def handleMessage(self, msg):
        # handle LogicalProcess messages (GVT, etc) here
        if msg.timestamp < self.localTime:
            self.rollback(msg)
        else:
            self.stateQueue[self.localTime] = self.getCurrentState() #define getCurrentState() in subclass
            self.setLocalTime(msg.timestamp)
            msg.printData(1)            
            self.subclassHandleMessage(msg)
    
    def getNextMessage(self):
        msg = None       
        if self.inputQueue.hasMessages():
            # peek at first message
            firstMsg = self.inputQueue.getNextMessage()
            if firstMsg is None:
                self.inputQueue.remove(firstMsg)
            elif (not firstMsg.isAntiMessage()):
                #print 'Found First Message (not an AntiMessage)'
                return firstMsg
            else:
                #print 'Found First Message is an AntiMessage, returning to queue'
                self.inputQueue.justPut(firstMsg)
                # loop until non-antiMessage is found
                while True:
                    currMsg = self.inputQueue.getNextMessage()
                    if currMsg == firstMsg:
                        self.inputQueue.justPut(currMsg)
                        #print 'All messages in queue are AntiMessages'
                        break
                    if (currMsg.isAntiMessage()):
                        # put it back and get another one
                        #print 'Found AntiMessage, returning to queue'
                        self.inputQueue.justPut(currMsg)
                    else:
                        #print 'Found Message'
                        msg = currMsg
                        break
        return msg        
                
    def setLocalTime(self, time):
        self.localTime = time
        self.inputQueue.setLocalTime(time)        
        
    def saveAntiMessage(self, msg):
        antimsg = msg.getAntiMessage()
        outputQueue.put(msg.id, antimsg)
                
    def getLocalMinTimeForGVT(self):
        pass
    
    def setGVT(self, gvt):
        self.gvt = gvt
        releaseResources(gvt)
        executeIO(gvt)
        
    def releaseResources(self):
        # delete items in state/output queues prior to GVT
        pass
    
    def executeIO(gvt):
        # commit IO operations for times prior to GVT
        pass
            