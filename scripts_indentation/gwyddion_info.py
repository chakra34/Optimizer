#!/usr/bin/env python
# -*- coding: UTF-8 no BOM -*-

import os,sys
import numpy as np
from optparse import OptionParser, OptionGroup, Option, SUPPRESS_HELP

SI = {'m': 1e0,
      'mm': 1e-3,
      'µm': 1e-6,
      'nm': 1e-9,
     }

scriptID = '$Id: gwyddion_info.py 150 2015-11-06 14:29:21Z chakra34 $'
scriptName = scriptID.split()[1]

parser = OptionParser(usage='%prog options [file[s]]', description = """
find pixelsize from a gwyddion (AFM) file.

""", version = scriptID)

parser.add_option('--pixelsize',
                  dest = 'pixelsize', action = 'store_true',
                  help = 'pixelsize from dimension and shape')

parser.add_option('--width',
                  dest = 'width', action = 'store_true',
                  help = 'width in SI units')

parser.add_option('--height',
                  dest = 'height', action = 'store_true',
                  help = 'height in SI units')

parser.add_option('--shape',
                  dest = 'shape', action = 'store_true',
                  help = 'shape of data array')
parser.add_option('-v','--verbose',
                  dest = 'verbose', action = 'store_true',
                  help = 'report info heading')

(options,filenames) = parser.parse_args()

head = []
if options.pixelsize: head.append('pixelsize')
if options.width: head.append('width/m')
if options.height: head.append('height/m')
if options.shape: head.append('shape(WxH)')
for file in filenames:
  with open(file,'r') as f:
    for line in f:
      pieces = line.split()
      if pieces[0] != '#': break
      if pieces[1] == 'Width:':  width  = float(pieces[2])*SI[pieces[3]]
      if pieces[1] == 'Height:': height = float(pieces[2])*SI[pieces[3]]
      
    elevation = np.loadtxt(file)
    if options.pixelsize:
      pixelsize = height/(elevation.shape[0]-1) if height/(elevation.shape[0]-1) == width/(elevation.shape[1]-1) else 'mismatch'
    else:
      pixelsize = ''
    if not options.width:  width  = ''
    if not options.height: height = ''
    if options.shape:
      shape = 'x'.join(map(str,[elevation.shape[1],elevation.shape[0]]))
    else: shape = ''

    if options.verbose: print ' '.join(head)
    print pixelsize,width,height,shape

