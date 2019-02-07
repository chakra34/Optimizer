#!/usr/bin/env python

import numpy as np
import sys,os,shutil
import Optimization
from optparse import OptionParser
from subprocess import call,check_output

#------------------------------------------------------------------------------------------------- #
class optimize(Optimization.Optimization):
  _counter = 0

#===========================================
  def fitness(self,x):
#============================================
    print "****************************************************************************************"
    print "                                  generation %i                                         "%(self.generation)                                               # generation
    print "****************************************************************************************"
#------------- Replacing the parameters in material config ---------------------------------------- #
    rep = {}                                                                                        # dictionary representing the parameters
    for i in xrange(len(x)):
      rep["coords_%i"%(i+1)] = x[i]*1e6                                                             # parameters are in MPa 

    with open(self.mat_file,'r') as file_in:
      contents = file_in.read()


    if not os.path.isdir("{}/Generation_0{}".format(self.root,str(self.generation+1)) ):
      os.mkdir('{}/Generation_0{}'.format(self.root,str(self.generation+1)) )

    if not os.path.isdir('{}/Generation_0{}/Test_0{}'.format(self.root,str(self.generation+1),self._counter) ):
      os.mkdir('{}/Generation_0{}/Test_0{}'.format(self.root,str(self.generation+1),self._counter) )

    dir_loc = "{}/Generation_0{}/Test_0{}".format(self.root,str(self.generation+1),self._counter)
    if self.job_id != None:
      shutil.copy("%s/%s.dat"%(self.root,self.job_id),'%s/'%dir_loc)                               #  *.dat file for mentat
      shutil.copy("%s/%s.outputHomogenization"%(self.root,self.job_id),'%s/'%dir_loc)                                    #  *.outputHomogenization for mentat
      shutil.copy("%s/%s.outputCrystallite"%(self.root,self.job_id),'%s/'%dir_loc)                                    #  *.outputHomogenization for mentat
      shutil.copy("%s/%s.outputConstitutive"%(self.root,self.job_id),'%s/'%dir_loc)                                    #  *.outputConstitutive for mentat
    shutil.copy("%s/%s"%(self.root,self.exp_file),'%s/'%dir_loc)
    os.chdir('%s/'%dir_loc)
    with open("material.config",'w') as f_out:
      for key,value in rep.items():
        contents = contents.replace("%s"%str(key),"%s"%str(value) )
      f_out.write(contents)

#--------- Running damask postProcessing and finding error against "experimental" data ----------- #

    fname = "%s_%s"%(os.path.splitext(options.geom_file)[0],os.path.splitext(options.load_file)[0])

    cmd1 = '/opt/soft/MSC/marc2013.1/tools/run_damask -prog /egr/research/CMM/DAMASK/chakra34/code/DAMASK_marc.marc -jid  {}/{} -dirjid {} -dirjob {} -q b -ml 387555 -ci no -cr no -ver no'\
                 .format(dir_loc,self.job_id,dir_loc,dir_loc)
#    call(cmd1,shell=True)
    print cmd1
    
    cmd2 = 'postResults --cr f,p {}/{}.t16'.format(dir_loc,self.job_id)
#    call(cmd2, shell=True)
    print cmd2

    cmd3 = 'addCauchy {}/postProc/{}.txt'.format(dir_loc,self.job_id)
#    call(cmd3,shell=True)
    print cmd3
    cmd4 = 'addStrainTensors -0 -v {}/postProc/{}.txt'.format(dir_loc,self.job_id)
#    call(cmd4,shell=True)
    print cmd4
    cmd5 = 'addMises -s Cauchy -e "ln(V)" {}/postProc/{}.txt'.format(dir_loc,self.job_id)
#    call(cmd5,shell=True)
    print cmd5

    cmd6 = 'InterpolateTables.py --expX "Mises(ln(V))" --expY "Mises(Cauchy)" --expfile {}/{} --simX "Mises(ln(V))" --simY "Mises(Cauchy)" --simfile {}/postProc/{}.txt'\
                .format(dir_loc,options.exp_file,dir_loc,self.job_id)
#    error = check_output(cmd6, shell=True)
    print cmd6


#------------------------------------------------------------------------------------------------- #
    os.chdir('%s'%(self.root))

    self._counter += 1
    print "+++++++++++++++++++++++++++++++++ current fitness ++++++++++++++++++++++++++++++++++++++"
    print "                                       %s                                               "%(str(error))
    print "++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
#    return float(error)
    return np.linalg.norm()

  def info_fitness(self,mat_file,job_id,exp_file):
    self.mat_file  = mat_file
    self.job_id    = job_id
    self.exp_file  = exp_file


#-------------------------------- main program starts here ----------------------------------------- #

parser = OptionParser()
parser.add_option(      '--mat',
                  dest = 'mat_file',
                  type = 'string', metavar = 'string',
                  help = ' material.config file')
parser.add_option(      '--job_id',
                  dest = 'job_id',
                  type = 'string', metavar = 'string',
                  help = ' job id for mentat file')
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
if not os.path.exists(options.job_id):
  parser.error('No job_file selected for mentat')

options.root = os.path.dirname(os.path.realpath(__file__)) if options.root == None else options.root


theOptimizer = optimize(method = 'neldermead',
                         bounds = np.array([[20,40],
                                            [40,60],
                                            [70,80],
                                           ]),
                         tolerance = 0.001,
                         root      = options.root,
                         rigid     = True,
                         )

theOptimizer.info_fitness(options.mat_file,options.job_id,options.exp_file)
theOptimizer.optimize(verbose = False)

print theOptimizer.cost
print theOptimizer.best()