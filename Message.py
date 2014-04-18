import sys

class Message:
    
    # For MsgID (NOT USED) (saving code in case we change our minds)
    nextMsgID = 0
    
    # Update Message ID Function
    # Description: Iterate message ID to provide unique ids for new messages
    # Input: None
    # Output: Message ID integer
    def getNextMessageID(self):
        msgID = Message.nextMsgID
        Message.nextMsgID += 1
        return msgID
    
    # Initialize Message Function
    # Description: Creates message of any type to be passed to another LP
    # Input: 5 arguments
    #   msgType: 1, 2, or 3 - 1 for Sim Control, 2 for Target Assignment, 3 for Status Report
    #   data: Depends on msgType, may be 1x?, 1x9, or 1x2 vector
    #       Msg Type 1: 1x? with ?
    #       Msg Type 2: 1x10 list of 
    #           Tgt ID: unique integer id for targets
    #           Tgt Intel Value: Real number from 0 to 100. 0 is low, 100 is high value
    #           Tgt Intel Priority: Real number from -100 to 100. Default is to match Tgt Intel Value but can be adjusted by LPs
    #           Tgt Type: "Vehicle" or "Pedestrian"
    #           Tgt Stealth: Real number from 0 to 2 to multiply base acq probabilities
    #           Tgt Speed: Real number from 0 to 2 to multiply base route speeds
    #           Tgt Predicted Location: [X,Y] x,y coord of tgt (possible to change to node itself?)
    #           Tgt Goal Track Time: Integer from 0 to 360 minutes of goal visual contact between drone and target
    #           Tgt Actual Track Time: Integer from 0 to 360 minutes of actual visual contact achieved
    #           Tgt Track Attempts: Integer >= 0 recording number of attempts at tracking target
    #       Msg Type 3: 1x3 list of
    #           Drone ID: unique integer id for drones
    #           Drone Busy Status: "Busy" or "Idle"
    #           Drone Location: [X,Y] x,y coord of node (possible to change to node itself?)
    #   sender: Unique integer id of sender LP
    #   recipient: Unique integer id of recipient LP
    #   timestamp: Sim time corresponding to message
    # Output: None.  
    def __init__(self, msgType, data, sender, recipient, timestamp, uid=None):
        if uid is None:
            self.id = self.getNextMessageID()            
        else:
            self.id = uid
        self.isAnti = 0
        self.msgType = msgType
        self.data = data
        self.sender = sender
        self.recipient = recipient
        self.timestamp = timestamp
        
    def __eq__(self, other): 
        return self.__dict__ == other.__dict__   
    
    def clone(self):
        return Message(self.msgType, self.data, self.sender, self.recipient, self.timestamp, self.id)
    
    def setColor(self, color):
        self.color = color
    
    # Anti Message Function (IN PROGRESS)
    # Description: Creates an anti-message from an existing message
    # Input: None/Message
    # Output: Anti Message    
    def getAntiMessage(self):
        antimsg = self.clone()
        antimsg.isAnti = 1
        return antimsg
    
    def isAntiMessage(self):
        return self.isAnti

    # Print Data Function
    # Description: Display attributes of Message instance
    # Input: 0 or 1. Enter 0 for primary message info only, 1 for comlete message data
    # Output: Prints Message attributes to command line
    def printData(self,x):
        # Primary Message Information
        print "-------Primary Message Information-------"
        print "Message Type: " + str(self.msgType)
        print "Message Sender: " + str(self.sender)
        print "Message Recipient: " + str(self.recipient)
        print "Message Timestamp: " + str(self.timestamp)
        # Complete Message Data
        # Message data differs by message type
        if x==1:
            if self.msgType==1:
                print "---Sim Control Data---"
                print "placeholder" # replace placeholder
            elif self.msgType==2:
                print "---Target Assignment Data---"
                print "Tgt ID: " + str(self.data[0])
                print "Tgt Intel Value: " + str(self.data[1])
                print "Tgt Intel Priority: " + str(self.data[2])
                print "Tgt Type: " + str(self.data[3])
                print "Tgt Stealth: " + str(self.data[4])
                print "Tgt Speed: " + str(self.data[5])
                print "Tgt Predicted Location: " + str(self.data[6])
                print "Tgt Goal Track Time: " + str(self.data[7])
                print "Tgt Actual Track Time: " + str(self.data[8])
                print "Tgt Track Attempts: " + str(self.data[9])
            elif self.msgType==3:
                print "---Status Data---"
                print "Drone ID: " + str(self.data[0])
                print "Drone Busy Status: " + str(self.data[1])
                print "Drone Location: " + str(self.data[2])


# Debugging

# # Example message 2
# # This is a "Target Assignment" Message
# # We can tell being sent from LP1 HUMINT/CAOC to a Drone LP because of the sender/recipient fields (and the "Tgt Actual Track Time" is set to 0)
# tgt_data=[1,85,85,"Vehicle",0.8,1.2,[3,10],30,0,0]
# tgt_assign=Message(2,tgt_data,1,5,6)
# tgt_assign.printData(1)

# # Example message 3
# # This is a "Status" Message
# # Right now this is drone specific, but we could modify easily if necessary
# status_data=[3,"Idle",[3,10]]
# status_msg=Message(3,status_data,5,1,11)
# status_msg.printData(1)

