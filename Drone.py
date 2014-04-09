import sys
from LogicalProcess import *
from Map import GenMap
from nodes import EntryNode
from multiprocessing import Lock
import random

class Drone (LogicalProcess):

    # instance argument list
    #id - unique id of drone
    #controller - the simulation executive
    #droneType - descriptive

    def __init__(self, id, droneType, caoc):
        LogicalProcess.__init__(self)
        self.droneType = droneType
        self.caoc = caoc
        self.id = id
     
        self.LocalSimTime=0 #current simulation time for the drone
        self.MatenanceActionTime=144000 #how much time until we need to land for maintainance (40 hr engine overhaul (yes andrew it should be 100hr), ect)
        self.Joker=0 #how much time we have to search
        self.Bingo=0 #time until we have to leave the map
        self.DistEntry=0.0 #distance from the entry node
        self.FlightSpeed=random.randint(50,200)#Random flight speed of the drone
        self.DroneLegs=28800 # Assuming the drone has 8hr legs (8*3600=28800 sec) We can change this later if we want
        self.xpos=0 #current x location
        self.ypos=0 #current y location
        self.EntNode=[]
        self.currentNode=[]
        self.target=[]
    
    def __call__(self):
        self.run()        
    
    def setController(self, controller):
        self.controller = controller
            
    def handleMessage(self, msg):
        # determine message type and process accordingly
        pass
    
    def start(self,mapObj):
        # Begin process of selecting target from CAOC priority queue, tracking, check when refueling needed, etc.
        pass
    
    
    
    def updateTime(self,DroneSimTime):
        #Update the timers with each timestep
        timeDif=DroneSimTime-self.LocalSimTime
        self.Joker-=timeDif
        self.Bingo-=timeDif
        self.MatenanceActionTime-=timeDif
        print "\nNew Joker:", self.Joker, "New Bingo:",self.Bingo


    def setJokerBingo(self):
    # Call this funtion after the drone returns from a maintainance action, refuleing or at the start of the sim
            if(self.DroneLegs<self.MatenanceActionTime):#We have less fuel time than maintainance time
                self.Joker=self.DroneLegs*0.8 # Joker is set at 6 hrs 24 min. Ensures we have enough time (48 min) to track another target before bingo
                
                self.Bingo=self.DroneLegs*0.9 # 45 minutes flight time to return to base
            
            else: #assuming we have more than 4 hours of flight time. If less than 4 hours, we should be premptively performing maintainance
                self.Joker=self.MatenanceActionTime - 7200 # 2 hour joker
                self.Bingo=self.MatenanceActionTime - 3600 # 1 hour bingo

            print "\nJoker set to:", self.Joker, "Bingo set to:",self.Bingo


    def resetMatenanceTimer(self):
        self.MatenanceActionTime=144000

    def setEntry(self,obj):
        self.EntryNode=obj
        #print "Map entry at:" , self.EntryNode.xpos,",",self.EntryNode.ypos

    def updateCurNode(self,obj):
        self.currentNode=obj #may not be needed, but may be expanded later if needed.
        
    def getNewTargetFromCAOC(self):
        lock = Lock()
        self.target=self.caoc.getNextTarget(lock, None, None)
        del lock
    
    def run(self):
        # Begin process of selecting target from CAOC priority queue, tracking, check when refueling needed, etc.
        print('Drone process running')    


    def probTest(self,probVal):

    def detection(self):

        #This function will be called to determine if we get a positive detection on the
        testprob=random.uniform(0,1)
        if(probVal<=testprob):
        # Weve got a positive hit!
            return 1
        else:
            return 0





