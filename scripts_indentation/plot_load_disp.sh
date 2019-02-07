#!/usr/bin/env bash


file="${1%%.*}"            #data file 
gri \
         -output ${file}_load_plot.ps \
         -p \
         $CMMHOME/Code/Gri/plot \
         line solid \
         symbol dot \
         nolabel \
         frame 5 \
         linear 'load' %g 0 1 5 2 1 \
         linear 'depth/nm' %g 0 600 3 4 1 \
#         linear 'time' %g 0 200 4 5 1  \
         ${file} 2 1
gri_ps2pdf ${file}_load_plot.ps
open ${file}_load_plot.pdf
