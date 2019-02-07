#!/usr/bin/env bash

# function to check whether a specified field is already present 

label_present () {                                                                        # $1: ASCIItable, $2: column label, $3 expected count
#  echo checking labels `filterTable -w $2 < $1 | showTable --label | wc -w`
  [[ $((`filterTable -w $2 < $1 | showTable --label | wc -w`)) -eq $3 ]] && return 0 || return 1
}


# finds the directory from where the script is executed 

SOURCE="${BASH_SOURCE[0]}"
while [ -h "$SOURCE" ]; do # resolve $SOURCE until the file is no longer a symlink
  CODEDIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"
  SOURCE="$(readlink "$SOURCE")"
  [[ $SOURCE != /* ]] && SOURCE="$CODEDIR/$SOURCE" # if $SOURCE was a relative symlink, we need to resolve it relative to the path where the symlink file was located
done
CODEDIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"

FORCE=NO

while [[ $# > 1 ]]
do
key="$1"

case $key in
    -f|--force)
    FORCE=YES
    ;;
    -i|--indents)
    INDENTS="$2"
    shift # past argument
    ;;
    *)
            # unknown option
    ;;
esac
shift # past argument or value
done

patchname="$1"

[[ $FORCE == YES ]] && echo "using force..."

# AFM_done label
# map eulers to grain_IDs
# find topo min
# find conosphere location 
# add SST position
# add spherical eulers
# center AFM indent image
# circular crop of centered AFM image
# add maximum depth to load-displacement curve


cd $CODEDIR/../experiment/Sn/${patchname}


# adding blank indent indicator to the mother file 
if ! label_present ${patchname}_indentations.txt AFM_done 1; then
  echo 'adding AFM indicator...'
  filterTable -b AFM_done ${patchname}_indentations.txt
  addCalculation -l AFM_done -f '0' ${patchname}_indentations.txt

fi

# adding Euler angles to the mother file 
if ! label_present ${patchname}_indentations.txt eulerangles 3 || [ $FORCE == YES ]; then
  echo 'updating Euler angles...'
  filterTable -b eulerangles ${patchname}_indentations.txt
  addMapped -c grain_ID -l eulerangles -a ${patchname}_orientations.txt ${patchname}_indentations.txt

fi

# adding global and spherical_fit coordinates

if ! label_present ${patchname}_indentations.txt topography_minimum 3 || [ $FORCE == YES ]; then
  echo 'updating topography minima...'
  filterTable -b topography_minimum ${patchname}_indentations.txt
  addCalculation -l topography_minimum -f 'np.nan*np.ones(3)' ${patchname}_indentations.txt
  
fi

if ! label_present ${patchname}_indentations.txt spherical_fit 3 || [ $FORCE == YES ] ; then
  echo 'updating spherical fit...'
  filterTable -b spherical_fit ${patchname}_indentations.txt
  addCalculation -l spherical_fit -f 'np.nan*np.ones(3)' ${patchname}_indentations.txt


fi

indents_done=`filterTable -w "indent_ID" -c "#AFM_done# == 1" < ${patchname}_indentations.txt | showTable --data`

# adding SST projection

if ! label_present ${patchname}_indentations.txt 'SST(proper)' 2 || [ $FORCE == YES ]; then
  echo 'updating SST projection...'
  filterTable -b "SST(proper)" ${patchname}_indentations.txt
  $CODEDIR/add_SSTprojection.py -d -e eulerangles --proper -s tetragonal ${patchname}_indentations.txt

fi

#adding Spherical Orientations

if ! label_present ${patchname}_indentations.txt SphericalEulers 3 || [ $FORCE == YES ]; then
  echo 'updating spherical Eulers...'
  filterTable -b SphericalEulers ${patchname}_indentations.txt
  $CODEDIR/add_SphericalOrientations.py -d -e eulerangles -s tetragonal ${patchname}_indentations.txt

fi


if [[ ! -z $INDENTS ]]; then
  OLDIFS=$IFS
  IFS=','
  indents_done=( $INDENTS )
  IFS=$OLDIFS

fi

for i in ${indents_done[@]};
do
  i=${i%%.*}                                                            # converting floating point to integer
  gw_info=`$CODEDIR/gwyddion_info.py --pixelsize --shape AFM/processed/${i}/${patchname}${i}.000`
  array=( $gw_info )
  file="tip_${array[1]}.txt"
  [[ -e "$CODEDIR/../experiment/Sn/$patchname/$file" ]] || \
    $CODEDIR/spheroconical_tip.py -r 1.0e-6 --alpha 45 --float_pix ${array[0]} --dim 11 11 > $file                 ## helper script for finding the pixel size

# converting an AFM file to a geom file format for subsequent use

  $CODEDIR/geom_fromGwyddion.py AFM/processed/${i}/${patchname}${i}.000


# Adding information of global x,y,z and best spherical fit x,y,z

  answer=`$CODEDIR/out_TopographyMin_SphericalFit.py --tip $file --disp 3_displacement AFM/processed/${i}/${patchname}${i}.geom`
  array=( $answer )

  echo $answer

  globalX=${array[1]}
  globalY=${array[2]}
  globalZ=${array[3]}

  sphericalX=${array[5]}
  sphericalY=${array[6]}
  sphericalZ=${array[7]}


  fillTable -l topography_minimum,spherical_fit \
            -f "np.array([${globalX};${globalY};${globalZ}])","np.array([${sphericalX};${sphericalY};${sphericalZ}])" \
            -c "#indent_ID# == $i" \
            ${patchname}_indentations.txt

#  making the AFM (centered ) images by image data and cropping it

  centered=`$CODEDIR/centered_data.py --center ${sphericalX} ${sphericalY} AFM/processed/${i}/${patchname}${i}.geom `
  array=( $centered )

  grid_X=${array[1]}
  grid_Y=${array[2]}

  offset_x=${array[4]}
  offset_y=${array[5]}



# making centered images

  geom_canvas --float -g ${grid_X} ${grid_Y} 1 --fill 0.0 --offset ${offset_x} ${offset_y} 0  AFM/processed/${i}/${patchname}${i}.geom

  imageData -d ${grid_X} ${grid_Y} -r -100e-9 100e-9 --color bluered AFM/processed/${i}/${patchname}${i}.geom

  cropCenter_x=$(( grid_Y / 2 ))
  cropCenter_y=$(( grid_X / 2 ))
  $CODEDIR/image_crop.py --center ${cropCenter_x} ${cropCenter_y} --rmin 0 --rmax 50 AFM/processed/${i}/${patchname}${i}.png

done
