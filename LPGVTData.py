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
        print 'self.tMin = %d' % (self.tMin)
        print 'self.tRed = %d' % (self.tRed)
        print 'self.color = %s' % (self.color)        
        for i in range(len(self.counts)):
            print 'self.counts[%d] = %d' % (i,self.counts[i])
        print 'self.gvt = %d' % (self.gvt)
