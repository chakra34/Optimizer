#!/usr/bin/env python

import os,sys,damask
import os,sys,string
from optparse import OptionParser
import numpy as np
from scipy import interpolate
import math

scriptID   = string.replace('$Id: chopTable.py 153 2015-11-06 14:32:50Z chakra34 $','\n','\\n')
scriptName = os.path.splitext(scriptID.split()[1])[0]

parser = OptionParser(option_class=damask.extendableOption, usage='%prog options [file[s]]', description = """
in .

""", version = scriptID)

parser.add_option('--expX',
                  dest = 'expX',
                  type = 'string',
                  help = 'xcolumn label of experimental file')

parser.add_option('--expY',
                  dest = 'expY',
                  type = 'string',
                  help = 'ycolumn label of experimental file')

parser.add_option('--simX',
                  dest = 'simX',
                  type = 'string',
                  help = 'xcolumn label of simulated file')

parser.add_option('--simY',
                  dest = 'simY',
                  type = 'string',
                  help = 'ycolumn label of simulated file')

parser.add_option(      '--expfile',
                  dest = 'expfile',
                  type = 'string', metavar = 'string',
                  help = 'experimental file to interpolat')

parser.add_option(      '--simfile',
                  dest = 'simfile',
                  type = 'string', metavar = 'string',
                  help = 'simulated file to interpolate')

parser.add_option('--show',  action="store_true",
                  dest="show",
                  help="showing the interpolated result [False]")

parser.set_defaults(show = False,
                   )

(options, filenames) = parser.parse_args()

table_exp = damask.ASCIItable(name = options.expfile, buffered = False, readonly = True)
table_exp.head_read()
table_exp.data_readArray((options.expX,options.expY))
x_exp_index = table_exp.label_index(options.expX)
y_exp_index = table_exp.label_index(options.expY)
x_exp_data = table_exp.data[:,x_exp_index]
y_exp_data = table_exp.data[:,y_exp_index]

table_sim = damask.ASCIItable(name = options.simfile, buffered = False, readonly = True)
table_sim.head_read()
table_sim.data_readArray((options.simX,options.simY))
x_sim_index = table_sim.label_index(options.simX)
y_sim_index = table_sim.label_index(options.simY)

x_sim_data = table_sim.data[:,x_sim_index]
y_sim_data = table_sim.data[:,y_sim_index]

last_sim_x = x_sim_data[len(x_sim_data)-1]
last_exp_x = x_exp_data[len(x_exp_data)-1]

x_sim_data = np.array(x_sim_data)
if last_sim_x > last_exp_x :
  x_sim_data = np.delete(x_sim_data,len(x_sim_data)-1)
  y_sim_data = np.delete(y_sim_data,len(y_sim_data)-1)

if last_exp_x > last_sim_x :
  x_exp_data = np.delete(x_exp_data,len(x_exp_data)-1)
  y_exp_data = np.delete(y_exp_data,len(y_exp_data)-1)

# --- loop over input files ------------------------------------------------------------------------

new_X = np.sort(np.concatenate((x_exp_data,x_sim_data)))
new_Y_sim = np.ones(new_X.size)*np.nan
new_Y_exp = np.ones(new_X.size)*np.nan
new_array = np.array((new_X,new_Y_sim,new_Y_exp)).T
function_sim = interpolate.InterpolatedUnivariateSpline(x_sim_data,y_sim_data,k=1)          # k=1 gives a linear interpolation
function_exp = interpolate.InterpolatedUnivariateSpline(x_exp_data,y_exp_data,k=1)

for pos,val in enumerate(table_sim.data[:,x_sim_index]):
  if val in new_array[:,0]:
    new_array[np.where(val == new_array[:,0])[0][0] , 1 ] = table_sim.data[pos,y_sim_index]
for pos,val in enumerate(table_exp.data[:,x_exp_index]):
  if val in new_array[:,0]:
    new_array[np.where(val == new_array[:,0])[0][0] , 2 ] = table_exp.data[pos,y_sim_index]

interpolate_indices_sim = np.where(np.isnan(new_array[:,1]) == True)
interpolate_indices_exp = np.where(np.isnan(new_array[:,2]) == True)
for i in interpolate_indices_sim :
  new_array[i,1] = function_sim(new_array[i,0])
for i in interpolate_indices_exp :
  new_array[i,2] = function_exp(new_array[i,0])

new_array = new_array[~np.isnan(new_array).any(axis=1)]
if options.show == True:
  print "1 head "
  print ' '.join(('new_X',options.simY,options.expY))
  for i in xrange(new_array.shape[0]):
    for j in xrange(new_array.shape[1]):
      print new_array[i,j],
    print
  
#---- Error Integral ---------------------------------------------------------#
error = 0.0
a = 0.0
b = 0.0
exp_area = 0.0
for i in xrange(new_array.shape[0] - 1):
  a = abs( new_array[i,1]   - new_array[i,2]   )
  b = abs( new_array[i+1,1] - new_array[i+1,2] )
  h = abs( new_array[i,0] - new_array[i+1,0] )
  error += 0.5 * (a + b) * h
  exp_area += 0.5 * abs(new_array[i,2] + new_array[i+1,2]) * h
print error/exp_area
