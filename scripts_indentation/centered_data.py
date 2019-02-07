#!/usr/bin/env python

import os,sys,damask
import string
from optparse import OptionParser
import numpy as np


scriptID   = string.replace('$Id: centered_data.py 125 2015-10-30 03:37:22Z chakra34 $','\n','\\n')
scriptName = os.path.splitext(scriptID.split()[1])[0]


parser = OptionParser(option_class=damask.extendableOption, usage='%prog options [file[s]]', description = """
Outputs a new grid for the given data field to be centered about the given center and also specifies the offset of the origin.

""", version = scriptID)

parser.add_option('-c','--center',
                  dest = 'center',
                  type = 'int', nargs = 2, metavar = 'int int',
                  help = 'center of the new image ')

parser.add_option('-s', '--size',
                  dest = 'size',
                  action = 'store_true',
                  help = 'if the center position is provided in terms of size [%default]')

parser.add_option('-p','--pix_size',
                  dest = 'pix_size',
                  type = 'string', metavar = 'eval',
                  help = 'pixel size [%default]')

parser.set_defaults(size       = False,
                    fill       = 0.0,
                    pix_size   = '10.0e-6/255',
                   )

(options,filenames) = parser.parse_args()

options.pix_size = eval(options.pix_size)

if options.center == None :
  print "The center has to be provided !!!"
  sys.exit()

else :
# --- loop over input files ------------------------------------------------------------------------

  if filenames == []: filenames = [None]

  for name in filenames:
    try:
      table = damask.ASCIItable(name = name,
                                labeled=False,
                                buffered = False,
                                readonly = True)
    except: continue
    damask.util.report(scriptName,name)

    table.head_read()
    table.data_readArray()
    if options.size :
      options.center = int( options.center / options.pix_size )

    dimension = table.data.shape
    new_grid_x = 2 * max(options.center[0],(dimension[0] - options.center[0]))
    new_grid_y = 2 * max(options.center[1],(dimension[1] - options.center[1]))
    offset = np.array([0,0])
    if new_grid_x/2 == (dimension[0] - options.center[0]) :
      offset[0] = -(dimension[0] - 2 * options.center[0])
    if new_grid_y/2 == (dimension[1] - options.center[1]) :
      offset[1] = -(dimension[1] - 2 * options.center[1])
    print "new_grid",new_grid_x,new_grid_y,"offset",offset[0],offset[1]
    table.close()
