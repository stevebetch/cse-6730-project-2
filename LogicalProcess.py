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
        self.stateQueue = []
        self.outputQueue = {}
        self.inputMsgHistory = []
        self.localTime = 0
        self.gvt = 0
        
    def sendMessage(self, msg):
        if (msg.isAntiMessage()):
            print 'sending anti-message with timestamp %s' % (msg.timestamp)
        else:
            print 'sending message with timestamp %s' % (msg.timestamp)
        if (msg.recipient == 'CAOC'):
            self.caocInQ.addMessage(msg)
        elif (msg.recipient == 'IMINT'):
            self.imintInQ.addMessage(msg)
        elif (msg.recipient == 'Controller'):
            self.controllerInQ.addMessage(msg)
        else:
            # Drone
            self.droneInQs.addMessage(msg.recipient, msg) # assumes recipient set to drone's ID in msg
            
        self.saveAntiMessage(msg)
    
    def rollback(self, msg):
        
        print 'ROLLBACK!!'
        # restore state to that at time of straggler message
        self.restoreState(msg.timestamp) # define restoreState(timestamp) in subclass
        
        # send anti-messages for all messages sent after straggler message
        for uid in self.outputQueue:
            if self.outputQueue[uid].timestamp > msg.timestamp:
                self.sendMessage(self.outputQueue[uid])
                
        # set local time to time of straggler, prevents recursive calling of rollback message
        self.localTime = msg.timestamp
        
        # append messages processed after this time to input queue for reprocessing
        reprocessList = []
        for histMsg in self.inputMsgHistory:
            if histMsg.timestamp > msg.timestamp:
                reprocessList.append(histMsg)
        reprocessList.sort(key=lambda x: x.timestamp, reverse=True)
        self.inputQueue.extend(reprocessList)
        
        # process straggler if not an anti-message
        if (not msg.isAntiMessage()):
            self.handleMessage(msg)
    
    def handleMessage(self, msg):
        # handle LogicalProcess messages (GVT, etc) here
        if msg.timestamp < self.localTime:
            self.rollback(msg)
        else:
            self.saveState() #define getCurrentState() in subclass
            self.setLocalTime(msg.timestamp)
            self.inputMsgHistory.append(msg.clone())
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
            elif (firstMsg.timestamp <= self.localTime):
                print 'Found First Message (AntiMessage w/ ts <= localTime)'
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
                        if (firstMsg.timestamp <= self.localTime):
                            print 'Found Message (AntiMessage w/ ts <= localTime)'
                            return currMsg
                        else:
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
        self.outputQueue[msg.id] = antimsg
                
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
            