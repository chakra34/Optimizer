#!/bin/bash
name=${1%.*}
echo ${name}
out="$2"
add_InterpolatedImage.py -l 1_nodeinitialcoord,2_nodeinitialcoord -d DisplacementZ --size 10.0 10.0 -p 10.0/255 ${name}.txt
imageData -d 256 256 -r -0.2 0.2 --color bluered -l 1_values --flipud out_${name}.txt
mv out_${name}_1_values.png ${out}.png
image_crop.py --rmin 10 --rmax 50 ${out}.png

