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
#============================================
    print "****************************************************************************************"
    print "                                  generation %i                                         "%(self.generation)                                               # generation
    print "****************************************************************************************"
#------------- Replacing the parameters in material config ---------------------------------------- #

    orientations = np.array([ [294.7, 17.42, 65.3],
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
      if self.job_id != None:
        shutil.copy("%s/%s.dat"%(self.root,self.job_id),'%s/'%dir_loc)                               #  *.dat file for mentat
        shutil.copy("%s/1%s.dat"%(self.root,self.job_id),'%s/'%dir_loc)                               #  *.dat file for mentat
        shutil.copy("%s/1%s.outputHomogenization"%(self.root,self.job_id),'%s/'%dir_loc)              #  *.outputHomogenization for mentat
        shutil.copy("%s/1%s.outputCrystallite"%(self.root,self.job_id),'%s/'%dir_loc)                 #  *.outputHomogenization for mentat
        shutil.copy("%s/1%s.outputConstitutive"%(self.root,self.job_id),'%s/'%dir_loc)                #  *.outputConstitutive for mentat
        shutil.copy("%s/2%s.dat"%(self.root,self.job_id),'%s/'%dir_loc)                               #  *.dat file for mentat
        shutil.copy("%s/2%s.outputHomogenization"%(self.root,self.job_id),'%s/'%dir_loc)              #  *.outputHomogenization for mentat
        shutil.copy("%s/2%s.outputCrystallite"%(self.root,self.job_id),'%s/'%dir_loc)                 #  *.outputHomogenization for mentat
        shutil.copy("%s/2%s.outputConstitutive"%(self.root,self.job_id),'%s/'%dir_loc)                #  *.outputConstitutive for mentat
        shutil.copy("%s/3%s.dat"%(self.root,self.job_id),'%s/'%dir_loc)                               #  *.dat file for mentat
        shutil.copy("%s/3%s.outputHomogenization"%(self.root,self.job_id),'%s/'%dir_loc)              #  *.outputHomogenization for mentat
        shutil.copy("%s/3%s.outputCrystallite"%(self.root,self.job_id),'%s/'%dir_loc)                 #  *.outputHomogenization for mentat
        shutil.copy("%s/3%s.outputConstitutive"%(self.root,self.job_id),'%s/'%dir_loc)                #  *.outputConstitutive for mentat
        shutil.copy("%s/4%s.dat"%(self.root,self.job_id),'%s/'%dir_loc)                               #  *.dat file for mentat
        shutil.copy("%s/4%s.outputHomogenization"%(self.root,self.job_id),'%s/'%dir_loc)              #  *.outputHomogenization for mentat
        shutil.copy("%s/4%s.outputCrystallite"%(self.root,self.job_id),'%s/'%dir_loc)                 #  *.outputHomogenization for mentat
        shutil.copy("%s/4%s.outputConstitutive"%(self.root,self.job_id),'%s/'%dir_loc)                #  *.outputConstitutive for mentat
      shutil.copy("%s/%s"%(self.root,self.exp_file),'%s/'%dir_loc)
      os.chdir('%s/'%dir_loc)
      with open("material.config",'w') as f_out:
        for key,value in rep.items():
          contents = contents.replace("%s"%str(key),"%s"%str(value) )
        for key,value in orient.items():
          contents = contents.replace("%s"%str(key),"%s"%str(value) )
        f_out.write(contents)

  #--------- Running damask postProcessing and finding error against "experimental" data ----------- #

      cmd1 = '/opt/soft/MSC/marc2013.1/tools/run_damask -prog /egr/research/CMM/DAMASK/chakra34/code/DAMASK_marc.marc -np 4 -npcord 4 -jid  {}/{} -dirjid {} -dirjob {} -nte 4 -nts 4 -q b -ml 387555 -ci no -cr no -ver no'\
                  .format(dir_loc,self.job_id,dir_loc,dir_loc)
      call(cmd1,shell=True)
      print cmd1
      time.sleep(5)
      print '{}/{}.pid'.format(dir_loc,self.job_id)
      print os.path.exists('{}/{}.pid'.format(dir_loc,self.job_id))
      while os.path.isfile('{}/{}.pid'.format(dir_loc,self.job_id)):
        print "Mentat is still running"
        time.sleep(500)
      exit_status = open('{}/{}.sts'.format(dir_loc,self.job_id),'r').readlines()[-3].split()[6]
      if exit_status != "3004":
        print "Error in termination"
        return "none"
      
      else:
        print "Normal termination doing post results"                                         # Repeating the simulation with parameter values in ratio of last converged 

        cmd1_1 = 'postResults -r 1468 1468 5 --increment --ns="Displacement Z","Reaction Force Z" -s --increment --filter "z > -0.1" --separation x,y,z {}/{}.t16'.format(dir_loc,self.job_id)
        call(cmd1_1,shell=True)
        print cmd1_1

        cmd2 = 'postResults --ns="Reaction Force Z" --filter "z < -3.98" --map "sum" {}/{}.t16'.format(dir_loc,self.job_id)
        call(cmd2, shell=True)
        print cmd2

        cmd3 = "addTable --table {}/{}Indenter.txt {}/postProc/{}.txt".format(self.root,self.job_id,dir_loc,self.job_id)
        call(cmd3,shell=True)
        print cmd3

        cmd4 = 'addCalculation -l "depth/nm","load/mN" -f "#Pos_indenter# * 1e3","#ReactionForceZ# * 1e-9" {}/postProc/{}.txt'.format(dir_loc,self.job_id)
        call(cmd4,shell=True)
        print cmd4

        cmd5 = 'filterTable --white="depth/nm","load/mN" < {}/postProc/{}.txt > {}/marc_result_load_disp.txt'.format(dir_loc,self.job_id,dir_loc)
        call(cmd5,shell=True)
        print cmd5

        cmd6 = 'chopTable.py -l "depth/nm" -v 500.0 {}/marc_result_load_disp.txt'.format(dir_loc)
        call(cmd6,shell=True)
        print cmd6

        cmd6 = 'InterpolateTables.py --expX "Displacement/nm" --expY "Load/mN" --expfile {}/{}Load_disp_{}.txt --simX "depth/nm" --simY "load/mN" --simfile {}/chopped_marc_result_load_disp.txt'\
                    .format(self.root,self.job_id,orientation_run,dir_loc)
        load_disp_error = check_output(cmd6, shell=True)
        print cmd6

        cmd7 = 'add_InterpolatedImage.py -l 1_nodeinitialcoord,2_nodeinitialcoord -d DisplacementZ --dim 280 282  -p 10.0/255 {}/postProc/{}_inc1468.txt'\
                    .format(dir_loc,self.job_id)
        call(cmd7, shell=True)
        print cmd7

        cmd8 = 'subset_image.py -d 280 282 --rmin 10 --rmax 50 -l 1_values --positive {}/out_{}_inc1468.txt'\
                    .format(dir_loc,self.job_id)
        call(cmd8, shell=True)
        print cmd8

        cmd9 = 'compare_pileup.py --multiplier 1 --sim {}/{}_exp_pileUp_{}.txt {}/subset_out_{}_inc1468.txt'\
                    .format(self.root,self.job_id,orientation_run,dir_loc,self.job_id)
        pile_up_error = check_output(cmd9, shell=True)

        print cmd9
        print "*** load_disp error--",load_disp_error," *** pile_up_error-- ",pile_up_error,"*** orientation -->",orientation,"***"
        error.append(float(load_disp_error) + float(pile_up_error))

    #------------------------------------------------------------------------------------------------- #
        os.chdir('%s'%(self.root))
        orientation_run += 1
    
    avg_error = sum(error)/2.0                                                                         # 2 for each orientation
    print "+++++++++++++++++++++++++++++++++ current fitness and points +++++++++++++++++++++++++++"
    print x
    print float(avg_error)
#    print "                                       %s                                               "%(str(error))
    print "++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
    return float(avg_error)
#    return np.linalg.norm(np.dot(x,x))

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
  print "No file selected for comparison"
if not os.path.exists('%s.dat'%options.job_id):
  parser.error('No job_file selected for mentat')

options.root = os.path.dirname(os.path.realpath(__file__)) if options.root == None else options.root

tick = time.time()
theOptimizer = optimize(method = 'neldermead',
                         bounds = np.array([[20000000,40000000],
                                            [40000000,70000000],
                                            [60000000,80000000], 
                                           ]),
                         tolerance = 0.015,
                         root      = options.root,
                         rigid     = True,
                         )

theOptimizer.info_fitness(options.mat_file,options.job_id,options.exp_file)
theOptimizer.optimize(verbose = False)
tock = time.time()
print "Time for simulation",(tock - tick)
print theOptimizer.cost
print theOptimizer.best()
