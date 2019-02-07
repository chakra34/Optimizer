#!/usr/bin/env python

from  PIL import Image, ImageFont, ImageOps, ImageDraw
import os,sys,damask,string
import numpy as np
from matplotlib import cm
import matplotlib.pyplot as plt
from scipy import signal
from mpl_toolkits.mplot3d import Axes3D
import math

"""  Does a cross correlation between simulated spheroconical indenter tip and tip impression from AFM data """


scriptID   = string.replace('$Id: Correlation_AFM.py 157 2015-11-06 14:37:59Z chakra34 $','\n','\\n')

AFM_filename = sys.argv[1]                                                                 # AFM file name
filename     = sys.argv[2]                                                                 # simulated tip file name
tip_data     = string(sys.argv[3]) if len(sys.argv) > 3 else "3_displacement" 
N            = int(sys.argv[4]) if len(sys.argv) > 4 else 11                         # patch dimension in pixel

#------------------- Reading the simulated tip from file -----------------

table1 = damask.ASCIItable(name = filename, buffered = False)
table1.head_read()
table1.data_readArray()

file = open(filename)
index = table1.label_index(tip_data)
tip = np.array(table1.data[:,index]).reshape(N,N)

#------------------- Reading AFM Data ------------------------------------ 

table = damask.ASCIItable(name = AFM_filename,
                          buffered = False,
                          labeled = False,
                          readonly = True)
table.head_read()
table.data_readArray()
table.data = table.data
#-----------------------------------------------------------------------------

AFM_min = table.data.min()

plt.contourf(tip,cmap='gray')
plt.colorbar()
plt.title('Simulated Indenter tip before AFM_min')
plt.show()

tip += AFM_min

print "Position of AFM min",np.unravel_index(np.argmin(table.data), table.data.shape)
print "Position of Tip min",np.unravel_index(np.argmin(tip), tip.shape)

#---------------------------- Correlation ---------------------------

template = tip
corr = signal.correlate2d(table.data, template, mode ='same')
ver,hor = np.unravel_index(np.argmax(corr), corr.shape)
#---------------------------------------------------------------------

print "Position of Max correlation",np.unravel_index(np.argmax(corr), corr.shape)
print "y-axis ", ver 
print "x-axis ",hor
print "AFM min", AFM_min
print "Depth at maximum correlation for AFM_data", table.data[ver,hor]

plt.contourf(tip,cmap='gray')
plt.colorbar()
plt.title('Simulated Indenter tip')
plt.show()
plt.contourf(table.data,cmap='gray')
plt.colorbar()
plt.title('AFM Data')
plt.show()
plt.contourf(corr,cmap='gray')
plt.colorbar()
plt.title('Correlation')
plt.show()

template_data = table.data[ver - (N/2): ver + N/2 + 1 , hor - (N/2): hor + N/2 +1]
print 'data min',np.unravel_index(np.argmin(template_data), template_data.shape)
print 'tip min',np.unravel_index(np.argmin(tip), tip.shape)

plt.contourf(template_data,cmap='gray')
plt.colorbar()
plt.title('Template from AFM data')
plt.show()

#--------------------------- Linear Search of Max indent at min error ------------- 

""" Change indent height based on min of AFM data """

offset = np.linspace(-1e-6,1e-6,100000)
sum = []
pos = 0.0
y = np.nansum((template_data - tip)**2)                                             # initializing a value
for d in offset:
    template3 = tip + d                                                             # varying the 'z' of the spherical tip to see where it best fits the experimental data
    sum.append(np.nansum((template3 - template_data)**2))
    if np.nansum((template3 - template_data)**2) < y:                               # least sum of square of errors is the best fit
      y = np.nansum((template3 - template_data)**2)
      pos = d

#--------------------------------------------------------------------------------------
depth = AFM_min + pos
print "Total Depth after Error Minimization" ,depth
plt.contourf((template_data -(tip + pos)),cmap='gray')                            # actual AFM data vs the best fit found from above algorithm
plt.colorbar()
plt.title('Error in AFM and Simulated tip')
plt.show()

#------------------------ for outputting a particular part of AFM data ------------------
# pix_size = 10.0e-6/255
# dim = 8e-6/pix_size
# template_data_2 = table.data[ver - (dim/2): ver + dim/2 + 1 , hor - (dim/2): hor + dim/2 +1]
# print template_data_2.shape
# print "1 head "
# print "values "
# for i in xrange(template_data_2.shape[0]):
#   for j in xrange(template_data_2.shape[1]):
#     print template_data_2[i,j],
#   print
