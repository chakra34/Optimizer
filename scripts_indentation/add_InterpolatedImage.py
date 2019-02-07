#!/usr/bin/env python

import numpy as np
import scipy 
import damask
import os,sys,string
from subprocess import call 
from optparse import OptionParser
from scipy.interpolate import griddata


scriptID   = string.replace('$Id: add_InterpolatedImage.py 247 2016-03-22 21:45:34Z chakra34 $','\n','\\n')
scriptName = os.path.splitext(scriptID.split()[1])[0]


parser = OptionParser(option_class=damask.extendableOption, usage='%prog options [file[s]]', description = """
Converts point cloud data to Regular grid and gives the resulting image. 
if pix_size is 1 and size = 3.0 X 3.0 then dimension is 4 X 4.

""", version = scriptID)

parser.add_option('-c','--coords',
                  dest   = 'coords',
                  type = 'string', metavar = 'string',
                  help   = 'column label of point coordinate vector')
parser.add_option('-d','--displacement',
                  dest   = 'disp',
                  type = 'string', metavar = 'string',
                  help   = 'column label of displacement vector')
parser.add_option('--grid',
                  dest = 'grid',
                  type = 'int', nargs = 2, metavar = 'int int',
                  help = 'interpolation grid')
parser.add_option('--size',
                  dest = 'size',
                  type = 'float', nargs = 2, metavar = 'float float',
                  help = 'interpolation size')
parser.add_option('--center',
                  dest = 'center',
                  type = 'float', nargs = 2, metavar = 'float float',
                  help = 'coordinates of interpolation patch center')
parser.add_option('-p','--pixelsize',
                  dest = 'pix_size',
                  type = 'string', metavar = 'string',
                  help = 'pixel size [20.0e-6/255]')


(options,filenames) = parser.parse_args()
#----------------------------------------  sanity checks   ------------------------------------------------

if options.pix_size:
  options.pix_size = float(eval(options.pix_size))
  if options.grid: 
    options.size = tuple(options.pix_size * (x - 1) for x in options.grid)
  elif options.size:
    options.grid = tuple(round(x/options.pix_size + 1) for x in options.size)
    options.size      = tuple(options.pix_size * (x - 1) for x in options.grid)
  else:
    parser.error("Either dimension or size has to be specified if pixel size is given.")
else:
  if options.size and options.grid:
    options.pix_size = options.size/options.grid
  else:
    parser.error("Both dimension and size has to be specified if pixel size is not given.")

# --------------------------------------- loop over input files -------------------------------------------

if filenames == []: filenames = [None]

for name in filenames:
  out_file = "out_"+os.path.basename(name)
  try:
    table = damask.ASCIItable(name     = name, 
                              outname  = out_file,
                              buffered = False)
  except: continue
  damask.util.report(scriptName,name)

# ------------------------------------------ read header and data ------------------------------------------

  table.head_read()
  table.data_readArray([options.coords,options.disp])
  table.data = 1e-6*table.data
  if len(table.data[0]) != 6:
    continue 

#-------------------------------------------- process and store output ---------------------------------------

  table.data[:,:3] += table.data[:,3:6]                                                           # add displacement to coordinates

  if not options.center:
    options.center = 0.5*(table.data[:,:2].max(axis=0)+table.data[:,:2].min(axis=0))
  
#   l = np.array((table.data[:,positions[0]],table.data[:,positions[1]])).T
#   hull = scipy.spatial.Delaunay(l).convex_hull                                              # finding the convex hull to find the center of the point cloud data
#   ps = set()
#   for x,y in hull:
#     ps.add(x)
#     ps.add(y)
#   ps = np.array(list(ps))
#   if options.center == None :
#     options.center = points[ps].mean(axis=0)

  grid_x, grid_y = np.meshgrid(np.linspace(options.center[0] - 0.5 * options.size[0],
                                           options.center[0] + 0.5 * options.size[0], num=options.grid[0]),
                               np.linspace(options.center[1] - 0.5 * options.size[1],
                                           options.center[1] + 0.5 * options.size[1], num=options.grid[1]))
  grid = np.vstack((grid_x.flatten(),grid_y.flatten())).T
  interpolation = griddata(table.data[:,:2], table.data[:,2], grid , fill_value = 0.0,method='linear')
  table.data = np.vstack((grid_x.flatten().T,
                          grid_y.flatten().T,
                          interpolation.T)).T

#--------------------------------------------------- output header info --------------------------------------

  table.labels_clear()
  table.labels_append(['{}_gridInterpolation'.format(1+i) for i in xrange(3)])
  table.info_clear()
  table.info_append(scriptID + '\t' + ' '.join(sys.argv[1:]))
  table.head_write()

  table.data_writeArray()

  table.close()
