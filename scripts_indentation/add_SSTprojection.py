#!/usr/bin/env python

import os,sys,damask
import os,sys,string
from optparse import OptionParser
import numpy as np
import math

scriptID   = string.replace('$Id: add_SSTprojection.py 61 2015-09-12 17:53:29Z chakra34 $','\n','\\n')
scriptName = os.path.splitext(scriptID.split()[1])[0]


parser = OptionParser(option_class=damask.extendableOption, usage='%prog options [file[s]]', description = """
Adds positions for placing in SST (either homochoric or stereographic) .

""", version = scriptID)

parser.add_option('-p','--projection',
                  dest = 'projection',
                  type = 'string', metavar = 'string',
                  help = 'homochoric or stereographic projection [%default]')

parser.add_option('-s', '--symmetry',
                  dest = 'symmetry',
                  type = 'choice', choices = damask.Symmetry.lattices[1:], metavar='string',
                  help = 'crystal symmetry [%default] {{{}}} '.format(', '.join(damask.Symmetry.lattices[1:])))
parser.add_option("--proper",  action="store_true",
                  dest="proper",
                  help="proper (double) or improper (single) standard triangle [%default]")
parser.add_option('-e', '--eulers',
                  dest = 'eulers',
                  type = 'string', metavar = 'string',
                  help = 'Euler angles label')
parser.add_option('-d', '--degrees',
                  dest = 'degrees',
                  action = 'store_true',
                  help = 'Euler angles are given in degrees [%default]')
parser.add_option('-m', '--matrix',
                  dest = 'matrix',
                  type = 'string', metavar = 'string',
                  help = 'orientation matrix label')
parser.add_option('-a',
                  dest = 'a',
                  type = 'string', metavar = 'string',
                  help = 'crystal frame a vector label')
parser.add_option('-b',
                  dest = 'b',
                  type = 'string', metavar = 'string',
                  help = 'crystal frame b vector label')
parser.add_option('-c',
                  dest = 'c',
                  type = 'string', metavar = 'string',
                  help = 'crystal frame c vector label')
parser.add_option('-q', '--quaternion',
                  dest = 'quaternion',
                  type = 'string', metavar = 'string',
                  help = 'quaternion label')

parser.set_defaults(projection = 'stereographic',
                    symmetry = damask.Symmetry.lattices[-1],
                    degrees = False,
                    proper     = False,
                   )

(options, filenames) = parser.parse_args()

input = [options.eulers     != None,
         options.a          != None and \
         options.b          != None and \
         options.c          != None,
         options.matrix     != None,
         options.quaternion != None,
        ]

if np.sum(input) != 1: parser.error('needs exactly one input format.')

(label,dim,inputtype) = [(options.eulers,3,'eulers'),
                         ([options.a,options.b,options.c],[3,3,3],'frame'),
                         (options.matrix,9,'matrix'),
                         (options.quaternion,4,'quaternion'),
                        ][np.where(input)[0][0]]                                                    # select input label that was requested
toRadians = math.pi/180.0 if options.degrees else 1.0                                               # rescale degrees to radians

# --- loop over input files ------------------------------------------------------------------------

if filenames == []: filenames = [None]

for name in filenames:
  try:
    table = damask.ASCIItable(name = name,
                              buffered = False)
  except: continue
  damask.util.report(scriptName,name)

# ------------------------------------------ read header ------------------------------------------

  table.head_read()

# ------------------------------------------ sanity checks ----------------------------------------

  if not np.all(table.label_dimension(label) == dim):
    damask.util.croak('input {} has wrong dimension {}.'.format(label,dim))
    table.close(dismiss = True)                                                                     # close ASCIItable and remove empty file
    continue

  column = table.label_index(label)

# ------------------------------------------ assemble header ---------------------------------------
  if options.proper == True:
    type = "proper"
  else :
    type = "improper"
  table.info_append(scriptID + '\t' + ' '.join(sys.argv[1:]))
  table.labels_append(['{}_SST({})'.format(1+i,type) for i in xrange(2)])
  table.head_write()

# ------------------------------------------ process data ------------------------------------------

  outputAlive = True
  while outputAlive and table.data_read():                                                          # read next data line of ASCII table
    if inputtype == 'eulers':
      o = damask.Orientation(Eulers   = np.array(map(float,table.data[column:column+3]))*toRadians,
                             symmetry = options.symmetry).reduced()
    elif inputtype == 'matrix':
      o = damask.Orientation(matrix   = np.array(map(float,table.data[column:column+9])).reshape(3,3).transpose(),
                             symmetry = options.symmetry).reduced()
    elif inputtype == 'frame':
      o = damask.Orientation(matrix = np.array(map(float,table.data[column[0]:column[0]+3] + \
                                                         table.data[column[1]:column[1]+3] + \
                                                         table.data[column[2]:column[2]+3])).reshape(3,3),
                             symmetry = options.symmetry).reduced()
    elif inputtype == 'quaternion':
      o = damask.Orientation(quaternion = np.array(map(float,table.data[column:column+4])),
                             symmetry   = options.symmetry).reduced()
    vector,symOp = o.inversePole([0.,0.,1.], proper=options.proper)
    if options.projection == "homochoric" :
      X = vector[0] * math.sqrt( 1. /(1. + abs(vector[2])) )
      Y = vector[1] * math.sqrt( 1. /(1. + abs(vector[2])) )
    else :
      X = vector[0] /(1. + abs(vector[2]))
      Y = vector[1] /(1. + abs(vector[2]))
    table.data_append((X,Y))
    outputAlive = table.data_write()                                                                # output processed line

# ------------------------------------------ output finalization -----------------------------------  

  table.close()                                                                                     # close ASCII tables

