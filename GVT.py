import time
from threading import Thread

class GVTWaitForThread(Thread):
    
    def onGVTThreadFinished(self, lpids, msg):
        pass  # this is deliberately set to 'pass' to make callback work
    
    def __init__(self, parent, controlMsg):
        Thread.__init__(self)
        self.parent = parent
        self.LPID = parent.LPID
        self.controlMsg = controlMsg
        
    def run(self):
        numMsgsSentToThisLP = 0
        LPIDs = []
        for i, j in self.controlMsg.data.counts.items():
            LPIDs.append(i)
        numMsgsSentToThisLP = self.controlMsg.data.counts[self.LPID]
        while self.parent.gvtData.counts[self.LPID] < numMsgsSentToThisLP:
            print 'sent to: %d' % (numMsgsSentToThisLP)
            print 'received by: %d' % (self.parent.gvtData.counts[self.LPID])         
            print 'LP %d: Waiting for all white messages sent to this LP to be received' % (self.LPID)
            time.sleep(2)
        self.parent and self.parent.onGVTThreadFinished(LPIDs, self.controlMsg)
        
class GVTControlMessageData():
    'Data content for GVT Control Message'
    
    def __init__(self, lpids):
        self.tMin = 0
        self.tRed = 0
        self.counts = {}
        for i in range(len(lpids)):
            self.counts[i] = 0
        self.LPIDs = lpids
            
    def addLocalCounts(self, localCounts, lpid):
        print 'self.counts'
        for i in self.counts:
            print 'self.counts[%d] = %d' % (i,self.counts[i])        
        print 'localCounts'
        for i in localCounts:
            print 'localCounts[%d] = %d' % (i,localCounts[i])         
        for key, value in self.counts.items():
            if (key != lpid):
                self.counts[key] += localCounts[key]
            
    def dump(self):
        print 'GVTControlMessageData dump:'
        print 'self.tMin = %d' % (self.tMin)
        print 'self.tRed = %d' % (self.tRed)        
        for i in self.counts:
            print 'self.counts[%d] = %d' % (i,self.counts[i])  
            
class LPGVTData:
    "Local GVT data for a logical process"
    
    # Class constants
    WHITE = 'white' # Set when before cut 1 or after cut 2
    RED = 'red'  # Set when between cut 1 and cut 2
    INF = 999999999999
    
    def __init__(self):
        self.tMin = 0 # smallest timestamp of any unprocessed message in inputqueue
        self.tRed = 0 # smallest timestamp of any red message (sent between cut C1 and C2)
        self.color = LPGVTData.WHITE
        self.gvt = 0
        self.counts = {}
        
    def initCounts(self, lpids):
        for i in range(len(lpids)):
            self.counts[i] = 0
            
    def dump(self):
        print 'LPGVTData dump'
        if self.tMin is None:
            print 'self.tMin = None'
        else:
            print 'self.tMin = %d' % (self.tMin)
        print 'self.tRed = %d' % (self.tRed)
        print 'self.color = %s' % (self.color)        
        for i in self.counts:
            print 'self.counts[%d] = %d' % (i,self.counts[i])
        print 'self.gvt = %d' % (self.gvt)
        
class GVTValue:
    
    def __init__(self, gvt):
        self.gvt = gvt
