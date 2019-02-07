#!/usr/bin/env python

from  PIL import Image, ImageFont, ImageOps, ImageDraw
import os,sys,damask,string
import numpy as np
from matplotlib import cm
import matplotlib.pyplot as plt
from scipy import signal
from mpl_toolkits.mplot3d import Axes3D
import math
from optparse import OptionParser


scriptID   = string.replace('$Id: out_TopographyMin_SphericalFit.py 154 2015-11-06 14:33:26Z chakra34 $','\n','\\n')
scriptName = os.path.splitext(scriptID.split()[1])[0]

parser = OptionParser(option_class=damask.extendableOption, usage='%prog options [file[s]]', description = """
Does a cross correlation between simulated spheroconical indenter tip and tip impression from AFM data to give the spherical fit.

""", version = scriptID)




parser.add_option(      '--tip',
                  dest = 'tip_file',
                  type = 'string', metavar = 'string',
                  help = '(tip) file to compare with AFM file')

parser.add_option('-d','--disp',
                  dest = 'values',
                  type = 'string',
                  help = 'column label of (displacement) values for comparison [%default]')

parser.set_defaults(values  = "3_displacement",
                    patch   = (11,11),
                   )

(options,filenames) = parser.parse_args()


if not options.tip_file or not os.path.exists(options.tip_file):
  parser.error('No file selected for comparison')



#------------------- Reading the simulated tip from file -----------------

table1 = damask.ASCIItable(name = options.tip_file, buffered = False)
table1.head_read()
table1.data_readArray()
index = table1.label_index(options.values)
size = table1.data[:,index].shape
size = [ int(table1.info[1]), int(table1.info[2]) ]
tip = np.array(table1.data[:,index]).reshape(size[0],size[1])


#------------------- Reading AFM Data ------------------------------------ 
if filenames == []: filenames = [None]

for name in filenames:
  try:
    table = damask.ASCIItable(name = name,
                              buffered = False,
                              labeled = False,
                              readonly = True)
  except: continue
  damask.util.report(scriptName,name)

  table.head_read()
  table.data_readArray()

  #-----------------------------------------------------------------------------
  AFM_min = table.data.min()


  tip += AFM_min

  global_y,global_x = np.unravel_index(np.argmin(table.data), table.data.shape)
  global_z          = AFM_min

  print "global",global_x,global_y,global_z,
  #---------------------------- Correlation ---------------------------

  template = tip
  corr = signal.correlate2d(table.data, template, mode ='same')
  spherical_fit_y,spherical_fit_x = np.unravel_index(np.argmax(corr), corr.shape)
  #---------------------------------------------------------------------

  # print "Depth at maximum correlation for AFM_data", table.data[ver,hor]

  template_data = table.data[spherical_fit_y - ((size[0])/2) : spherical_fit_y + ((size[0])/2)  , \
                           spherical_fit_x - (size[1]/2) : spherical_fit_x + (size[1]/2)  ]
  if size[0] % 2 != 0 :
    template_data = table.data[spherical_fit_y - ((size[0] - 1)/2) : spherical_fit_y + ((size[0] + 1)/2) , \
                             spherical_fit_x - (size[1]/2) : spherical_fit_x + (size[1]/2) ]
  if size[1] % 2 != 0 :  
    template_data = table.data[spherical_fit_y - (size[0]/2) : spherical_fit_y + (size[0]/2) , \
                             spherical_fit_x - ((size[1] - 1)/2) : spherical_fit_x + ((size[1] + 1)/2) ]
  if size[1] % 2 != 0 and size[0]/2 != 0 :  
    template_data = table.data[spherical_fit_y - ((size[0] - 1)/2) : spherical_fit_y + ((size[0] + 1)/2) , \
                             spherical_fit_x - ((size[1] - 1)/2) : spherical_fit_x + ((size[1] + 1)/2) ]

  #--------------------------- Linear Search of Max indent at min error ------------- 

  """ Change indent height based on min of AFM data """

  offset = np.linspace(-1e-6,1e-6,100000)
  sum = []
  pos = 0.0
  y = np.nansum((template_data - tip)**2)
  for d in offset:
      template3 = tip + d
      sum.append(np.nansum((template3 - template_data)**2))
      if np.nansum((template3 - template_data)**2) < y:
        y = np.nansum((template3 - template_data)**2)
        pos = d

  #--------------------------------------------------------------------------------------
  spherical_fit_z = AFM_min + pos
  print "spherical",spherical_fit_x,spherical_fit_y,spherical_fit_z
  
  table.close()
