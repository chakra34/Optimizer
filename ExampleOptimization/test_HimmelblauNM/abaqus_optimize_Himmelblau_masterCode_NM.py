#!/usr/bin/env python3

import numpy as np
import sys,os,shutil
import time
import random
import Optimization
from optparse import OptionParser
from subprocess import run,check_output
import damask

#------------------------------------------------------------------------------------------------- #
_ratio = None
class optimize(Optimization.Optimization):

  def id(self,x):
    return str(self.map2space(x[:self.dimension])).translate(str.maketrans(' []','___')) 
      
#===========================================
  def fitness(self,x):
    if self.id(x) in self.locations:
      self.curr_locations.append(np.append(x,self.locations[self.id(x)]))
      return self.locations[self.id(x)]

    xvalue        = self.map2space(x[:self.dimension])[0]
    yvalue        = self.map2space(x[:self.dimension])[1]
    fitness_value = (xvalue**2 + yvalue -11)**2 + (xvalue + yvalue**2 - 7 )**2               #https://en.wikipedia.org/wiki/Test_functions_for_optimization
    print('fitness {}'.format(fitness_value))
    self.locations[self.id(x)] = fitness_value
   
    if not options.concise:
      with open('{}/output_gen{}_{}.log'.format(options.root,self.generation+1,self.id(x)),'a') as file:
        file.write("\n Generation %i "%(self.generation+1))
        file.write("\n +++++++++++++++++++++++++++++++++ current fitness and points +++++++++++++++++++++++++++\n")
        file.write("\n fitness {}".format(fitness_value))
        file.write("\n points {} parameters{}".format(x[:self.dimension],self.map2space(x[:self.dimension])))
        file.write("\n++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++\n")
      file.close() 
    
    return fitness_value

#-------------------------------- main program starts here ----------------------------------------- #

parser = OptionParser()
parser.add_option(      '--root',
                  dest = 'root',
                  type = 'string', metavar = 'string',
                  help = ' desired root of this process ')
parser.add_option('--restart',  action="store_true",
                  dest="restart",
                  help="restart optimization")
parser.add_option('-c','--concise',  action="store_true",
                  dest="concise",
                  help="concise outputs")
parser.add_option(      '--points',
                  dest = 'points_data',
                  type = 'string', metavar = 'string',
                  help = 'points for next generation ')

#making the default values and let them show
parser.set_defaults( concise = False,
                   )
(options,filenames) = parser.parse_args()


options.root = os.path.dirname(os.path.realpath(__file__)) if options.root == None else options.root

tick = time.time()
if options.restart:

  table1 = damask.ASCIItable(name = options.points_data, buffered = False)
  table1.head_read()
  table1.data_readArray()

  theOptimizer = optimize( method          = 'neldermead',
                           bounds          = np.array([[-10,10],
                                                       [-10,10],
                                                     ]),
                           tolerance       = 0.01,
                           root            = options.root,
                           concise_outputs = options.concise,
                           rigid           = True,
                           restart         = True,
                           points_rs       = table1.data,
                           )
else:
  theOptimizer = optimize(method           = 'neldermead',
                           bounds          = np.array([[-10,10],
                                                       [-10,10],
                                                     ]),
                           tolerance       = 0.01,
                           root            = options.root,
                           concise_outputs = options.concise,
                           rigid           = True,
                           )

theOptimizer.optimize(verbose = False)
tock = time.time()
print("Time for simulation",(tock - tick))
print("Cost {}".format(theOptimizer.cost()))
print("Best parameters and fitness {}".format(theOptimizer.best()))
with open("{}/output_{}.log".format(options.root,theOptimizer.method),'a') as file:
  file.write("\nTime for simulation {}".format(tock - tick))
  file.write("\nCost {}".format(theOptimizer.cost()))
  file.write("\nBest parameters and fitness {}".format(theOptimizer.best()))