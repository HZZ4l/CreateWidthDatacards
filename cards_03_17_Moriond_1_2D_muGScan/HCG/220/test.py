#!/usr/bin/env python
import re
from sys import argv, stdout, stderr, exit
from optparse import OptionParser
import numpy
from ROOT import *

col = numpy.array([kGreen,kYellow],dtype='i')
gStyle.SetPalette(2,col)
f = TFile.Open("higgsCombine2D_obs.MultiDimFit.mH220.root")
limit = f.Get("limit")
h = TH2F("h","h",50,0,30,50,0,3)
for i in range(limit.GetEntries()):
    limit.GetEvent(i)
    h.SetBinContent(h.FindBin(limit.CMS_zz4l_GGsm,limit.CMS_zz4l_mu),limit.deltaNLL)
c1= TCanvas()
levels = numpy.array([2.3,6])
h.SetContour(2,levels)
h.GetYaxis().SetTitle("#mu")
h.SetLineWidth(4)
h.GetXaxis().SetTitle("r=#Gamma/#Gamma_{SM}")
h.SetAxisRange(0,20,"X")
h.Draw("CONT1")

g= TGraph(1)
g.SetName("SM")
g.SetTitle("SM")
g.SetPoint(0,1,1)
g.SetMarkerStyle(33)
g.SetMarkerColor(kBlue)
g.SetMarkerSize(1.5)
g.Draw("PSAME")
leg=TLegend(0.1,0.45,0.45,0.8)
leg.AddEntry(g,"p")
c1.SaveAs("2Dscan.eps")
c1.SaveAs("2Dscan.pdf")
c1.SaveAs("2Dscan.png")
c1.SaveAs("2Dscan.gif")
c1.SaveAs("2Dscan.root")
c1.SaveAs("2Dscan.gif")
#c2= TCanvas("c2")
#h.ProjectionY().Draw()
    
        
