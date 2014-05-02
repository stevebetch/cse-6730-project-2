from StubLP import *
from StubDrone import *
from StubController import *
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
        stublpInQ_uri = nameserver.lookup('inputqueue.stublp')
        stublpInQ = Pyro4.Proxy(stublpInQ_uri)
        
        #
        # Messaging Tests: Uncomment one by one and run
        #

        #Test 1 - single message
        #stublpInQ.addMessage(Message(2, 'Data', 'Test Message Generator', LogicalProcess.STUBLP_ID, 5))
        
        #Test 2 - multiple messages
        #stublpInQ.addMessage(Message(2, 'Data1', 'Test Message Generator', LogicalProcess.STUBLP_ID, 1))
        #stublpInQ.addMessage(Message(2, 'Data2', 'Test Message Generator', LogicalProcess.STUBLP_ID, 2))
        #stublpInQ.addMessage(Message(2, 'Data3', 'Test Message Generator', LogicalProcess.STUBLP_ID, 3))
        #stublpInQ.addMessage(Message(2, 'Data4', 'Test Message Generator', LogicalProcess.STUBLP_ID, 4))
        
        #Test 3 - an AntiMessage first (expect annihilation)
        #msg = Message(2, 'Data1', 'Test Message Generator', LogicalProcess.STUBLP_ID, 1)
        #am = msg.getAntiMessage()
        #stublpInQ.addMessage(am)
        #stublpInQ.addMessage(msg)
        
        #Test 4 - message for antimessage is already in the queue (expect annihilation)
        #msg = Message(2, 'Data1', 'Test Message Generator', LogicalProcess.STUBLP_ID, 1)
        #am = msg.getAntiMessage()
        #stublpInQ.addMessage(msg)  
        #stublpInQ.addMessage(am)
        
        #Test 5 - lots of antimessages
        #am = Message(2, 'Data1', 'Test Message Generator', LogicalProcess.STUBLP_ID, 1)
        #am.isAnti = 1
        #am1 = Message(2, 'Data2', 'Test Message Generator', LogicalProcess.STUBLP_ID, 2)
        #am1.isAnti = 1
        #am2 = Message(2, 'Data3', 'Test Message Generator', LogicalProcess.STUBLP_ID, 3)
        #am2.isAnti = 1 
        #am3 = Message(2, 'Data4', 'Test Message Generator', LogicalProcess.STUBLP_ID, 4)
        #am3.isAnti = 1
        #stublpInQ.addMessage(am)
        #stublpInQ.addMessage(am1)
        #stublpInQ.addMessage(am2)
        #stublpInQ.addMessage(am3)
        #stublpInQ.addMessage(Message(2, 'Data5', 'Test Message Generator', LogicalProcess.STUBLP_ID, 5))
        
        #Test 6 - Anti-message for message already processed
        #msg1 = Message(2, 'Data1', 'Test Message Generator', LogicalProcess.STUBLP_ID, 1)
        #am = msg1.getAntiMessage()
        #stublpInQ.addMessage(msg1)
        #time.sleep(2)
        #stublpInQ.addMessage(am)         
        
        #Test 7 - Message for anti-message already in queue
        #msg1 = Message(2, 'Data1', 'Test Message Generator', LogicalProcess.STUBLP_ID, 1)
        #am = msg1.getAntiMessage()
        #stublpInQ.addMessage(msg1)  
        #stublpInQ.addMessage(am)  
        
        #Test 8 = Rollback caused by straggler message
        #msg3 = Message(2, 'Data3', 'Test Message Generator', LogicalProcess.STUBLP_ID, 3)
        #msg4 = Message(2, 'Data4', 'Test Message Generator', LogicalProcess.STUBLP_ID, 4)
        #msg7 = Message(2, 'Data7', 'Test Message Generator', LogicalProcess.STUBLP_ID, 7)
        #stublpInQ.addMessage(msg4)
        #stublpInQ.addMessage(msg7)
        #time.sleep(5)
        #stublpInQ.addMessage(msg3) 
        
        #Test 9 - Rollback caused by anti-message
        msg3 = Message(2, ['Data3'], 'Test Message Generator', LogicalProcess.STUBLP_ID, 3)
        msg7 = Message(2, ['Data7'], 'Test Message Generator', LogicalProcess.STUBLP_ID, 7)
        am3 = msg3.getAntiMessage()
        stublpInQ.addMessage(msg3)        
        stublpInQ.addMessage(msg7)
        time.sleep(5)
        stublpInQ.addMessage(am3) 
        
        #
        # GVT Tests
        #
        
        # Test 1: No messages
        # (don't need any messages for this test!)
        
        # Test 2: 3 messages to same drone (edit StubLP)
        # GVT will be 0
        
        # Test 3: 3 messages to drone, 1 to stub LP
        # GVT should be 3

PYRO_HOST = '192.168.0.3'
PYRO_PORT = 12778

def createNewDrone(uid):
    droneref = StubDrone(uid)
    droneref.setConnectionParams(PYRO_HOST, PYRO_PORT)
    return droneref
    
#
# Main method
#

def main():
    
    numDrones = 1
    
    # Create PYRO remote object daemon
    daemon = Pyro4.Daemon(host=PYRO_HOST, port=PYRO_PORT)
    ns = Pyro4.locateNS() 
    
    # Create input queue instance to share
    stublp = StubLP()
    stublp.setConnectionParams(PYRO_HOST, PYRO_PORT)    
    stublpInQ = LPInputQueue()
    stublpInQ.setLocalTime(0)
    stublpInQ.setLPID(stublp.LPID)
    uri = daemon.register(stublpInQ)
    ns.register('inputqueue.stublp', uri)   
    
    # Producer Client
    pc1 = ProducerClient()
    pPc1 = Process(group=None, target=pc1, name='Test Message Producer Process')
    pPc1.start() 
    
    # Consumer Client (StubLP)
    pStubLP = Process(group=None, target=stublp, name='StubLP Process')
    pStubLP.start()
    
    # Create Simulation Controller
    controller = StubController(stublp)
    controller.setConnectionParams(PYRO_HOST, PYRO_PORT)
    controllerInQ = LPInputQueue()
    controllerInQ.setLocalTime(0)
    controllerInQ_uri = daemon.register(controllerInQ)
    ns.register("inputqueue.stubcontroller", controllerInQ_uri)          
    
    # Stub drones
    # Create drone entities, each will be separate process started by Controller
    droneInQs = DroneInputQueueContainer()
    drones = []
    for i in range(numDrones):
        dronename = i
        print 'dronename is %s' % dronename
        drone = createNewDrone(dronename)
        drones.append(drone)
        controller.addDrone(drone)
        droneInQs.addDroneInputQueue(dronename)
    droneInQs.setLPIDs(drones)
    droneInQs_uri = daemon.register(droneInQs)
    ns.register("inputqueue.stubdrones", droneInQs_uri)  
    
    # Start Controller process
    pController = Process(group=None, target=controller, name='Stub Controller Process')
    print 'starting controller'
    pController.start()     
    
    # Drones
    print 'starting drones'
    pDrones = []
    for i in range(0, len(drones)):
        pDrone = Process(group=None, target=drones[i], name='drone'+str(drones[i].uid)) 
        pDrones.append(pDrone)
        pDrone.start()  
        print i, pDrone.is_alive()    
    
    # Run shared object requests loop
    print 'starting shared objects request loop'
    daemon.requestLoop()
        
#
# Start of Execution
#
if __name__ == '__main__':
    main()