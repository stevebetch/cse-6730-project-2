from DroneSim1 import *
import csv



def ProgRunner ():
#Input: none 
#Output: None 
#Description: Initializes PYRO4, opens and takes data from control.csv, pasrses the data up and starts the sim running.
# This is a wrapper script to control multiple simulation runs.


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
#Input: none Output: None. Description: Initializes the class of data that controls the simulation

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
        self.tarType=2
        self.Legs=41760


    def fillRow(self,row):
    #Input: a row of data Output: None. Description: Sets the data for a simulation based on what is passed to it from the Control.csv file
        self.numDrones=int(row[0])
        self.typeOfDrone = row[1]
        self.numTargets=int(row[2])*2
        self.numStreets=int(row[3])
        self.seedNum=float(row[4])
        self.mapX=int(row[5])
        self.mapY=int(row[6])
        self.heuristic=int(row[7])
        self.Nuisance=float(row[8])
        self.tarType=float(row[9])
        self.Legs=float(row[10])

if __name__ == '__main__':
    ProgRunner()