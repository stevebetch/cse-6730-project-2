import Queue

class LPInputQueue():
    
    def __init__(self):
        self.q = Queue.Queue()
        
    def put(self, obj):
        self.q.put(obj)
        
    def get(self):
        return self.q.get()