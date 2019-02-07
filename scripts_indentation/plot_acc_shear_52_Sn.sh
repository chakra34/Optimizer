#!/usr/bin/env bash

file="$1"
gri -output plot_$file.ps -p ~/Documents/Code/Gri/plot line solid symbol dot color own nolabel clip frame 5 linear 'increment ' %g 0 2550 5 2 1 log 'log (acc_shear)' %g 0.0006 0.1 2 5 1 \
$file 1 9 'rgb 0 0 1' $file 1 10 'rgb 0 0 1' \
$file 1 11 'rgb 0 0 0.5' $file 1 12 'rgb 0 0 0.5' \
$file 1 13 'rgb 0 0.5 0' $file 1 14 'rgb 0 0.5 0' \
$file 1 15 'rgb 0.5 0 0' $file 1 16 'rgb 0.5 0 0' $file 1 17 'rgb 0.5 0 0' $file 1 18 'rgb 0.5 0 0' \
$file 1 19 'rgb 0 0.5 0.5' $file 1 20 'rgb 0 0.5 0.5' \
$file 1 21 'rgb 0.5 0.5 0' $file 1 22 'rgb 0.5 0.5 0' $file 1 23 'rgb 0.5 0.5 0' $file 1 24 'rgb 0.5 0.5 0' \
$file 1 25 'rgb 0.5 0 0.5' $file 1 26 'rgb 0.5 0 0.5' \
$file 1 27 'rgb 0.5 0.5 0.5' $file 1 28 'rgb 0.5 0.5 0.5' \
$file 1 29 'rgb 1 0 0' $file 1 30 'rgb 1 0 0' $file 1 31 'rgb 1 0 0' $file 1 32 'rgb 1 0 0' \
$file 1 33 'rgb 0 1 0' $file 1 34 'rgb 0 1 0' $file 1 35 'rgb 0 1 0' $file 1 36 'rgb 0 1 0' $file 1 37 'rgb 0 1 0' $file 1 38 'rgb 0 1 0' $file 1 39 'rgb 0 1 0' $file 1 40 'rgb 0 1 0' \
$file 1 41 'rgb 1 0.5 0.5' $file 1 42 'rgb 1 0.5 0.5' $file 1 43 'rgb 1 0.5 0.5' $file 1 44 'rgb 1 0.5 0.5' \
$file 1 45 'rgb 1 0 0.5' $file 1 46 'rgb 1 0 0.5' $file 1 47 'rgb 1 0 0.5' $file 1 48 'rgb 1 0 0.5' $file 1 49 'rgb 1 0 0.5' $file 1 50 'rgb 1 0 0.5' $file 1 51 'rgb 1 0 0.5' $file 1 52 'rgb 1 0 0.5' \
$file 1 53 'rgb 1 1 0.5' $file 1 54 'rgb 1 1 0.5' $file 1 55 'rgb 1 1 0.5' $file 1 56 'rgb 1 1 0.5' $file 1 57 'rgb 1 1 0.5' $file 1 58 'rgb 1 1 0.5' $file 1 59 'rgb 1 1 0.5' $file 1 60 'rgb 1 1 0.5' 
gri_ps2pdf plot_$file.ps