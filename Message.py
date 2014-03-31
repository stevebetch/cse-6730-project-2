import sys

class Message:
    
    isAntiMessage
    msgType
    data
    sender
    recipient
    time
    
    def __init__(self, msgType, data, sender, recipient, time):
        isAntiMessage = false
        self.msgType = msgType
        self.data = data
        self.sender = sender
        self.recipient = recipient
        self.time = time
        
    def getAntiMessage(self):
        antimsg = Message(self.msgType, self.data, self.sender, self.recipient, self.time)
        antimsg.isAntiMessage = true
        return antimsg    