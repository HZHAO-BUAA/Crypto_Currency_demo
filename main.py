import time
import Simulation
import CrazyMiner
import sys, os

#f = open(os.devnull, 'w')
#oldStderr = sys.stderr
#sys.stderr = f
    

Simulation.normal_simul(2, 6, 6)


time.sleep(5)
CrazyMiner.crazy_miner_simulation()
