#!/usr/bin/env python
# -*- coding: UTF-8 no BOM -*-

import os,sys,string,math
from optparse import OptionParser
import numpy as np
import damask

scriptID   = string.replace('$Id: geom_fromGwyddion.py 148 2015-11-06 14:28:06Z chakra34 $','\n','\\n')
scriptName = os.path.splitext(scriptID.split()[1])[0]


SI = {'m': 1e0,
      'mm': 1e-3,
      'µm': 1e-6,
      u'µ': 1e-6,
      'nm': 1e-9,
     }


scriptID   = string.replace('$Id: geom_fromGwyddion.py 148 2015-11-06 14:28:06Z chakra34 $','\n','\\n')
scriptName = os.path.splitext(scriptID.split()[1])[0]

parser = OptionParser( usage='%prog options [file[s]]', description = """
creates a geom file from a Gwyddion output .

""", version = scriptID)

(options,filenames) = parser.parse_args()

# --- loop over input files ------------------------------------------------------------------------

if filenames == []: filenames = [None]

for file in filenames:
  size = np.zeros(2,'f')
  with open(file,'r') as f:
    for line in f:
      pieces = line.split()
      if pieces[0] != '#': break
      if pieces[1] == 'Width:':  size[1]  = float(pieces[2])*SI[pieces[3]]
      if pieces[1] == 'Height:': size[0] = float(pieces[2])*SI[pieces[3]]
    elevation = np.loadtxt(file)
  pixelsize = size/elevation.shape
  with open ('%s.geom'%(os.path.splitext(file)[0]),'w') as new:

# #------------------- adding geom information -----------------------------------------------------
    new.write('\n'.join(["5 head",
                        scriptID + ' ' + ' '.join(sys.argv[1:]),
                        "grid\ta {}\tb {}\tc 1".format(elevation.shape[1], elevation.shape[0]),
                        "size\tx {}\ty {}\tz {}".format(size[1] , size[0] , np.average(pixelsize)),
                        "origin\tx 0.0\ty 0.0\tz 0.0",
                        "homogenization\t1",
                      ]) + '\n')

# -------------------- close table ------------------------------------------------------------
    with open(file,'r') as f:
      for line in f.readlines():
        if line[0] != '#' :
          new.write(line)