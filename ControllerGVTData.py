class ControllerGVTData:
    
    def __init__(self):
        self.tMin = 0   # min time stamp value among unprocessed msgs among LPs visited so far
        self.tRed = 0   # min time stamp value of RED msgs sent by LPs visited so far
        self.count = {}   # cumulative vector counters among LPs visited so far
                          # count[i] is number of white msgs sent to P_i that have not yet been rcvd