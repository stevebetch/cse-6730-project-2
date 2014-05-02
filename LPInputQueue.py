import Queue
from GVT import *

# Input message queue for a logical process
class LPInputQueue():
    
    def __init__(self):
        self.q = list()
        self.localTMin = 0
        self.LPID = None
        
    # prints contents of queue
    def dump(self):
        if(debug==1):
            if len(self.q) == 0:
                print 'Empty'
            else:
                for i in self.q:
                    i.printData(0)
       
    # sets the LPID value for the input queue 
    def setLPID(self, lpid):
        self.LPID = lpid
      
    # gets the LPID value  
    def getLPID(self):
        return self.LPID
       
    # gets the length of the input queue 
    def getLength(self):
        return len(self.q)
    
    # appends the contents of the given list to the end of this queue
    def extend(self, list):
        self.q.extend(list)
      
    # tells whether this input queue contains messages  
    def hasMessages(self):
        hasMsgs = 0
        if len(self.q) > 0:
            hasMsgs = 1
        return hasMsgs
       
    # sets the local time currently associated with the input queue 
    def setLocalTime(self, time):
        self.localTime = time
        
    # Gets the number of white messages contained in the input queue
    def numWhiteMessages(self):
        count = 0
        for msg in self.q:
            if msg.color == LPGVTData.WHITE:
                count += 1
        return count

    # Puts the given message in the queue without the normal checks
    def justPut(self, msg):
        self.q.insert(0, msg)
        
    # adds the given message to the queue, with the normal checks
    def addMessage(self, msg):
        self.insertAtBack(msg)
        
    # removes the given message from the queue
    def remove(self, msg):
        self.q.remove(msg) 
        
    # Removes the message with the given ID from the queue
    def removeByID(self, msgId):
        removeMsg = None
        for msg in self.q:
            if msg.id == msgId:
                removeMsg = msg
        if not(removeMsg is None):
            self.q.remove(removeMsg)
      
    # Gets the next message from the queue, normally the message with the lowest timestamp.
    # Also includes normal checks for anti-messages and other special cases.
    def getNextMessage(self):
        
        if len(self.q) == 0:
            return None
        
        msg = None
        removeMsg = None
        smallestTimestamp = 99999999999999
        for currMsg in self.q:
            if currMsg is None:
                # catch the case of null message
                removeMsg = currMsg                
            if currMsg.msgType == 1:
                # handle control messages first
                msg = currMsg            
            elif currMsg.isAntiMessage():
                if currMsg.timestamp <= self.localTime:
                    # need to process this
                    # antimessage, which may trigger rollback
                    smallestTimestamp = currMsg.timestamp
                    msg = currMsg
                else:
                    # corresponding message hasn't arrived yet, leave in queue
                    continue
            # regular message
            elif currMsg.timestamp < smallestTimestamp:
                smallestTimestamp = currMsg.timestamp
                msg = currMsg
                
        if not(removeMsg is None):
            self.q.remove(removeMsg)
            
        if not(msg is None):
            self.q.remove(msg)                    
        return msg
    
    # gets a list of all messages in the queue
    def getAllMessages(self):
        msgs = []
        for msg in self.q:
            msgs.append(msg)
        return msgs
    
    # Calculates the local tMin for the queue, which is the timestamp of the lowest-
    # timestamp message in the queue
    def calculateLocalTMin(self):
        self.localTMin = self.localTime
        for msg in self.q:
            if msg.timestamp >= 0:
                if msg.timestamp < self.localTMin:
                        self.localTMin = msg.timestamp
        return self.localTMin
    
    # inserts a message at the front of the queue
    def insertAtFront(self, msg):
        if msg.timestamp < self.localTMin:
            self.localTMin = msg.timestamp        
        self.q.append(msg)
        
    # Inserts into the queue, but also contains logic to identify and handle anti-messages,
    # annihilation, etc.
    def insertAtBack(self, msg):
        if msg.timestamp < self.localTMin:
            self.localTMin = msg.timestamp        
        if msg.isAntiMessage():
            # check if matching message is still in input queue, if so annihalate both
            match = None
            for m in self.q:
                if (m.id == msg.id) and (not m.isAntiMessage()):
                    match = m
            if match:
                if(debug==1):
                    print 'Found match for anti-message, both are ANNIHILATED!'
                self.q.remove(match)
                return            
            # matching message already processed or not yet received
            if msg.timestamp <= self.localTime:
                # message already processed
                self.insertAtFront(msg) # will trigger rollback
                if(debug==1):
                    print 'Received anti-message in the past'
            else:
                # message not yet received
                self.q.insert(0, msg) #inserts at end of input queue
                if(debug==1):
                    print 'Matching message for anti-message not yet received'
        else:
            # regular message, check if matching anti-message is already in input queue, if so annihalate both
            match = None
            for m in self.q:
                if (m.isAntiMessage()):
                    mid = m.id
                    msgid = msg.id
                    if (m.id == msg.id):
                        match = m
            if match:
                if(debug==1):
                    print 'Anti-message for message found, both are ANNIHILATED!'
                self.q.remove(m)
                return        
            # check if time is before currTime
            if msg.timestamp < self.localTime:
                self.insertAtFront(msg) # will trigger rollback
                if not(isinstance(msg.data, GVTControlMessageData)) and not(isinstance(msg.data, GVTValue)):
                    
                    print 'Straggler message found, should trigger rollback'
            else:
                # normal case adds valid message to queue
                self.q.insert(0, msg)
                if(debug==1):
                    print 'Adding message to queue'
                        
                