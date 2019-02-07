#!/usr/bin/env python

import os,sys,damask
import damask,string
from optparse import OptionParser
import numpy as np
from subprocess import call
import math


scriptID   = string.replace('$Id: latex_it.py 192 2015-11-11 17:26:30Z chakra34 $','\n','\\n')
scriptName = os.path.splitext(scriptID.split()[1])[0]

def generate_tex(section):
  if section == 'footer' :
   return'\n'.join(['\n\\end{scope}\n',
                    '\\end{scope}',
                    '\\end{tikzpicture}'
])


parser = OptionParser(option_class=damask.extendableOption, usage='%prog options [file[s]]', description = """
Discretizes a spherical triangle equally based on degrees of runs.

""", version = scriptID)

parser.add_option('--symm',
                  dest = 'symmetry',
                  type = 'string',
                  help = 'symmetry [cubic]')

parser.add_option("--proper",  action="store_true",
                  dest="proper",
                  help="proper triangle or not [False]")


parser.add_option('-S','--SST',
                  dest = 'SST',
                  type = 'string',
                  help = ' label of SST positions')

parser.add_option('-a','--angle',
                  dest = 'theta',
                  type = 'string',
                  help = 'theta (in plane rotation ) label ')

parser.add_option('-p','--patch',
                  dest = 'patch',
                  type = 'string',
                  help = 'patch name ')




parser.set_defaults(symmetry    = 'cubic',
                    proper      = False,
                   )

(options,filenames) = parser.parse_args()

if options.patch == None:
  print "Must provide a patch name ..."
  sys.exit()
else:
# Getting the path from where its executed
  script_path = os.path.dirname(sys.argv[0])
  os.chdir(os.path.dirname(sys.argv[0]))

#------------------- loop over input files ------------------------------------ 
  if filenames == []: filenames = [None]

  for name in filenames:
    try:
      table = damask.ASCIItable(name = name,
                              buffered = False,
                             )
    except: continue
    damask.util.report(scriptName,name)

#-------------------------- reading head and generating grid -----------------------------

    table.head_read()
    table.data_readArray()
    if options.proper :
      type = "proper"
    else :
      type = "improper"
    range = table.label_indexrange(options.SST)
    theta = table.label_index(options.theta)
#-------------------------------process and output result  --------------------------------
    header = open('%s_%s.tex'%(options.symmetry,type))
    new    = open('IPF_%s_indents_%s.tex'%(type,options.patch),'w')
    new.write('\\documentclass{article}\n')
    for line in header.readlines():
      new.write(line)
    for j in xrange(len(table.data[:,0])):
      if table.data[j,table.label_index('AFM_done')] == 1 :
        out = "%s/../experiment/Sn/%s/AFM/processed/%s/%s%s_cropped.png"%(script_path, 
                                                                              options.patch, 
                                                                              str(int(table.data[j,table.label_index('indent_ID')])), 
                                                                              options.patch, 
                                                                              str(int(table.data[j,table.label_index('indent_ID')])) )
        new.write('\n\\node [label = {{ [xshift = -0.5cm, yshift = -0.5cm ] \\tiny {} }}] at ({},{}) {{\includegraphics[angle = {},scale=0.2]{{{}}} }};'.format(str(int(table.data[j,table.label_index('indent_ID')])), \
                                                                                                                                                                        table.data[j,range[0]], \
                                                                                                                                                                        table.data[j,range[1]], \
                                                                                                                                                                        table.data[j,theta], \
                                                                                                                                                                        out) ) 


    new.write(generate_tex('footer'))
    new.close()
