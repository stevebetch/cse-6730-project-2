import sys

class Target:
    "Target"
    
    #param1 = predicted location (random variate)
    #param2 = strength of intelligence (random variate)
    #param3 = idle time (random variate)

    def __init__(self, param1, param2):
        # initialize parameters for target
        self.param1 = param1
        self.param2 = param2