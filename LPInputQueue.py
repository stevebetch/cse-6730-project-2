import Queue
from GVT import *

class LPInputQueue():
    
    def __init__(self):
        self.q = list()
        self.localTMin = 0
        self.LPID = None
        
    def dump(self):
        if(debug==1):
            if len(self.q) == 0:
                print 'Empty'
            else:
                for i in self.q:
                    i.printData(0)
        
    def setLPID(self, lpid):
        self.LPID = lpid
        
    def getLPID(self):
        return self.LPID
        
    def getLength(self):
        return len(self.q)
    
    def extend(self, list):
    
        self.q.extend(list)
    
    def hasMessages(self):
        hasMsgs = 0
        if len(self.q) > 0:
            hasMsgs = 1
        return hasMsgs
        
    def setLocalTime(self, time):
        self.localTime = time
        
    def numWhiteMessages(self):
        count = 0
        for msg in self.q:
            if msg.color == LPGVTData.WHITE:
                count += 1
        return count
        
    def justPut(self, msg):
        self.q.insert(0, msg)
        
    def addMessage(self, msg):
        self.insertAtBack(msg)
        
    def remove(self, msg):
        self.q.remove(msg) 
        
    def removeByID(self, msgId):
        removeMsg = None
        for msg in self.q:
            if msg.id == msgId:
                removeMsg = msg
        if not(removeMsg is None):
            self.q.remove(removeMsg)
        
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
    
    def getAllMessages(self):
        msgs = []
        for msg in self.q:
            msgs.append(msg)
        return msgs
    
    def calculateLocalTMin(self):
        self.localTMin = self.localTime
#        if self.LPID is None:
#            print 'Controller calculateLocalTMin()'
#        else:
#            print 'LP %d calculateLocalTMin()' % (self.LPID)
#        print 'Local Time = %d' % (self.localTime)
        for msg in self.q:
#            print 'msg.timestamp = %d' % (msg.timestamp)
            if msg.timestamp >= 0:
                if msg.timestamp < self.localTMin:
                        self.localTMin = msg.timestamp
#        print 'tMin = %d' % (self.localTMin)
        return self.localTMin
    
    def insertAtFront(self, msg):
        if msg.timestamp < self.localTMin:
            self.localTMin = msg.timestamp        
        self.q.append(msg)
        self.q=self.sortAndUniq()

    def sortAndUniq(self):
        output = []
        for x in self.q:
            if x not in output:
                output.append(x)
        output.sort()
        return output
        
        for v in removal:
            self.q.remove(v)


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
            # check if time is before currTime, if so then do rollback
            if msg.timestamp < self.localTime:
                self.insertAtFront(msg) # will trigger rollback
                if not(isinstance(msg.data, GVTControlMessageData)) and not(isinstance(msg.data, GVTValue)):
                    if(1):
                        print 'Straggler message found, should trigger rollback'
            else:
                self.q.insert(0, msg) #inserts at end of queue
                if(debug==1):
                    print 'Adding message to queue'
                        
                