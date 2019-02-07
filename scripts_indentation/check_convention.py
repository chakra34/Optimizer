#!/usr/bin/env python

import os,sys,damask
import damask,string
from optparse import OptionParser
import numpy as np
from subprocess import call
import math


#----------------------------------------------#
def generate_tex(section):

  if section == 'header' :
   return'\n'.join(['\\documentclass{article}',
                    '\\usepackage{tikz}\n',
                    '\\usetikzlibrary{shapes,arrows}\n',
                    '\\usepackage{miller}\n',
                    '\\usepackage[graphics, active, tightpage]{preview}\n',
                    '\\PreviewEnvironment{tikzpicture}\n',
                    '\\begin{document}\n',
                    '\\thispagestyle{empty}\n',
                    '\\begin{tikzpicture}',
                    '\\begin{scope}[x=19.313708cm,y=19.313708cm]',
                    '\\draw[line width=1.0pt] (0,0) -- (1,0);',
                    '\\draw[line width=1.0pt] (1,0) arc(0:45:1);',
                    '\\draw[line width=1.0pt] (0,0) -- (0.707107,0.707107);',
                    '\\begin{scope}[inner sep=0pt]',
                    '\\node[fill,rectangle,minimum height=6pt,minimum width=6pt,label={below left:\\small\\hkl<001>}] at (0.000000,0.000000) {};',
                    '\\node[fill,diamond,minimum height=12pt,minimum width=6pt,label={below right:\\small\\hkl<100>}] at (1.000000,0.000000) {};',
                    '\\node[fill,ellipse,minimum height=6pt,minimum width=6pt,label={above right:\\small\\hkl<110>}] at (0.707107,0.707107) {};',
                    '\\end{scope}\n',
                    '\\begin{scope}',
                    '\\end{scope}\n',
                    '\\begin{scope}[inner sep=1.0pt]\n'])
  elif section == 'footer' :
   return'\n'.join(['\\end{scope}\n',
                    '\\end{scope}',
                    '\\end{tikzpicture}',
                    '\\end{document}'])
#------------------------------------------------------#

#-------------------------- Calculation of Orientation matrix -------------------------------

def OrientationMatrix(phi1,PHI,phi2):
  g = np.ones((3,3))
  g[0,0] =   math.cos(phi1) * math.cos(phi2) - math.sin(phi1) * math.sin(phi2) * math.cos(PHI)
  g[0,1] =   math.sin(phi1) * math.cos(phi2) + math.cos(phi1) * math.sin(phi2) * math.cos(PHI)
  g[0,2] =   math.sin(phi2) * math.sin(PHI)
  g[1,0] = - math.cos(phi1) * math.sin(phi2) - math.sin(phi1) * math.cos(phi2) * math.cos(PHI)
  g[1,1] = - math.sin(phi1) * math.sin(phi2) + math.cos(phi1) * math.cos(phi2) * math.cos(PHI)
  g[1,2] =   math.cos(phi2) * math.sin(PHI)
  g[2,0] =   math.sin(phi1) * math.sin(PHI)
  g[2,1] =  -math.cos(phi1) * math.sin(PHI)
  g[2,2] =   math.cos(PHI)
  return g
#---------------------------- Calculation of Euler Angles ------------------------------------

def EulerAngles(g):
  PHI = math.degrees(math.acos(g[2,2]))
  if PHI == 0 :
    phi1_phi2 = math.degrees(math.acos(g[0,0]))
    list_phi1_phi2 = [phi1_phi2, 360 - phi1_phi2]
    for i in list_phi1_phi2 :
      if g[0,1]/math.sin(math.radians(i)) > 0 :
        phi1_phi2 = i
    return round(phi1_phi2,3),round(PHI,3),round(math.degrees(0.0),3)
    
  else:
    phi1 = math.degrees(math.acos(((- g[2,1])/math.sin(math.radians(PHI)))))
    list_phi1 = [phi1, 360 - phi1 ]
    for i in list_phi1 :
      if g[2,0]/math.sin(math.radians(i))*math.sin(math.radians(PHI)) > 0 :
        phi1 = i
    phi2 = math.degrees(math.acos((g[1,2]/math.sin(math.radians(PHI)))))
    list_phi2 = [phi2, 360 - phi2]
    for i in list_phi2 :
      if g[0,2]/math.sin(math.radians(i))*math.sin(math.radians(PHI)) > 0 :
        phi2 = i
    return round(phi1,3),round(PHI,3),round(phi2,3)
#---------------------------- inverse -----------------------------------------------------
def tetragonal(tensile_ax,phi1,PHI,phi2):
  axes = np.array(([tensile_ax,-1 * tensile_ax]))
  g = OrientationMatrix(math.radians(phi1),math.radians(PHI),math.radians(phi2))
  symm_operators = np.array(([[1,0,0],[0,1,0],[0,0,1]],
                             [[-1,0,0],[0,1,0],[0,0,-1]],
                             [[1,0,0],[0,-1,0],[0,0,-1]],
                             [[-1,0,0],[0,-1,0],[0,0,1]],
                             [[0,1,0],[-1,0,0],[0,0,1]],
                             [[0,-1,0],[1,0,0],[0,0,1]],
                             [[0,1,0],[1,0,0],[0,0,-1]],
                             [[0,-1,0],[-1,0,0],[0,0,-1]]
  ))
  for axis in axes:
    for i in xrange(8):
      G = np.dot(symm_operators[i],g)
      crystal_vector = np.dot(G,axis)
      if crystal_vector[0] >= 0 and crystal_vector[1] >= 0 and crystal_vector[2] >= 0:
        if crystal_vector[0] > crystal_vector[1] :
           return G,EulerAngles(G),crystal_vector

os.mkdir('unitcell_check')
os.chdir('unitcell_check')
texfile = open("Indent_unitcell_IPF.tex", 'w')
texfile.write(generate_tex('header'))
tensile_ax = np.array([0,0,1])

for i in xrange(5):

#   o = damask.Orientation(random=True, symmetry='tetragonal')
#   vector,sym_op = o.inversePole([0,0,1],SST=True)
#   q = o.equivalentQuaternions()[sym_op]
#   angles = np.array(q.asEulers(degrees=True))
#   vector = vector/np.linalg.norm(vector)
#   X = vector[0]/(1 + abs(vector[2]))
#   Y = vector[1]/(1 + abs(vector[2]))
#   zeta = 0.0 if vector[0] == 0. and vector[1] == 0. else math.degrees(math.atan2(vector[1],vector[0]))
#   eta  = math.degrees(math.acos(vector[2]))
#   o_convention = damask.Orientation(Eulers=np.radians(np.array([270. + zeta,eta,90.-zeta])))
#   angle_conv = np.array([270. + zeta,eta,90.-zeta])
#   angle_mis,axis = (o_convention.quaternion * q.conjugated()).asAngleAxis(degrees=True)
# #  print angle_mis,axis[2]
#   angle_mis = angle_mis * axis[2]
  o = damask.Orientation(random=True,symmetry='tetragonal')

  v,symOp = o.inversePole([0.,0.,1.])

  print "vector",v,symOp,"\n"
  X = v[0]/(1. + abs(v[2]))
  Y = v[1]/(1. + abs(v[2]))
  p = o.equivalentOrientations()[symOp]
  eta = np.arccos(abs(v[2]))
  zeta = np.arctan2(v[1],v[0])

  c = damask.Orientation(Eulers=np.array([1.5*np.pi+zeta,eta,0.5*np.pi-zeta]),symmetry='tetragonal')

  print "random",o.asEulers(degrees=True)
  print "convention",c.asEulers(degrees=True)
  angle,axis = (c.quaternion*p.quaternion.conjugated()).asAngleAxis(degrees=True)
  if axis[2] < 0.0:
    angle *= -1
  print "misorientation",(c.quaternion*p.quaternion.conjugated()).asAngleAxis(degrees=True)
  cmd = 'unitcell -n "cell_{}" -c 0.5456 --up 0 1 0 -r -e {} '.format(i,' '.join(map(str,o.asEulers())))
#  cmd1 = 'unitcell -n "cell_%i" -c 0.5456 -e %.02f %.02f %.02f '%((i+1),angle_conv[0],angle_conv[1],angle_conv[2])
  call(cmd,shell=True)
#  out = 'phi1%sPHI%sphi2%s.pdf'%(str(int(angles[0])),str(int(angles[1])),str(int(angles[2])))
#  out = "cell_{}.pdf".format(str(i))
  texfile.write('\\node at ({},{}) {{\includegraphics[angle = {},scale=0.2]{{cell_{}.pdf}}{{}}}};\n'.format(X,Y,angle,i,(i+1) ))
#  texfile.write('\\node at (%f,%f){\includegraphics[scale=0.2]{%s}};\n'%(X,Y,out1))
texfile.write(generate_tex('footer'))
texfile.close()



