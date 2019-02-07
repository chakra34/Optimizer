#!/usr/bin/env python

import os,sys,damask,string
import numpy as np
import math
from optparse import OptionParser

scriptID   = string.replace('$Id: compare_pileup.py 154 2015-11-06 14:33:26Z chakra34 $','\n','\\n')
scriptName = os.path.splitext(scriptID.split()[1])[0]

parser = OptionParser(option_class=damask.extendableOption, usage='%prog options [file[s]]', description = """
Does a cross correlation between simulated spheroconical indenter tip and tip impression from AFM data to give the spherical fit.

""", version = scriptID)

parser.add_option('--sim',
                  dest = 'sim_file',
                  type = 'string', metavar = 'string',
                  help = 'simulated/file1 to compare with AFM file')

parser.add_option('--error',  action="store_true",
                  dest="error",
                  help="prints out the abs error [False]")

parser.add_option('--multiplier',
                  dest = 'multiplier',
                  type = 'float',
                  help = 'multiplier for matching the values of the two datasets')

parser.add_option('--flipud',  action="store_true",
                   dest="flipud",
                   help="flips up/down - generally required for simulation [False]")


parser.set_defaults(error      = False,
                    flipud     = False,
                   )

(options,filenames) = parser.parse_args()


if options.multiplier == None :
  print "There has to be a multiplier!!!, aborting"
  sys.exit()


if not options.sim_file or not os.path.exists(options.sim_file):
  parser.error('No file selected for comparison')



#------------------- Reading the simulated tip from file -----------------

table1 = damask.ASCIItable(name = options.sim_file, buffered = False,readonly=True)
table1.head_read()
table1.data_readArray()
if options.flipud == True: table1.data = np.flipud(table1.data)

#------------------- loop over input files ------------------------------------ 
if filenames == []: filenames = [None]

for name in filenames:
  try:
    table = damask.ASCIItable(name = name,
                              readonly = True,
                             )
  except: continue

  damask.util.report(scriptName,name)

  table.head_read()
  table.data_readArray()
  table.data = table.data * options.multiplier
  abs_error = abs((table1.data/np.amax(table1.data)) - (table.data/np.amax(table.data)))

#----------------- printing the absolute error if needed ---------------------------#
  if options.error :
    for j in xrange(abs_error.shape[1]):
      for i in xrange(abs_error.shape[0]):
        print abs_error[i,j],
      print
  print ( np.nansum(abs_error)/ np.nansum(table.data/np.amax(table.data)) )



  table.close
