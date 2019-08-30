#!/usr/bin/env python3

import numpy as np
import sys,os,shutil
import time
import random
import Optimization
from optparse import OptionParser
from subprocess import run,check_output

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
    with open('{}/output_gen{}_{}.log'.format(options.root,self.generation+1,self.id(x)),'a') as file:
      file.write("\n Generation %i "%(self.generation+1)) 

      xvalue        = self.map2space(x[:self.dimension])[0]
      yvalue        = self.map2space(x[:self.dimension])[1]
      fitness_value = (xvalue**2 + yvalue -11)**2 + (xvalue + yvalue**2 - 7 )**2               #https://en.wikipedia.org/wiki/Test_functions_for_optimization
      print(fitness_value)
      
#       server = [1,3,4,5,6,7,8,9,10]
#       j = random.choice(server)
#       cmd = 'ssh compute{:02}.egr.msu.edu -t "cd {};./Himmelblau_bash.sh {} {}"'.format(j,self.root,float(x[0]),float(x[1]))
#       fitness_value = check_output(cmd, shell=True, universal_newlines=True).split()[0]  
#       print(cmd)

      self.curr_locations.append(np.append(x,fitness_value))
      self.locations[self.id(x)] = fitness_value

      file.write("\n +++++++++++++++++++++++++++++++++ current fitness and points +++++++++++++++++++++++++++\n")
      file.write("\n fitness {}".format(fitness_value))
      file.write("\n points {} parameters{}".format(x[:self.dimension],self.map2space(x[:self.dimension])))
      file.write("\n++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++\n")
      
    return fitness_value

#-------------------------------- main program starts here ----------------------------------------- #

parser = OptionParser()
parser.add_option(      '--root',
                  dest = 'root',
                  type = 'string', metavar = 'string',
                  help = ' desired root of this process ')

(options,filenames) = parser.parse_args()


options.root = os.path.dirname(os.path.realpath(__file__)) if options.root == None else options.root

tick = time.time()
theOptimizer = optimize(method = 'pso',
                         bounds = np.array([[-10,10],                     
                                            [-10,10],                    
                                           ]),
                         tolerance = 0.001,
                         root      = options.root,
                         rigid     = True,
                         )

theOptimizer.optimize(verbose = False)
tock = time.time()
print("Time for simulation",(tock - tick))
print(theOptimizer.cost())
print(theOptimizer.best())
with open("{}/output.log".format(options.root),'a') as file:
  file.write("\nTime for simulation {}".format(tock - tick))
  file.write("\n {}".format(theOptimizer.cost()))
  file.write("\n {}".format(theOptimizer.best()))