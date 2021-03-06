#!/bin/bash


python make_width2D_DCsandWSs.py -i SM_inputs_8TeV -a $1 -d 2 -b 

#cd test1D/HCG/240 or test2D/HCG/240
cd cards_"$1"/HCG/220
combineCards.py hzz4l_2e2muS_8TeV.txt hzz4l_4muS_8TeV.txt hzz4l_4eS_8TeV.txt > hzz4l_allS_8TeV.txt

#text2workspace.py -m 240 hzz4l_allS_8TeV.txt -P HiggsAnalysis.CombinedLimit.HiggsWidth:higgswidth -o hzz4l_allS_8TeV.root
text2workspace.py -m 220 hzz4l_allS_8TeV.txt -P HiggsAnalysis.CombinedLimit.HiggsWidth:higgswidth -o hzz4l_allS_8TeV.root --stat
#(add --stat if no systematics)
#(add -PO=GGsmVal=25 if you want to run with e.g. G/G_SM = 25 and not 1)

combine -M GenerateOnly hzz4l_allS_8TeV.root -m 220 -t -1 --expectSignal=1 --saveToys -V -v 7
root -b -l -q ../../../utils/addToyDataset.C\(\"hzz4l_allS_8TeV.root\",\"higgsCombineTest.GenerateOnly.mH220.123456.root\",\"toy_asimov\",\"workspaceWithAsimov.root\"\)
combine -M MultiDimFit workspaceWithAsimov.root --algo=grid --points 200 -m 220 -n 1D_exp -D toys/toy_asimov -v 3 -S 0 --fastScan
#(add "-S 0 --fastScan" if no systematics)
root ../../../utils/plotScan1D.C\(220,30\)
