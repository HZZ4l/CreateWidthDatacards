#!/bin/bash

First=$1

cd ${LS_SUBCWD}

echo "LSF job running in: " `pwd` with options $First $Last

eval `scram runtime -sh`

combine -M MultiDimFit hzz4l_allS_8TeV.root --algo=grid --points 200 -m 220 -n 2D_${First} -t 1 --expectSignal=1 -s $((12345+$First))