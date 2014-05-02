import time
from Message import *
from threading import Thread

# Thread object executed wait for a logical process' white messages received
# count to equal total number of white messages sent to that process
class GVTWaitForThread(Thread):
    
    def onGVTThreadFinished(self, lpids, msg):
        pass  # this is deliberately set to 'pass' to make callback work
    
    def __init__(self, parent, controlMsg):
        Thread.__init__(self)
        self.parent = parent
        self.LPID = parent.LPID
        self.controlMsg = controlMsg
        
    # executes the thread
    def run(self):
        numMsgsSentToThisLP = 0
        LPIDs = []
        for i, j in self.controlMsg.data.counts.items():
            LPIDs.append(i)
        numMsgsSentToThisLP = self.controlMsg.data.counts[self.LPID]
        while self.parent.gvtData.counts[self.LPID] + numMsgsSentToThisLP > 0:
            if(self.parent.Loopcont.getCon()==0):
                break
            if(debug==1):
                print 'sent to: %d' % (numMsgsSentToThisLP)
                print 'received by: %d' % (self.parent.gvtData.counts[self.LPID])         
                print 'LP %d: Waiting for all white messages sent to this LP to be received' % (self.LPID)
            time.sleep(2)
        if(self.parent.Loopcont.getCon()==0):
            return
        self.parent and self.parent.onGVTThreadFinished(LPIDs, self.controlMsg)
        
# Message representing GVT token used to accumulate message counts among all logical
# processes in token ring
class GVTControlMessageData():
    'Data content for GVT Control Message'
    
    def __init__(self, lpids):
        self.tMin = LPGVTData.INF
        self.tRed = LPGVTData.INF
        self.counts = {}
        for i in range(len(lpids)):
            self.counts[i] = 0
        self.LPIDs = lpids
            
    # Adds the message counts for the local logical process to the accumulated totals
    def addLocalCounts(self, localCounts, lpid):
        if(debug==1):
            print 'self.counts'
            for i in self.counts:
                print 'self.counts[%d] = %d' % (i,self.counts[i])        
            print 'localCounts'
            for i in localCounts:
                print 'localCounts[%d] = %d' % (i,localCounts[i])         
        for key, value in self.counts.items():
            if (key != lpid):
                self.counts[key] += localCounts[key]
            
    # prints out token's parameters
    def dump(self):
        if(debug==1):
            print 'GVTControlMessageData dump:'
            print 'self.tMin = %d' % (self.tMin)
            print 'self.tRed = %d' % (self.tRed)        
            for i in self.counts:
                print 'self.counts[%d] = %d' % (i,self.counts[i])  

# Data structure used by a logical process to store its local GVT data
# including vector of message counts, local tMin and tRed values
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
        
    # initializes vector of message counts
    def initCounts(self, lpids):
        for i in range(len(lpids)):
            self.counts[i] = 0
        
    # prints contents of data structure    
    def dump(self):
        if(debug==1):
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

    # resets the local values
    def reset(self):
        self.tMin = 0 # smallest timestamp of any unprocessed message in inputqueue
        self.tRed = 0 # smallest timestamp of any red message (sent between cut C1 and C2)
        self.color = LPGVTData.WHITE
        self.gvt = 0
        self.counts = []

# Message data containing GVT value to be propagated to all LPs
class GVTValue:
    
    def __init__(self, gvt):
        self.gvt = gvt
