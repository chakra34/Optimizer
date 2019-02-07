#!/usr/bin/env python

import os,sys,damask
import os,sys,string
from optparse import OptionParser
import numpy as np


scriptID   = string.replace('$Id: AFM_gridData.py 61 2015-09-12 17:53:29Z chakra34 $','\n','\\n')
scriptName = os.path.splitext(scriptID.split()[1])[0]


parser = OptionParser(option_class=damask.extendableOption, usage='%prog options [file[s]]', description = """
Generates ASCII table from AFM data.

""", version = scriptID)

parser.add_option('-p','--pix_size',
                  dest = 'pix_size',
                  type = 'string', metavar = 'eval',
                  help = 'pixel size [20.0e-6/255]')

parser.set_defaults(pix_size   = '20.0e-6/255',
                   )

(options,filenames) = parser.parse_args()

options.pix_size = eval(options.pix_size)

#------------------- loop over input files ------------------------------------ 
if filenames == []: filenames = [None]

for name in filenames:
  out_file = "out_"+name
  try:
    table = damask.ASCIItable(name = name,
                            outname = "out_"+ name,
                            buffered = False,
                           )
  except:
    continue
  table.croak(damask.util.emph(scriptName)+(': '+name if name else ''))

#-------------------------- reading head and generating grid -----------------------------

  table.head_read()
  table.data_readArray()
  grid = np.array([table.data.shape[1],table.data.shape[0]],dtype=int)

#-------------------------------process and output result  --------------------------------

  table.info_clear()
  table.labels_clear()
  table.info_append("max indent depth (min value): {}".format(table.data.min()))
  table.labels_append(['{}_pos'.format(1+i) for i in xrange(3)]+ \
                      ['{}_displacement'.format(1+i) for i in xrange(3)])

  table.head_write()
  
  grid_x,grid_y = np.meshgrid(np.arange(grid[0]),np.arange(grid[1]))

  grid_x = grid_x.reshape(grid.prod()).astype(object)
  grid_y = grid_y.reshape(grid.prod()).astype(object)
  h      = table.data.reshape(grid.prod()).astype(object)
  grid_z = np.zeros(np.shape(grid_x)).astype(object)
  table.data = np.vstack((options.pix_size * grid_x,options.pix_size * grid_y.astype(int),grid_z.astype(int),grid_z,grid_z,h)).T
  table.data_writeArray()
#----------------------------------   close table     ------------------------------------
  table.close()