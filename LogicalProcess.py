import sys
from Message import *

class LogicalProcess:
    
    # instance variable list
    #inputqueue
    #statequeue
    #outputqueue
    #currTime
    #gvt
    
    # also need list of previously processed messages??
    
    def __init__(self):
        pass
    
    def rollback(self, msg):
        # restore state to last state saved before msg.time
        # send anti-messages for any messages sent after msg.time
        # process msg
        # re-process rolled-back messages
        pass
    
    def processNextMessage(self):
        saveState(time, getCurrentState())
        msg = inputqueue.get()
        currTime = msg.time
        handleMessage(msg)
        
    def sendMessage(self, msg):
        antimsg = msg.getAntiMessage()
        addToOutputQueue(antimsg)
        send(msg)
        
    def receiveMessage(self, msg):
        if msg.isAntiMessage:
            # handle receipt of anti-message
            # check if matching message is still in input queue, if so annihalate both
            pass
            # else
            if msg.time < currTime: # or actually check if orig message already processed?
                rollback(msg)
            else:
                addToInputQueue(msg)
        else:
            # check if matching anti-message is already in input queue, if so annihalate both
            pass
            # check if time is before currTime, if so then do rollback
            if msg.time < currTime:
                rollback(msg)
            else:
                addToInputQueue(msg)
                
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
            