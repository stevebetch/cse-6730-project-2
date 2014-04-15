from IMINT import *
from LPInputQueue import *
from Message import *
from multiprocessing import Process
import sys, time
import Pyro4

class ProducerClient():
    
    def __init__(self):
        pass
    
    def __call__(self):
        self.run()
        
    def run(self):

        print('Producer Client Running')

        # Get the message queue objects from Pyro    
        nameserver = Pyro4.locateNS()
        imintInQ_uri = nameserver.lookup('inputqueue.imint')
        imintInQ = Pyro4.Proxy(imintInQ_uri)

        #Test 1 - single message
        #imintInQ.addMessage(Message(1, 'Data', 'Test Message Generator', 'IMINT', 5))
        
        #Test 2 - multiple messages
        #imintInQ.addMessage(Message(1, ['Data1'], 'Test Message Generator', 'IMINT', 1))
        #imintInQ.addMessage(Message(1, ['Data2'], 'Test Message Generator', 'IMINT', 2))
        #imintInQ.addMessage(Message(1, ['Data3'], 'Test Message Generator', 'IMINT', 3))
        #imintInQ.addMessage(Message(1, ['Data4'], 'Test Message Generator', 'IMINT', 4))
        
        #Test 3 - an AntiMessage first
        #am = Message(1, ['Data1'], 'Test Message Generator', 'IMINT', 1)
        #am.isAnti = 1
        #imintInQ.addMessage(am)
        #imintInQ.addMessage(Message(1, ['Data2'], 'Test Message Generator', 'IMINT', 2))
        
        #Test 4 - an AntiMessage second
        #am = Message(1, ['Data1'], 'Test Message Generator', 'IMINT', 1)
        #am.isAnti = 1
        #imintInQ.addMessage(Message(1, ['Data2'], 'Test Message Generator', 'IMINT', 2))  
        #imintInQ.addMessage(am)
        
        #Test 5 - lots of antimessages
        #am = Message(1, ['Data1'], 'Test Message Generator', 'IMINT', 1)
        #am.isAnti = 1
        #am1 = Message(1, ['Data1'], 'Test Message Generator', 'IMINT', 2)
        #am1.isAnti = 1
        #am2 = Message(1, ['Data1'], 'Test Message Generator', 'IMINT', 3)
        #am2.isAnti = 1 
        #am3 = Message(1, ['Data1'], 'Test Message Generator', 'IMINT', 4)
        #am3.isAnti = 1
        #imintInQ.addMessage(am)
        #imintInQ.addMessage(am1)
        #imintInQ.addMessage(am2)
        #imintInQ.addMessage(am3)
        #imintInQ.addMessage(Message(1, ['Data2'], 'Test Message Generator', 'IMINT', 5))
        
        #Test 6 - Anti-message for message already in queue
        #msg1 = Message(1, ['Data1'], 'Test Message Generator', 'IMINT', 1)
        #am = msg1.getAntiMessage()
        #imintInQ.addMessage(am)
        #imintInQ.addMessage(msg1) 
        
        #Test 7 - Message for anti-message already in queue
        #msg1 = Message(1, ['Data1'], 'Test Message Generator', 'IMINT', 1)
        #am = msg1.getAntiMessage()
        #imintInQ.addMessage(msg1)  
        #imintInQ.addMessage(am)  
        
        #Test 8 = Rollback caused by straggler message
        #msg3 = Message(1, ['Data1'], 'Test Message Generator', 'IMINT', 3)
        #msg4 = Message(1, ['Data1'], 'Test Message Generator', 'IMINT', 4)
        #msg7 = Message(1, ['Data1'], 'Test Message Generator', 'IMINT', 7)
        #imintInQ.addMessage(msg4)
        #imintInQ.addMessage(msg7)
        #imintInQ.addMessage(msg3) 
        
        #Test 9 - Rollback caused by anti-message
        msg3 = Message(1, ['Data1'], 'Test Message Generator', 'IMINT', 3)
        msg7 = Message(1, ['Data1'], 'Test Message Generator', 'IMINT', 7)
        am3 = msg3.getAntiMessage()
        imintInQ.addMessage(msg3)        
        imintInQ.addMessage(msg7)
        time.sleep(1)
        imintInQ.addMessage(am3)           

PYRO_HOST = '192.168.0.3'
PYRO_PORT = 12778
    
#
# Main method
#

def main():
    
    # Create PYRO remote object daemon
    daemon = Pyro4.Daemon(host=PYRO_HOST, port=PYRO_PORT)
    ns = Pyro4.locateNS()     
    
    # Create input queue instance to share
    imintInQ = LPInputQueue()
    imintInQ.setLocalTime(0)
    uri = daemon.register(imintInQ)
    ns.register('inputqueue.imint', uri)
    caocInQ = LPInputQueue()
    caocInQ.setLocalTime(0)
    uri1 = daemon.register(caocInQ)
    ns.register('inputqueue.caoc', uri1)    
    
    # Producer Client
    pc1 = ProducerClient()
    pPc1 = Process(group=None, target=pc1, name='Test Message Producer Process')
    pPc1.start() 
    
    # Consumer Client (IMINT)
    imint = IMINT()
    pIMINT = Process(group=None, target=imint, name='IMINT Process')
    pIMINT.start()       
    
    # Run shared object requests loop
    print 'starting shared objects request loop'
    daemon.requestLoop()
        
#
# Start of Execution
#
if __name__ == '__main__':
    main()