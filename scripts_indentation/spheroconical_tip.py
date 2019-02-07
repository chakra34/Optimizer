#!/usr/bin/env python

from  PIL import Image, ImageFont, ImageOps, ImageDraw
import os,sys,string,damask
import numpy as np
import math
from optparse import OptionParser

scriptID   = string.replace('$Id: spheroconical_tip.py 155 2015-11-06 14:34:21Z chakra34 $','\n','\\n')
scriptName = os.path.splitext(scriptID.split()[1])[0]

#-------------------------------- spherical cap of indenter tip -----------------------------

def SphericalCap(r,R):
    "height of sphere surface based on cap radius"
    return R - (R*R - r**2)**0.5
    

#-------------------------------- conical part of indenter tip -----------------------------
def ConicalBase(r,R,alpha):
    "height of conus with opening angle 2alpha running tangential to sphere of radius R"
    return r*math.tan(np.pi/2 - alpha) - R * (1 - math.sin(alpha))/math.sin(alpha)
    

#---------------------------------- arguments -----------------------------------------------

parser = OptionParser(option_class=damask.extendableOption, usage='%prog options [file[s]]', description = """
Generates indenter tip of desired dimension based on spherical Radius, cone half angle and pixel size.

""", version = scriptID)

parser.add_option('--dim',
                  dest = 'dimension',
                  type = 'int', nargs = 2, metavar = 'int int ',
                  help = 'patch dimension in number of pixels [11 X 11] ')
parser.add_option('-r',
                  dest = 'radius',
                  type = 'float', nargs = 1, metavar = 'float ',
                  help = 'Radius of the spherical tip [1.0e-6] ')
parser.add_option('--alpha',
                  dest = 'alpha',
                  type = 'float', nargs = 1, metavar = 'float ',
                  help = 'cone half angle in degrees [45.0] ')
parser.add_option('-p','--pix_size',
                  dest = 'pix_size',
                  type = 'string', metavar = 'eval',
                  help = 'pixel size [20.0e-6/255]')

parser.add_option('--float_pix',
                  dest = 'float_pix',
                  type = 'float',
                  help = 'provide only if pixel size is already calculated')

parser.set_defaults(pix_size   = '20.0e-6/255',
                    dimension  = [11,11],
                    radius     = 1.0e-6,
                    alpha      = 45.0,
                   )
(options,filenames) = parser.parse_args()

#---------------------- process and output -------------------------------------------------

if options.float_pix:
  options.pix_size = (options.float_pix)
else :
  options.pix_size = eval(options.pix_size)
options.alpha    = np.radians(options.alpha)
grid_y,grid_x = np.meshgrid(options.pix_size * np.linspace(- 0.5 * options.dimension[0],0.5 * options.dimension[0] , num=options.dimension[0], endpoint=True),
                            options.pix_size * np.linspace(- 0.5 * options.dimension[0],0.5 * options.dimension[0] , num=options.dimension[0], endpoint=True))
table = damask.ASCIItable()

#--------------------------- append header and info ----------------------------------------

table.info_append(repr(options.pix_size))
table.info_append((options.dimension[0],options.dimension[1]))
table.labels_append(['{}_pos'.format(1+i) for i in range(3)]+ \
                   ['{}_displacement'.format(1+i) for i in range(3)])

table.head_write()

#---------------------------- output result ------------------------------------------------

tip = np.zeros(np.shape(grid_x),dtype=float)
for j in xrange(len(grid_y)):
  for i in xrange(len(grid_x)):
    r = (grid_x[i,j]**2 + grid_y[i,j]**2)**0.5
    tip[i,j] = SphericalCap(r,options.radius) if r < np.cos(options.alpha)* options.radius else ConicalBase(r,options.radius,options.alpha)
    table.data = [grid_x[i,j] + options.pix_size * 0.5 * options.dimension[0],grid_y[i,j] + options.pix_size * 0.5 * options.dimension[1],0,0,0,tip[i,j]]
    outputAlive = table.data_write()
    if not outputAlive: break
  if not outputAlive: break
#------------------------- close ------------------------------------------------------------
table.close()
