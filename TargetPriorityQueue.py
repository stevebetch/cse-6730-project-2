from Queue import PriorityQueue

class TargetPriorityQueue (PriorityQueue):
    
    # Need to implement
    def __init__(self):
        PriorityQueue.__init__(self)
        self.counter = 0
        
    def put(self, priority, target):
        PriorityQueue.put(self, (priority, self.counter, target))
        self.counter += 1    
        
    def get(self, *args, **kwargs):
        _, _, item = PriorityQueue.get(self, *args, **kwargs)
        return item    