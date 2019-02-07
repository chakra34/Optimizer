#!/usr/bin/env python

#from  PIL import Image, ImageFont, ImageOps, ImageDraw
import os,sys,damask,string
import numpy as np
#from matplotlib import cm
#import matplotlib.pyplot as plt
#from scipy import signal
#from mpl_toolkits.mplot3d import Axes3D
import math
from optparse import OptionParser


scriptID   = string.replace('$Id: subset_image.py 154 2015-11-06 14:33:26Z chakra34 $','\n','\\n')
scriptName = os.path.splitext(scriptID.split()[1])[0]

parser = OptionParser(option_class=damask.extendableOption, usage='%prog options [file[s]]', description = """
Does a cross correlation between simulated spheroconical indenter tip and tip impression from AFM data to give the spherical fit.

""", version = scriptID)
parser.add_option('-c','--center',
                  dest = 'center',
                  type = 'int', nargs = 2, metavar = 'int int',
                  help = 'center of circular cropping [image center]')
parser.add_option('--rmin',
                  dest = 'rmin',
                  type = 'int',
                  help = 'inner crop radius [%default]')
parser.add_option('--rmax',
                  dest = 'rmax',
                  type = 'int',
                  help = 'outer crop radius (number of pixels) [max fit]')
parser.add_option('-d','--dimension',
                  dest = 'dimension',
                  type = 'int', nargs = 2, metavar = 'int int',
                  help = 'data dimension (width height) [native]')
parser.add_option('-l','--label',
                  dest = 'label',
                  type = 'string', metavar = 'string',
                  help = 'column containing data [all]')

parser.add_option('--afm',  action="store_true",
                  dest="afm",
                  help="if the given file is AFM file format [False]")

parser.add_option('--positive',  action="store_true",
                  dest="positive",
                  help="considering only positive values [False]")

parser.add_option('--new',
                  dest = 'new_d',
                  type = 'int', nargs = 2, metavar = 'int int',
                  help = 'new data dimension ')

parser.set_defaults(rmin  = 0,
                    afm   = False,
                    positive = False,
                   )

(options,filenames) = parser.parse_args()
if not options.new_d:
  options.new_d = [options.rmax,options.rmax]

#------------------- loop over input files ------------------------------------ 
if filenames == []: filenames = [None]

for name in filenames:
  try:
    table = damask.ASCIItable(name = name,
                              outname = "subset_"+os.path.basename(name),
                              readonly = True,
                             )
  except: continue

  damask.util.report(scriptName,name)

  table.head_read()
  table.data_readArray(options.label)
  if options.afm == False :
    if options.dimension[0] * options.dimension[1] != table.data.shape[0] :
      if options.dimension[0] * options.dimension[1] != table.data.shape[1]:
        print "dimensions do not match"
        sys.exit()
  else :
    table.data = np.fliplr(table.data)
    options.dimension = np.array([table.data.shape[1], table.data.shape[0]])
  if options.center == None:
    options.center = [options.dimension[0]/2,options.dimension[1]/2]
  if options.rmax == None:
    options.rmax = min(abs(options.dimension[0] - options.center[0]),abs(options.dimension[1] - options.center[1]))
  if options.positive == True:
    np.place(table.data,table.data<0, 0.0)
  data = table.data.reshape((options.dimension[1],options.dimension[0]))
  for j in xrange(options.dimension[0]):
    for i in xrange(options.dimension[1]):
      if ((options.center[0] - i)**2 + (options.center[1] - j)**2) >= (options.rmin)**2 and ((options.center[0] - i)**2 + (options.center[1] - j)**2) <= (options.rmax)**2 :
        data[i,j]
        
      else:
        data[i,j] = 0.0
  
  with open('subset_sim.txt','w') as subset_output:
    subset_output.write("1 head\n")
    subset_output.write("values\n")
  temp_data = np.ones((options.new_d[0],options.new_d[1]))
  for i in xrange(-options.new_d[0],options.new_d[0]):
    for j in xrange(-options.new_d[1],options.new_d[1]):
      temp_data[i,j] = data[options.center[0]- i, options.center[1]- j]
      with open('subset_sim.txt','a') as subset_output:
        subset_output.write("%s "%temp_data[i,j])
    with open('subset_sim.txt','a') as subset_output:
      subset_output.write("\n")

  table.labels_clear()
  table.labels_append(options.label)
  table.head_write()



  table.data = data
  table.data_writeArray()



#   print "1 head"
#   print "Displacement"
#   for j in xrange(data.shape[1]):
#     for i in xrange(data.shape[0]):
#       print data[i,j],
#     print
  table.close
