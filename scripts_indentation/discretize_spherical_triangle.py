#!/usr/bin/env python

import os,sys,damask
import damask,string
from optparse import OptionParser
import numpy as np
from subprocess import call
import math


scriptID   = string.replace('$Id: discretize_spherical_triangle.py 185 2015-11-09 15:56:55Z chakra34 $','\n','\\n')
scriptName = os.path.splitext(scriptID.split()[1])[0]


parser = OptionParser(option_class=damask.extendableOption, usage='%prog options [file[s]]', description = """
Discretizes a spherical triangle equally based on depth.

""", version = scriptID)

parser.add_option('--depth',
                  dest = 'depth',
                  type = 'int',
                  help = 'recursion depth of discretization [%default]')

parser.add_option('--symm',
                  dest = 'symmetry',
                  type = 'string',
                  help = 'symmetry [cubic]')

parser.add_option("--unitcell",  action="store_true",
                  dest="unitcell",
                  help="unitcell or not [False]")

parser.add_option("--eulers",  action="store_true",
                  dest="eulers",
                  help="prints out the discretized Euler angles in Bunge convention [False]")

parser.add_option('--p1',
                  dest = 'point1',
                  type = 'float', nargs = 3, metavar = 'float float float',
                  help = 'first point in the spherical triangle to be discretized [%default]')

parser.add_option('--p2',
                  dest = 'point2',
                  type = 'float', nargs = 3, metavar = 'float float float',
                  help = 'second point in the spherical triangle to be discretized [%default]')

parser.add_option('--p3',
                  dest = 'point3',
                  type = 'float', nargs = 3, metavar = 'float float float',
                  help = 'third point in the spherical triangle to be discretized [%default]')

parser.set_defaults(depth       = 3,
                    symmetry    = 'cubic',
                    unitcell    = False,
                    eulers      = False,
                    point1      = [0., 0., 1.],
                    point2      = [1., 0., 0.],
                    point3      = [1., 1., 0.],
                   )

(options,filenames) = parser.parse_args()

options.point1 = np.array(options.point1)/np.linalg.norm(options.point1)
options.point2 = np.array(options.point2)/np.linalg.norm(options.point2)
options.point3 = np.array(options.point3)/np.linalg.norm(options.point3)

#----------------------------------------------#
def generate_tex_cubic(section):

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
                    '\\draw[line width=1.0pt] (0,0) -- (0.414,0);',
                    '\\draw[line width=1.0pt] (0,0) -- (0.0,0.414);',
                    '\\draw[line width=1.0pt, domain=0:15] plot ({-1 + sqrt(2)*cos(\\x)}, {sqrt(2)*sin(\\x)});',
                    '\\draw[line width=1.0pt, domain=75:90] plot ({ sqrt(2)*cos(\\x)}, {-1 + sqrt(2)*sin(\\x)});',
                    '\\draw[line width=1.0pt] (0,0) -- (0.366,0.366);',
                    '\\begin{scope}[inner sep=0pt]',
                    '\\node[fill,rectangle,minimum height=6pt,minimum width=6pt,label={below left:\\small\\hkl<001>}] at (0.000000,0.000000) {};',
                    '\\node[fill,diamond,minimum height=12pt,minimum width=6pt,label={below right:\\small\\hkl<101>}] at (0.414,0.000000) {};',
                    '\\node[fill,diamond,minimum height=12pt,minimum width=6pt,label={below right:\\small\\hkl<011>}] at (0.0,0.414) {};',
                    '\\node[fill,ellipse,minimum height=6pt,minimum width=6pt,label={above right:\\small\\hkl<111>}] at (0.366,0.366) {};',
                    '\\end{scope}\n',
                    '\\begin{scope}[inner sep=1.0pt]\n'])
  elif section == 'footer' :
   return'\n'.join(['\\end{scope}\n',
                    '\\end{scope}',
                    '\\end{tikzpicture}',
                    '\\end{document}'])

def generate_tex_tetragonal(section):
   
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
                      '\\draw[line width=1.0pt] (0,0) -- (0,1);',
                      '\\draw[line width=1.0pt] (0,0) -- (0.707,0.707);',
                      '\\begin{scope}[inner sep=0pt]',
                      '\\node[fill,rectangle,minimum height=6pt,minimum width=6pt,label={below left:\\small\\hkl<001>}] at (0.000000,0.000000) {};',
                      '\\node[fill,diamond,minimum height=12pt,minimum width=6pt,label={below right:\\small\\hkl<100>}] at (1.000000,0.000000) {};',
                      '\\node[fill,ellipse,minimum height=6pt,minimum width=6pt,label={above right:\\small\\hkl<110>}] at (0.707107,0.707107) {};',
                      '\\node[fill,diamond,minimum height=6pt,minimum width=6pt,label={above right:\\small\\hkl<010>}] at (0.0000,1.0000) {};',
                      '\\end{scope}\n',
                      '\\begin{scope}[inner sep=1.0pt]\n'])
   elif section == 'footer' :
     return'\n'.join(['\\end{scope}\n',
                      '\\end{scope}',
                      '\\end{tikzpicture}',
                      '\\end{document}'])

def generate_tex_hexagonal(section):
   
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
                      '\\draw[line width=1.0pt] (1,0) arc(0:60:1);',
#                      '\\draw[line width=1.0pt] (0,0) -- (0,1);',
                      '\\draw[line width=1.0pt] (0,0) -- (0.866,0.50);',
                      '\\draw[line width=1.0pt] (0,0) -- (0.5,0.8660);',
                      '\\begin{scope}[inner sep=0pt]',
                      '\\node[fill,rectangle,minimum height=6pt,minimum width=6pt,label={below left:\\small\\hkl<0001>}] at (0.000000,0.000000) {};',
                      '\\node[fill,diamond,minimum height=12pt,minimum width=6pt,label={below right:\\small\\hkl<2-1-10>}] at (1.000000,0.000000) {};',
                      '\\node[fill,ellipse,minimum height=6pt,minimum width=6pt,label={above right:\\small\\hkl<10-10>}] at (0.866,0.5) {};',
                      '\\node[fill,diamond,minimum height=6pt,minimum width=6pt,label={above right:\\small\\hkl<11-20>}] at (0.5,0.866) {};',
                      '\\end{scope}\n',
                      '\\begin{scope}[inner sep=1.0pt]\n'])
   elif section == 'footer' :
     return'\n'.join(['\\end{scope}\n',
                      '\\end{scope}',
                      '\\end{tikzpicture}',
                      '\\end{document}'])


#------------------------------------------------------#
def plot(vector):
  color = np.array(([255,0,0]))
  zeta = math.degrees(math.atan2(vector[1],vector[0]))
  eta  = math.degrees(math.acos(vector[2]))
  phi1 = 270 + zeta
  PHI  = eta
  phi2 = 90 - zeta
  if options.eulers == True:
    print phi1,PHI,phi2
  X = vector[0] /((1 + abs(vector[2])))                                                     # stereographic projection
  Y = vector[1] /((1 + abs(vector[2])))
  if options.unitcell == True :
    if options.symmetry == 'tetragonal' :
      cmd = 'unitcell -n "%s-%s-%s" -c 0.5456 --up 0 1 0 -e %.02f %.02f %.02f '%(str(int(phi1)),str(int(PHI)),str(int(phi2)),phi1,PHI,phi2)
    elif options.symmetry == 'cubic' :
      cmd = 'unitcell -n "%s-%s-%s" -c 1.0 --up 0 1 0 -e %.02f %.02f %.02f '%(str(int(phi1)),str(int(PHI)),str(int(phi2)),phi1,PHI,phi2)
    elif options.symmetry == 'hexagonal' :
      cmd = 'unitcell -u hexagonal -n "%s-%s-%s" --up 0 1 0 -e %.02f %.02f %.02f '%(str(int(phi1)),str(int(PHI)),str(int(phi2)),phi1,PHI,phi2)
#    call(cmd,shell=True)
    out = '%s-%s-%s.pdf'%(str(int(phi1)),str(int(PHI)),str(int(phi2)))
    texfile.write('\\node at (%.03f,%.03f){\includegraphics[scale=0.1]{%s}};\n'%(X,Y,out))
  else :
    texfile.write('\\node[fill={rgb:red,%.4f;green,%.4f;blue,%.4f}, circle, minimum height=4pt] at (%.4f, %.4f) {};\n'%(color[0]/255.0, color[1]/255.0, color[2]/255.0, X, Y))
  return


def mid(vector1,vector2):
  key = "{}+{}".format(vector1,vector2)
  dict = {}
  if key not in dict:
    dict[key] = 0.5*(vector1+vector2)
    dict[key] /= np.linalg.norm(dict[key])
    plot(dict[key])
    return dict[key]

def subdivide(triangles):
  subdivisions = []
  for triangle in enumerate(triangles):
    a = mid(triangle[0],triangle[1])
    b = mid(triangle[1],triangle[2])
    c = mid(triangle[2],triangle[0])
    subdivisions += [[triangle[0],a,c],[a,triangle[1],b],[b,triangle[2],c],[a,b,c]]
  return subdivisions

os.mkdir('equidistant')
os.chdir('equidistant')

texfile = open("equidistant_IPF.tex", 'w')
if options.symmetry == 'tetragonal':
  texfile.write(generate_tex_tetragonal('header'))
elif options.symmetry == 'cubic':
  texfile.write(generate_tex_cubic('header'))
elif options.symmetry == 'hexagonal':
  texfile.write(generate_tex_hexagonal('header'))

triangles = [[options.point1,options.point2,options.point3]]
plot(options.point1)
plot(options.point2)
plot(options.point3)
while options.depth > 0:
  triangles = subdivide(triangles)
  options.depth -= 1
texfile.write(generate_tex_tetragonal('footer'))
texfile.close()


