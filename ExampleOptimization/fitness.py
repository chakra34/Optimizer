#!/usr/bin/env python

import numpy as np
import sys,os,shutil
import time
import Optimization
from optparse import OptionParser
from subprocess import call,check_output

#------------------------------------------------------------------------------------------------- #
_ratio = None
class optimize(Optimization.Optimization):

#===========================================
  def fitness(self,x):
    self.cost += 1
    return np.linalg.norm(np.dot(x,x))

#-------------------------------- main program starts here ----------------------------------------- #

parser = OptionParser()
parser.add_option(      '--root',
                  dest = 'root',
                  type = 'string', metavar = 'string',
                  help = ' desired root of this process ')

(options,filenames) = parser.parse_args()

options.root = os.path.dirname(os.path.realpath(__file__)) if options.root == None else options.root

tick = time.time()
theOptimizer = optimize(method = 'neldermead',
                         bounds = np.array([[0,1],
                                            [0,1],
                                            [0,1],
                                           ]),
                         tolerance = 1e-6,
                         root      = options.root,
                         rigid     = True,
                         )


theOptimizer.optimize(verbose = False)
tock = time.time()
print "Time for simulation",(tock - tick)
print theOptimizer.cost
print theOptimizer.best()
with open("{}/output.log".format(options.root),'a') as file:
  file.write("\nTime for simulation {}".format(tock - tick))
  file.write("\n {}".format(theOptimizer.cost))
  file.write("\n {}".format(theOptimizer.best()))
