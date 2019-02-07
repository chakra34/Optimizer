#!/usr/bin/env python

import os,sys,damask
import os,sys,string
from optparse import OptionParser
import numpy as np
import math

scriptID   = string.replace('$Id: out_size.py 153 2015-11-06 14:32:50Z chakra34 $','\n','\\n')
scriptName = os.path.splitext(scriptID.split()[1])[0]

parser = OptionParser(option_class=damask.extendableOption, usage='%prog options [file[s]]', description = """
prints the size of the file (as ASCII table) .

""", version = scriptID)

(options, filenames) = parser.parse_args()

# --- loop over input files ------------------------------------------------------------------------

if filenames == []: filenames = [None]

for name in filenames:
  try:
    table = damask.ASCIItable(name = name,
                              readonly = True,
                              buffered = False,
                             )
  except: continue

  damask.util.report(scriptName,name)
  table.head_read()
  table.data_readArray()
  print table.data.shape[0],table.data.shape[1]
  for i in xrange(table.data.shape[1]):
	print  np.amax(table.data[:,i])
  table.close()
