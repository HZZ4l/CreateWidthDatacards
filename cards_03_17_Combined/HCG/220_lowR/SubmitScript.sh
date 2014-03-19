#!/bin/bash

for itter in {0..99}
do
  bsub -q 1nd -o lsflog_${itter}.txt -e lsferr_${itter}.err -R "type=SLC5_64"  ParallelizeProfLike.lsf.sh $itter
#  bash ParallelizeProfLike68.lsf.sh $itter
done