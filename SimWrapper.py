from DroneSim1 import *
import csv



def ProgRunner ():

#initialize
    PYRO_HOST=get_local_ip_address()
    print "Using IP address:", PYRO_HOST
#    daemon = Pyro4.Daemon(host=PYRO_HOST, port=PYRO_PORT)
    ns = Pyro4.locateNS()

# parameters (later get from file)

    with open('Control.csv', 'rU') as file:
        reader=csv.reader(file)
        reader.next() #kill off the header row
        
        for row in reader:
            daemon = Pyro4.Daemon(host=PYRO_HOST)
            DataArgs=Data()
            DataArgs.fillRow(row)
            Simulation=main(DataArgs,daemon,ns)


class Data:
    def __init__(self):
        self.numDrones=0
        self.numStreets=50
        self.numTargets=10
        self.seedNum=1
        self.mapX=300
        self.mapY=300
        self.heuristic=1
        self.typeOfDrone = "DroneType1"
        self.Nuisance=.8

    def fillRow(self,row):
        self.numDrones=int(row[0])
        self.typeOfDrone = row[1] # does this need to be a string? or int? or float?
        self.numTargets=int(row[2])*2
        self.numStreets=int(row[3])
        self.seedNum=float(row[4])
        self.mapX=int(row[5])
        self.mapY=int(row[6])
        self.heuristic=int(row[7])
        self.Nuisance=float(row[8])

if __name__ == '__main__':
    ProgRunner()