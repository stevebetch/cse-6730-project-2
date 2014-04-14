import Queue

class LPInputQueue():
    
    def __init__(self):
        self.q = list()
        
    def getLength(self):
        return len(self.q)
        
    def hasMessages(self):
        hasMsgs = 0
        if len(self.q) > 0:
            hasMsgs = 1
        return hasMsgs
        
    def setLocalTime(self, time):
        self.localTime = time
        
    def justPut(self, msg):
        self.q.insert(0, msg)
        
    def addMessage(self, msg):
        self.insertAtBack(msg)
        
    def getNextMessage(self):
        if len(self.q) == 0:
            return None
        return self.q.pop()
    
    def insertAtFront(self, msg):
        self.q.append(msg)
        
    def insertAtBack(self, msg):
        if msg.isAntiMessage():
            # check if matching message is still in input queue, if so annihalate both
            match = None
            for m in self.q:
                if (m.id == msg.id) and (not m.isAntiMessage()):
                    match = m
            if match:
                print 'Found match for anti-message, annihilating both'
                self.q.remove(match)
                return            
            # matching message already processed or not yet received
            if msg.timestamp <= self.localTime:
                # message already processed
                self.insertAtFront(msg) # will trigger rollback
                print 'Matching message for anti-message has already been processed'
            else:
                # message not yet received
                self.q.insert(0, msg) #inserts at end of input queue 
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
                print 'Anti-message for message found, annihilate both'
                self.q.remove(m)
                return        
            # check if time is before currTime, if so then do rollback
            if msg.timestamp <= self.localTime:
                self.insertAtFront(msg) # will trigger rollback
                print 'Straggler message found, should trigger rollback'
            else:
                self.q.insert(0, msg) #inserts at end of queue
                print 'Adding message to queue'
                        
                