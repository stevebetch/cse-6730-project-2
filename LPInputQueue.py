import Queue

class LPInputQueue():
    
    def __init__(self):
        self.q = list()
        
    def hasMessages(self):
        hasMsgs = 0
        if len(self.q) > 0:
            hasMsgs = 1
        return hasMsgs
        
    def setCurrentTime(self, time):
        self.currTime = time
        
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
        if msg.isAntiMessage:
            # check if matching message is still in input queue, if so annihalate both
            match = None
            for m in self.q:
                if (m.id == msg.id) and (not m.isAntiMessage):
                    match = m
            if match:
                self.q.remove(match)
                return            
            # matching message already processed or not yet received
            #if msg.timestamp <= self.currTime:
                ## message already processed
                #self.insertAtFront(msg) # will trigger rollback
            else:
                # message not yet received
                self.q.insert(0, msg) #inserts at end of input queue 
        else:
            # regular message, check if matching anti-message is already in input queue, if so annihalate both
            match = None
            for m in self.q:
                if (m.id == msg.id) and (m.isAntiMessage):
                    match = m
            if match:
                self.q.remove(match)
                return        
            # check if time is before currTime, if so then do rollback
            #if msg.time <= self.currTime:
                #self.insertAtFront(msg) # will trigger rollback
            else:
                self.q.insert(0, msg) #inserts at end of queue
                        
                