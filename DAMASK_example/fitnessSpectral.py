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
    with open('{}/output.log'.format(options.root),'a') as file:
      file.write("\n Generation %i "%(self.generation+1))
  #============================================
      print "****************************************************************************************"
      print "                                  generation %i                                         "%(self.generation+1)                                               # generation
      print "****************************************************************************************"
  #------------- Replacing the parameters in material config ---------------------------------------- #

      orientations = np.array([ [ 270.0,  0.0,  90.0 ],         # orientation to run the optimization for
                             ])
      if not os.path.isdir("{}/Generation_0{}".format(self.root,str(self.generation+1)) ):
        os.mkdir('{}/Generation_0{}'.format(self.root,str(self.generation+1)) )
      print "***** Generation number ****", self.generation+1
      if not os.path.isdir('{}/Generation_0{}/Test_0{}'.format(self.root,str(self.generation+1),self.cost) ):
        os.mkdir('{}/Generation_0{}/Test_0{}'.format(self.root,str(self.generation+1),self.cost) )
      orientation_run = 1
      error = []
      for orientation in orientations:
        print " ------------------ orientation_run ----------------", orientation_run
        print "++++++++++++++++++++++++++++++++++++++++ doing for orientation ++++++++++++++++++++++++++++++++++++++++"
        print "                                          {}-{}-{}                                                     ".format(orientation[0],orientation[1],orientation[2])
        print "+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"           
        file.write("\n ++++++++++++++++++++++++++++++++++++++++ doing for orientation ++++++++++++++++++++++++++++++++++++++++")
        file.write("\n                                          {}-{}-{}                                                     ".format(orientation[0],orientation[1],orientation[2]))
        file.write("\n+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")           
        if not os.path.isdir("{}/Generation_0{}/Test_0{}/Orientation_0{}".format(self.root,str(self.generation+1),self.cost,orientation_run) ):
          os.mkdir("{}/Generation_0{}/Test_0{}/Orientation_0{}".format(self.root,str(self.generation+1),self.cost,orientation_run) )
        orient = {}
        with open('{}/{}'.format(self.root,self.mat_file),'r') as file_in:
          contents = file_in.read()
        for j in xrange(3):
          orient["{}_eulerangles".format(j+1)] = orientation[j]                                                                 # parameters are in MPa 

        rep = {}                                                                                        # dictionary representing the parameters
        for i in xrange(len(x)):
          rep["%i_coords"%(i+1)] = x[i]                                                                 # parameters are in MPa 

        with open('{}/{}'.format(self.root,self.mat_file),'r') as file_in:
          contents = file_in.read()


        dir_loc = "{}/Generation_0{}/Test_0{}/Orientation_0{}".format(self.root,str(self.generation+1),self.cost,orientation_run)
        print "directory location++++", dir_loc
        if options.load_file != None :
          shutil.copy("%s/%s"%(self.root,self.load_file),'%s/'%dir_loc)
        if options.num_file != None :
          shutil.copy("%s/%s"%(self.root,self.num_file),'%s/'%dir_loc)
        if options.geom_file != None :
          shutil.copy("%s/%s"%(self.root,self.geom_file),'%s/'%dir_loc)
        shutil.copy("%s/%s"%(self.root,self.exp_file),'%s/'%dir_loc)
        os.chdir('%s/'%dir_loc)
        with open("material.config",'w') as f_out:
          for key,value in rep.items():
            contents = contents.replace("%s"%str(key),"%s"%str(value) )
          for key,value in orient.items():
            contents = contents.replace("%s"%str(key),"%s"%str(value) )
          f_out.write(contents)

#--------- Running damask postProcessing and finding error against "experimental" data ----------- #
        fname = "%s_%s"%(os.path.splitext(options.geom_file)[0],os.path.splitext(options.load_file)[0])
        cmd1 = 'DAMASK_spectral -l {}/{} -g {}/{} > {}/output.log'\
                     .format(dir_loc,self.load_file,dir_loc,self.geom_file,dir_loc)
        call(cmd1,shell=True)
        print cmd1
        exit_status = open('{}/{}.sta'.format(dir_loc,fname),'r').readlines()[-1].split()[0]
        if exit_status != "4000":
          print "Error in termination"
          return "none"
        
        else:
          print "Normal termination doing post results"                                         # Repeating the simulation with parameter values in ratio of last converged 
    
          cmd2 = 'postResults --cr f,p {}/{}.spectralOut'.format(dir_loc,fname)
          call(cmd2, shell=True)
          print cmd2

          cmd3 = 'addCauchy {}/postProc/{}.txt'.format(dir_loc,fname)
          call(cmd3,shell=True)
          print cmd3
          cmd4 = 'addStrainTensors -0 -v {}/postProc/{}.txt'.format(dir_loc,fname)
          call(cmd4,shell=True)
          print cmd4
###### write your code to find the error between (in this case) simulated Stress-Strain curve and reference stress-strain curve
#           cmd6 = 'InterpolateTables.py --expX "x" --expY "y" --expfile {}/{} --simX "5_ln(V)" --simY "5_Cauchy" --simfile {}/postProc/{}.txt'\
#                       .format(dir_loc,options.exp_file,dir_loc,fname)
          error = check_output(cmd6, shell=True)
          print cmd6
          file.write("\n %s "%cmd6)
          file.write("***\n error-- {} *** orientation --> {} ***".format(error,orientation))
          print " error--",error,"*** orientation -->",orientation,"***"

#------------------------------------------------------------------------------------------------- #
          os.chdir('%s'%(self.root))
          orientation_run += 1
  
      print "+++++++++++++++++++++++++++++++++ current fitness and points +++++++++++++++++++++++++++"
      print x
      print float(error)
      print "                                       %s                                               "%(str(error))
      print "++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
      file.write("\n +++++++++++++++++++++++++++++++++ current fitness and points +++++++++++++++++++++++++++\n")
      file.write("\n {}".format(float(error)))
      file.write("\n {}".format(x))
  #    print "                                       %s                                               "%(str(error))
      file.write("\n++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++\n")
    return float(error)
#    return np.linalg.norm(np.dot(x,x))

  def info_fitness(self,mat_file,load_file,geom_file,exp_file,num_file):
    self.mat_file  = mat_file
    self.load_file = load_file
    self.geom_file = geom_file
    self.exp_file  = exp_file
    self.num_file  = num_file


#-------------------------------- main program starts here ----------------------------------------- #

parser = OptionParser()
parser.add_option(      '--mat',
                  dest = 'mat_file',
                  type = 'string', metavar = 'string',
                  help = ' material.config file')
parser.add_option(      '--numerics',
                  dest = 'num_file',
                  type = 'string', metavar = 'string',
                  help = ' numerics.config file')
parser.add_option(      '--load',
                  dest = 'load_file',
                  type = 'string', metavar = 'string',
                  help = ' loadcase file')
parser.add_option(      '--geom',
                  dest = 'geom_file',
                  type = 'string', metavar = 'string',
                  help = ' geom file')
parser.add_option(      '--exp',
                  dest = 'exp_file',
                  type = 'string', metavar = 'string',
                  help = ' experimental file to compare ')

parser.add_option(      '--root',
                  dest = 'root',
                  type = 'string', metavar = 'string',
                  help = ' desired root of this process ')

(options,filenames) = parser.parse_args()

if not options.mat_file or not os.path.exists(options.mat_file):
  print "Suitable format material config (file containing parameters) is not supplied "
if not options.exp_file or not os.path.exists(options.exp_file):
  parser.error('No file selected for comparison')
if not os.path.exists(options.load_file):
  print "No loadcase file for DAMASK!!! "
if not os.path.exists(options.geom_file):
  print "No geom file for DAMASK!!! "
options.root = os.path.dirname(os.path.realpath(__file__)) if options.root == None else options.root

tick = time.time()
theOptimizer = optimize(method = 'neldermead',
                         bounds = np.array([[20e6,40e6],
                                            [40e6,80e6],
                                            [40e6,80e6],
                                           ]),
                         tolerance = 0.004,
                         root      = options.root,
                         rigid     = True,
                         )

theOptimizer.info_fitness(options.mat_file,options.load_file,options.geom_file,options.exp_file,options.num_file)
theOptimizer.optimize(verbose = False)
tock = time.time()
print "Time for simulation",(tock - tick)
print theOptimizer.cost
print theOptimizer.best()
with open("{}/output.log".format(options.root),'a') as file:
  file.write("\nTime for simulation {}".format(tock - tick))
  file.write("\n {}".format(theOptimizer.cost))
  file.write("\n {}".format(theOptimizer.best()))
