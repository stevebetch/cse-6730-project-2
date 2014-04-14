from Drone import *
from IMINT import *

class DRONEState(): 
	def __init__(self, obj):
        self.uid = obj.uid
#        LogicalProcess.__init__(self)
        self.droneType = obj.droneType
        
        self.LocalSimTime=obj.LocalSimTime #current simulation time for the drone
        
        self.MaintenanceActionTime=obj.MaintenanceActionTime #how much time until we need to land for maintainance (40 hr engine overhaul (yes andrew it should be 100hr), ect)
        self.Joker=obj.Joker #how much time we have to search
        self.jokerflag=obj.jokerflag
        
        self.Bingo=obj.Bingo #time until we have to leave the map
        
        self.DistEntry=obj.DistEntry #distance from the entry node
        
        self.FlightSpeed=obj.FlightSpeed#Random flight speed of the drone, ft/s? something/s
        self.DroneLegs= obj.DroneLegs # Assuming the drone has 8hr legs (8*3600=28800 sec) We can change this later if we want
        
        self.xpos=obj.xpos #current x location
        self.ypos=obj.ypos #current y location
        
        self.EntNode=obj.EntNode
        self.currentNode=obj.currentNode
        
        self.target=obj.target
        self.detectBool=obj.detectBool # Boolian used for detection logic
        self.sNeedBool=obj.sNeedBool #boolian to determine if we need to activate the search logic.
        self.timeOnNode=obj.timeOnNode #how long have we been on the current node?
        self.nodeTime=obj.nodeTime #how long should it take the target to traverse the node?
        self.searchTime=obj.searchTime #It takes 20 seconds to search the area.
        self.searchdwell=obj.searchdwell


class IMINTstate():
	def __init__(self,obj):
	pass

class CAOCstate():
	def __init__(self,obj):
	pass

