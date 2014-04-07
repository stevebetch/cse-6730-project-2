import sys

class Message:
    
    nextMsgID = 0
    
    def getNextMessageID():
        msgID = Message.nextMsgID
        nextMsgID += 1
        return msgID
    
    def __init__(self, id, msgType, data, sender, recipient, timestamp):
        isAntiMessage = 'false'
        self.id = id
        self.msgType = msgType
        self.data = data
        self.sender = sender
        self.recipient = recipient
        self.timestamp = timestamp
        
    def getAntiMessage(self):
        antimsg = Message(self.msgType, self.id, self.data, self.sender, self.recipient, self.time)
        antimsg.isAntiMessage = true
        return antimsg    