#!/bin/bash

First=$1

cd ${LS_SUBCWD}

echo "LSF job running in: " `pwd` with options $First

eval `scram runtime -sh`

combine -M ProfileLikelihood hzz4l_allS_8TeV.root -m 220 -n 2D_${First} -t 50 --expectSignal=1 -s $((12345+$First))