import sys
from Message import *
from multiprocessing.managers import SyncManager
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
        
        # restore state to that at time of straggler message
        self.restoreState(msg.timestamp) # define restoreState(timestamp) in subclass
        
        # send anti-messages for all messages sent after straggler message
        for id in outputQueue.keys:
            if outputQueue[id].timestamp >= msg.timestamp:
                self.sendMessage(outputQueue[id])
                
        # set local time to time of straggler, 
        # this also ensures messages processed after this time will be re-processed
        self.localTime = msg.timestamp
        
        # process straggler
        self.handleMessage(msg)
    
    def handleMessage(self, msg):
        # handle LogicalProcess messages (GVT, etc) here, then call subclass method to handle class-specific behavior
        pass
    
    def processNextMessage(self):
        if len(inputQueue) > 0:
            # Get next message, including check if it is an anti-message
            foundMsg = 0
            for i in len(inputQueue):
                msg = inputQueue.pop()
                if (msg.isAntiMessage()):
                    # put it back and get another one
                    inputQueue.insert(0, msg)
                else:
                    foundMsg = 1
                    break
                
            # valid message: save state, set local time to time of message, and handle the message
            if foundMsg:
                stateQueue.put(localTime, getCurrentState()) #define getCurrentState() in subclass
                localTime = msg.timestamp
                handleMessage(msg)
        
    def sendMessage(self, msg, receiver):
        antimsg = msg.getAntiMessage()
        outputQueue.put(msg.id, antimsg)
        send(msg) # need to implement using multiprocessing queues
        
    def receiveMessage(self, msg):
        if msg.isAntiMessage:
            # check if matching message is still in input queue, if so annihalate both
            match = None
            for m in inputQueue:
                if (m.id == msg.id) and (not m.isAntiMessage):
                    match = m
            if match:
                inputQueue.remove(match)
                return            
            # matching message already processed or not yet received
            if msg.timestamp <= self.localTime:
                # message already processed
                rollback(msg)
            else:
                # message not yet received
                inputQueue.insert(0, msg) #inserts at beginning of input queue
        else:
            # regular message, check if matching anti-message is already in input queue, if so annihalate both
            match = None
            for m in inputQueue:
                if (m.id == msg.id) and (m.isAntiMessage):
                    match = m
            if match:
                inputQueue.remove(match)
                return        
            # check if time is before currTime, if so then do rollback
            if msg.time <= currTime:
                rollback(msg)
            else:
                inputQueue.insert(0, msg) #inserts at beginning of input queue
                
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
            