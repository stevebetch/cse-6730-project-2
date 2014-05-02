# Stores the state of a Drone object
class DRONEState(): 
     def __init__(self, obj):
            self.uid = obj.uid
            self.droneType = obj.droneType
            
            self.localTime = obj.localTime

            self.LocalSimTime=obj.LocalSimTime #current simulation time for the drone

            self.MaintenanceActionTime=obj.MaintenanceActionTime
            self.Joker=obj.Joker #how much time we have to search
            self.jokerflag=obj.jokerflag

            self.Bingo=obj.Bingo #time until we have to leave the map

            self.DistEntry=obj.DistEntry #distance from the entry node

            self.FlightSpeed=obj.FlightSpeed#Random flight speed of the drone,
            self.DroneLegs= obj.DroneLegs 

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
            self.TarTime=obj.TarTime

# Stores the state of a IMINT object
class IMINTState():
        def __init__(self,obj):
                self.key=obj.localTime
                self.id=obj.id
                self.heuristic=obj.heuristic
                self.totalValue=obj.totalValue
                self.targetsTracked=obj.targetsTracked
                self.localTime=obj.localTime

# Stores the state of a CAOC object
class CAOCState():
        def __init__(self,obj):
                self.key=obj.localTime
                self.localTime=obj.localTime
                self.id=obj.id
                self.priorityQueue=obj.priorityQueue
                self.drones=obj.drones
                self.heuristic=obj.heuristic

# Stores the state of a HMINT object
class HMINTState():
        def __init__(self,obj):
                self.key=obj.localTime
                self.localTime=obj.localTime
                self.id = obj.id
                self.numTargets = obj.numTargets
                self.count = obj.count
                self.currTargetTimestamp = obj.currTargetTimestamp
                self.targets = obj.targets
                self.targetTimestamps = obj.targetTimestamps
                self.randNodes = obj.randNodes
             
# Stores the state of a stub object (for testing only)
class StubState():
     def __init__(self, time):
          self.localTime = time