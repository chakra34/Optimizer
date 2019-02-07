#!/usr/bin/env python

import os,sys,damask
import os,sys,string
from optparse import OptionParser
from PIL import Image
import numpy as np


scriptID   = string.replace('$Id: image_crop.py 151 2015-11-06 14:31:17Z chakra34 $','\n','\\n')
scriptName = os.path.splitext(scriptID.split()[1])[0]


parser = OptionParser(option_class=damask.extendableOption, usage='%prog options [file[s]]', description = """
Makes an image transparent based on desired center, inner and outer crop radius.

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
parser.set_defaults(rmin  = 0,
                   )

(options,filenames) = parser.parse_args()

#------------------- loop over input files ------------------------------------ 
if filenames == []: filenames = [None]

for name in filenames:

  damask.util.report(scriptName,name)

  im = Image.open(name).convert("RGBA")
  imArray = np.asarray(im)
  newImArray = np.array(imArray).copy()
  if options.center == None:
    options.center = [imArray.shape[0]/2,imArray.shape[1]/2]
  if options.rmax == None:
    options.rmax = min(abs(imArray.shape[0] - options.center[0]),abs(imArray.shape[1] - options.center[1]))
  for j in xrange(imArray.shape[1]):
    for i in xrange(imArray.shape[0]):
      if ((options.center[0] - i)**2 + (options.center[1] - j)**2) >= (options.rmin)**2 and ((options.center[0] - i)**2 + (options.center[1] - j)**2) <= (options.rmax)**2 :
        newImArray[i,j,3] = 1 * 255
      else :
        newImArray[i,j,3] = 0 * 255
  newIm = Image.fromarray(newImArray,'RGBA')

#------------------- save new image as PNG -------------------------------------
  newIm.save(sys.stdout if not name else os.path.splitext(name)[0]+ "_cropped.png",
          format = "PNG")
