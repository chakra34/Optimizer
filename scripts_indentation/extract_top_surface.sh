#!/bin/bash
file="$1"
inc="$2"
postResults -r $inc $inc 5 --increment --ns="Displacement Z","Reaction Force Z" -s --increment --filter 'z > -0.1' --separation x,y,z $file
