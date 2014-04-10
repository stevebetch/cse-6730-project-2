import sys
from LogicalProcess import *


class IMINT (LogicalProcess):
    
    # instance variable list
    #id - unique id for component
    #controller - the simulation executive   
        
    def __init__(self):
        self.id = 'IMINT'
        LogicalProcess.__init__(self)
    
    def __call__(self):
        self.run()
            
    def handleMessage(self, msg):
        # determine message type and process accordingly
        pass
    
    def run(self):
        
        print('IMINT Running')
    
        # connect with Queue manager        
        qclient = self.QueueServerClient(self.REMOTE_HOST, self.PORT, self.AUTHKEY)
        
        # Get the message queue objects from the client
        inputQueues = qclient.get_queues()
        controllerInQ = inputQueues.get("controller")
        inputQueue = inputQueues.get("imint")
        caocInQ = inputQueues.get("caoc")
        
        print inputQueue.get()
        