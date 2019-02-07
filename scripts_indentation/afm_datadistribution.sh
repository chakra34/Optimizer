#!/bin/bash

theFile=$1

echo '4 head' \
| cat - $theFile \
| tr '\t' '\n' > ${theFile%.*}.distribution

gri -p -output ${theFile%.*}.ps \
 $HOME/Documents/Code/Gri/plot_distribution.gri \
 process 500 \
 nolabel \
 frame 5 \
 linear 'depth / micron' %g -1 1 2 5 1e6 \
 ${theFile%.*}.distribution 1

gri_ps2pdf ${theFile%.*}.ps
