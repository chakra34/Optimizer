#!/usr/bin/env python

import os,sys,damask
import os,sys,string
from optparse import OptionParser
import numpy as np
import math

scriptID   = string.replace('$Id: AFM_to_geom_file.py 131 2015-11-01 17:36:53Z chakra34 $','\n','\\n')
scriptName = os.path.splitext(scriptID.split()[1])[0]

parser = OptionParser(option_class=damask.extendableOption, usage='%prog options [file[s]]', description = """
Makes an input ASCII data to a geom format (DAMASK) .

""", version = scriptID)

parser.add_option('-p','--pix_size',
                  dest = 'pix_size',
                  type = 'string', metavar = 'eval',
                  help = 'pixel size [%default]')


parser.set_defaults(pix_size   = '10.0e-6/255',
                   )

(options,filenames) = parser.parse_args()

options.pix_size = eval(options.pix_size)
options.pix_size *= 1e6
# --- loop over input files ------------------------------------------------------------------------

if filenames == []: filenames = [None]

for name in filenames:
  try:
    out = name.split('.000')[0]
    ext = name.split('.')[1]
    table = damask.ASCIItable(name = name,
                              outname = out+"_geom."+ext,
                              labeled = False,
                              buffered = False,
                              readonly = True)
  except: continue
  damask.util.report(scriptName,name)
  table.head_read()
  table.data_readArray()
  table.labels_clear()
  table.info_clear()
  table.info_append([
    scriptID + ' ' + ' '.join(sys.argv[1:]),
    "grid\ta {}\tb {}\tc 1".format(table.data.shape[0], table.data.shape[1]),
    "size\tx {}\ty {}\tz 1".format(options.pix_size * (table.data.shape[0] - 1), options.pix_size * (table.data.shape[1] - 1)),
    "origin\tx 0.0\ty 0.0\tz 0.0",
    "homogenization\t1",
    ])
  table.head_write()
  table.data_writeArray()
  table.close()