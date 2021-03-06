#! /usr/bin/env python
import sys
import os
import re
import math
from scipy.special import erf
from ROOT import *
import ROOT
from array import array
from systematicsClass import *
from inputReader import *
from HiggsAnalysis.CombinedLimit.SMHiggsBuilder import SMHiggsBuilder

## ------------------------------------
##  card and workspace class
## ------------------------------------

## ------------------------------------
##  ISSUES:
##
##  qqZZ templates should be normalized xbin by xbin, I'm using roberto's
##  Do I still need signal rate normalizations, now that I use Ulash templates? Removed, but will need to be put back if using shape region < template region
##
## ------------------------------------


class width_datacardClass:

    def __init__(self):
    
        self.ID_4mu = 1
        self.ID_4e  = 2
        self.ID_2e2mu = 3    
        self.isFSR = True
        self.dimensions = 2

    def setDimensions(self,dim):
        self.dimensions = dim
        
    def loadIncludes(self):
        
        ROOT.gSystem.AddIncludePath("-I$ROOFITSYS/include/")
        ROOT.gSystem.AddIncludePath("-Iinclude/")
        ROOT.gROOT.ProcessLine(".L include/tdrstyle.cc")
        ROOT.gSystem.Load("libRooFit")
        ROOT.gSystem.Load("libHiggsAnalysisCombinedLimit.so")
        ROOT.gSystem.Load("include/HiggsCSandWidth_cc.so")
        ROOT.gSystem.Load("include/HiggsCSandWidthSM4_cc.so")
 
    # return trueVar if testStatement else return falseVar
    def getVariable(self,trueVar,falseVar,testStatement):

        if (testStatement): 
            return trueVar
        else:
            return falseVar
    
    # main datacard and workspace function
    def makeCardsWorkspaces(self, theLowSide, theOutputDir, theInputs):

        ## --------------- SETTINGS AND DECLARATIONS --------------- ##
        DEBUG = False
        self.mH = 125.6   ## FIXED
        self.lumi =theInputs['lumi']#100.0
        self.inputlumi = theInputs['lumi']
        self.sqrts = theInputs['sqrts']
        self.channel = theInputs['decayChannel']
        self.outputDir = theOutputDir

        self.ggH_chan = theInputs['ggH']
        self.qqH_chan = theInputs['qqH']
        self.WH_chan = theInputs['WH']
        self.ZH_chan = theInputs['ZH']
        self.ttH_chan = theInputs['ttH']
        self.qqZZ_chan = theInputs['qqZZ']
        self.ggZZ_chan = theInputs['ggZZ']
        self.ggZZ_signal_chan = theInputs['ggZZ_signal']
        self.ggZZ_bkg_chan = theInputs['ggZZbkg']
        self.ggZZ_interf_chan = theInputs['ggZZ_interf']
        self.VBF_offshell_chan = theInputs['VBF_offshell']
        self.zjets_chan = theInputs['zjets']
        self.templRange =220
        
        ## ---------------- SET PLOTTING STYLE ---------------- ## 
        ROOT.setTDRStyle(True)
        ROOT.gStyle.SetPalette(1)
        ROOT.gStyle.SetPadLeftMargin(0.16)        

        ## ---------------- VARIABLES FOR LATER --------------- ##
        self.bUseCBnoConvolution = False
        ForXSxBR = False

        myCSW = HiggsCSandWidth()
        
        w = ROOT.RooWorkspace("w","w")
                
        ## ----------------- WIDTH AND RANGES ----------------- ##
        self.widthHVal =  myCSW.HiggsWidth(0,self.mH)
        if(self.widthHVal < 0.12):
            self.bUseCBnoConvolution = True
        self.isHighMass = False
        if self.mH >= 390:
            if theInputs['useHighMassReweightedShapes']:
                self.isHighMass = True
            else: print "useHighMassReweightedShapes set to FALSE, using non-reweighted shapes!"

            
        print "width: ",self.widthHVal
        
        self.low_M = theLowSide
        self.high_M = 1600
        
        if (self.channel == self.ID_4mu):
            self.appendName = '4mu'
            self.appendNameAlt = '4mu'
        elif (self.channel == self.ID_4e):
            self.appendName = '4e'
            self.appendNameAlt = '4e'
        elif (self.channel == self.ID_2e2mu):
            self.appendName = '2e2mu'
            self.appendNameAlt = '2mu2e'
        else: print "Input Error: Unknown channel! (4mu = 1, 4e = 2, 2e2mu = 3)"
            
            
        
        ## ------------------------- SYSTEMATICS CLASSES ----------------------------- ##
    
        systematics = systematicsClass( self.mH, False, self.isFSR, theInputs)
        systematics_forXSxBR = systematicsClass( self.mH, True, self.isFSR,theInputs)

        ## -------------------------- SIGNAL SHAPE ----------------------------------- ##
    
        bins = (self.high_M-self.templRange)/20 #5 for Roberto's
        bins2 = (self.high_M-self.low_M)/20
        # if(self.bUseCBnoConvolution): bins = 200

        CMS_zz4l_widthMass_name = "CMS_zz4l_widthMass"
            
        CMS_zz4l_widthMass = ROOT.RooRealVar(CMS_zz4l_widthMass_name,CMS_zz4l_widthMass_name,self.low_M,self.high_M)
        CMS_zz4l_widthMass.setBins(bins2)

        ## use this variable only For Integration (FI)
        CMS_zz4l_widthMass_name = "CMS_zz4l_widthMass_FI"
            
        CMS_zz4l_widthMass_FI = ROOT.RooRealVar(CMS_zz4l_widthMass_name,CMS_zz4l_widthMass_name,self.templRange,1600)    
        CMS_zz4l_widthMass_FI.setBins(bins)

        mu_name = "R"
        mu = ROOT.RooRealVar(mu_name,mu_name,1.0,0,4)
        mu.setVal(1)
        mu.setBins(100)
        mu_name = "kV"
        muV = ROOT.RooRealVar(mu_name,mu_name,1.0,0,8)
        muV.setVal(1)
        muV.setBins(100)
        mu_name = "kgluon"
        muF = ROOT.RooRealVar(mu_name,mu_name,1.0,0,4)
        muF.setVal(1)
        muF.setBins(100)


        #kV=ROOT.RooRealVar("kV","kV",0.0,0.0,1.0) 
        ktau=ROOT.RooRealVar("ktau","ktau",0.0,0.0,2.0)
        ktop=ROOT.RooRealVar("ktop","ktop",0.0,0.0,4.0)
        kbottom=ROOT.RooRealVar("kbottom","kbottom",0,0.0,3.0)
        #kgluon=ROOT.RooRealVar("kgluon","kgluon",0,0.0,2.0)
        kgamma=ROOT.RooRealVar("kgamma","kgamma",0,0.0,2.5)
        #BRInvUndet=ROOT.RooRealVar("BRInvUndet","BRInvUndet",0,0,1)

        #Should we put the explicit SM values? OR can we fix them in the Physics model?
        SM_BR_hzz=ROOT.RooRealVar("SM_BR_hzz","SM_BR_hzz",1,0.0,2.0) 
        SM_BR_hww=ROOT.RooRealVar("SM_BR_hww","SM_BR_hww",1,0.0,2.0)
        SM_BR_htt=ROOT.RooRealVar("SM_BR_htt","SM_BR_htt",1,0.0,2.0)
        SM_BR_hmm=ROOT.RooRealVar("SM_BR_hmm","SM_BR_hmm",1,0.0,2.0)
        SM_BR_htoptop=ROOT.RooRealVar("SM_BR_htoptop","SM_BR_htoptop",1,0.0,2.0)
        SM_BR_hcc=ROOT.RooRealVar("SM_BR_hcc","SM_BR_hcc",1,0.0,2.0)
        SM_BR_hbb=ROOT.RooRealVar("SM_BR_hbb","SM_BR_hbb",1,0.0,2.0)
        SM_BR_hss=ROOT.RooRealVar("SM_BR_hss","SM_BR_hss",1,0.0,2.0)
        SM_BR_hgluglu=ROOT.RooRealVar("SM_BR_hgluglu","SM_BR_hgluglu",1,0.0,2.0)
        SM_BR_hgg=ROOT.RooRealVar("SM_BR_hgg","SM_BR_hgg",1,0.0,2.0)
        SM_BR_hzg=ROOT.RooRealVar("SM_BR_hzg","SM_BR_hzg",1,0.0,2.0)
        #just to scale properly the Ks: 1 if we minimize on GGsm, 0 if we use Ks
        normScalerK =  ROOT.RooRealVar("CMS_zz4l_scalerK","CMS_zz4l_scalerK",1.0,0.0,2.0)
        #normScalerK.setVal(1)
        #normScalerK.setConstant(true)
        #CMS_zz4l_Gscal_Vectors=ROOT.RooFormulaVar("CMS_zz4l_Gscal_Vectors","@0*@0 * (@1+@2)*abs(1-@3)", ROOT.RooArgList(muV, SM_BR_hzz, SM_BR_hww,normScalerK))
        CMS_zz4l_Gscal_Vectors=ROOT.RooFormulaVar("CMS_zz4l_Gscal_Vectors","(@0+@1)*abs(1-@2)", ROOT.RooArgList(SM_BR_hzz, SM_BR_hww,normScalerK))
        CMS_zz4l_Gscal_tau=ROOT.RooFormulaVar("CMS_zz4l_Gscal_tau","@0*@0 * (@1+@2)*abs(1-@3)", ROOT.RooArgList(ktau, SM_BR_htt, SM_BR_hmm,normScalerK))
        CMS_zz4l_Gscal_top=ROOT.RooFormulaVar("CMS_zz4l_Gscal_top","@0*@0 * (@1+@2)*abs(1-@3)", ROOT.RooArgList(ktop, SM_BR_htoptop, SM_BR_hcc,normScalerK))
        CMS_zz4l_Gscal_bottom=ROOT.RooFormulaVar("CMS_zz4l_Gscal_bottom","@0*@0 * (@1+@2)*abs(1-@3)", ROOT.RooArgList(kbottom, SM_BR_hbb, SM_BR_hss,normScalerK))
        CMS_zz4l_Gscal_gluon=ROOT.RooFormulaVar("CMS_zz4l_Gscal_gluon","@0*@0 * @1*abs(1-@2)", ROOT.RooArgList(muF, SM_BR_hgluglu,normScalerK))
        CMS_zz4l_Gscal_gamma=ROOT.RooFormulaVar("CMS_zz4l_Gscal_gamma","@0*@0 * (@1+@2)*abs(1-@3)", ROOT.RooArgList(kgamma, SM_BR_hgg, SM_BR_hzg,normScalerK))

        listggsm = ROOT.RooArgList(CMS_zz4l_Gscal_Vectors, CMS_zz4l_Gscal_tau, CMS_zz4l_Gscal_top, CMS_zz4l_Gscal_bottom, CMS_zz4l_Gscal_gluon, CMS_zz4l_Gscal_gamma,normScalerK)
        #listggsm = ROOT.RooArgList(kV,ktau,ktop,kbottom,kgluon,kgamma,BRInvUndet)

        x_name = "CMS_zz4l_GGsm"

        x = ROOT.RooRealVar(x_name,x_name,0,50)
        x.setVal(1)
        x.setBins(100)

        Kframework = ROOT.RooFormulaVar("gammaK","@0+@1+@2+@3+@4+@5+@6",listggsm)

        mu_name = "CMS_widthH_kbkg"

        kbkg = ROOT.RooRealVar(mu_name,mu_name,0,2)
        kbkg.setVal(1.0)
        #if self.dimensions==0 : kbkg.setConstant(True)
        kbkg.setBins(100)

        D2name = "CMS_zz4l_widthKD"
        CMS_zz4l_widthKD = ROOT.RooRealVar(D2name,D2name,0.,1.)
        CMS_zz4l_widthKD.setBins(30)

        self.LUMI = ROOT.RooRealVar("LUMI_{0:.0f}".format(self.sqrts),"LUMI_{0:.0f}".format(self.sqrts),self.lumi)
        self.LUMI.setConstant(True)
    
        #self.MH = ROOT.RooRealVar("MH","MH",300.)   
        #self.MH.setConstant(True)
        
        print '2D signal shapes for Width'
        
        #Roberto's templates
        #templateSigName = "{0}/templ2D_{1}_{2:.0f}TeV_m4l.root".format(self.templateDir, self.appendName, self.sqrts)
        #sigTempFile = ROOT.TFile(templateSigName)
        #print templateSigName
        #tmpSig_T_1 = sigTempFile.Get("mZZ_bkg")
        #tmpSig_T_2 = sigTempFile.Get("mZZ_sig")
        #tmpSig_T_4 = sigTempFile.Get("mZZ_inter")
        #tmpBkg_T = sigTempFile.Get("mZZ_qq")
        #tmpBkg_T.RebinX(4)
        #rangeBkg_T =TH2F("amZZ_bkg","amZZ_bkg",tmpBkg_T.GetXaxis().GetNbins()-tmpBkg_T.GetXaxis().FindBin(self.templRange)+1,self.templRange,tmpBkg_T.GetXaxis().GetXmax(),tmpBkg_T.GetYaxis().GetNbins(),tmpBkg_T.GetYaxis().GetXmin(),tmpBkg_T.GetYaxis().GetXmax())
        #for ix in range(1,rangeBkg_T.GetXaxis().GetNbins()+1):
        #    for iy in range(1,rangeBkg_T.GetYaxis().GetNbins()+1):
        #        bincontent = tmpBkg_T.GetBinContent(tmpBkg_T.FindBin(rangeBkg_T.GetXaxis().GetBinCenter(ix),rangeBkg_T.GetYaxis().GetBinCenter(iy)))
        #        rangeBkg_T.SetBinContent(ix,iy,bincontent)
        
        #Ulascan templates
        templateSigName = "/afs/cern.ch/work/u/usarica/public/CombineTemplates/02_04_2014/{0:.0f}TeV/{1}/{2}/HtoZZ4l_MCFM_125p6_ModifiedSmoothTemplatesForCombine__GenLevelVBF_wResolution_D_Gamma_gg_r10_Nominal.root".format(self.sqrts,self.appendNameAlt,self.templRange)
        #templateSigName = "/afs/cern.ch/work/u/usarica/public/CombineTemplates/14_3_2014/{0:.0f}TeV/{1}/{2}/HtoZZ4l_MCFM_125p6_ModifiedSmoothTemplatesForCombine__GenLevelVBF_wResolution_D_Gamma_gg_r10_Nominal.root".format(self.sqrts,self.appendName,self.templRange)
        #templateSigName = "/afs/cern.ch/work/u/usarica/public/CombineTemplates/14_3_2014/{0:.0f}TeV/{1}/{2}/HtoZZ4l_MCFM_125p6_ModifiedTemplatesForCombine_Raw_D_Gamma_gg_r10_Nominal.root".format(self.sqrts,self.appendName,self.templRange)
        #templateSigName = "/afs/cern.ch/work/u/usarica/public/CombineTemplates/14_3_2014/{0:.0f}TeV/{1}/{2}/HtoZZ4l_MCFM_125p6_ModifiedSmoothTemplatesForCombine__GenLevelVBF_wResolution_D_Gamma_gg_r10_Nominal.root".format(self.sqrts,self.appendName,self.templRange)
        #templateSigName = "/afs/cern.ch/work/u/usarica/public/CombineTemplates/{0:.0f}TeV/{1}/{2}/HtoZZ4l_gg2VV_125p6_ModifiedTemplatesForCombine_D_Gamma_gg_r10_Nominal.root".format(self.sqrts,self.appendName,self.templRange)
        #templateSigName = "/afs/cern.ch/work/u/usarica/public/CombineTemplates/forGiacomo_OldTemplates/WidthTemplates/{0:.0f}TeV/{1}/{2}/HtoZZ4l_gg2VV_125p6_TemplatesForCombine_D_Gamma_gg_r10_Nominal.root".format(self.sqrts,self.appendName,self.templRange)
        sigTempFileU = ROOT.TFile(templateSigName)
        tmpSig_T_1 = sigTempFileU.Get("T_2D_2") #different numbering convention Ulascan-Roberto
        tmpSig_T_2 = sigTempFileU.Get("T_2D_1")
        tmpSig_T_4 = sigTempFileU.Get("T_2D_4")
        rangeBkg_T = sigTempFileU.Get("T_2D_qqZZ_UnConditional")
        tmpVBF_T_1 = sigTempFileU.Get("T_2D_VBF_2") #different numbering convention Ulascan-Roberto
        tmpVBF_T_2 = sigTempFileU.Get("T_2D_VBF_1")
        tmpVBF_T_4 = sigTempFileU.Get("T_2D_VBF_4")

        templateSigNameUp_PDF = "/afs/cern.ch/work/u/usarica/public/CombineTemplates/02_04_2014/{0:.0f}TeV/{1}/{2}/HtoZZ4l_MCFM_125p6_ModifiedSmoothTemplatesForCombine__GenLevelVBF_wResolution_D_Gamma_gg_r10_SysUp_ggPDF.root".format(self.sqrts,self.appendNameAlt,self.templRange)
        templateSigNameDown_PDF = "/afs/cern.ch/work/u/usarica/public/CombineTemplates/02_04_2014/{0:.0f}TeV/{1}/{2}/HtoZZ4l_MCFM_125p6_ModifiedSmoothTemplatesForCombine__GenLevelVBF_wResolution_D_Gamma_gg_r10_SysDown_ggPDF.root".format(self.sqrts,self.appendNameAlt,self.templRange)
        templateSigNameUp_QCD = "/afs/cern.ch/work/u/usarica/public/CombineTemplates/02_04_2014/{0:.0f}TeV/{1}/{2}/HtoZZ4l_MCFM_125p6_ModifiedSmoothTemplatesForCombine__GenLevelVBF_wResolution_D_Gamma_gg_r10_SysUp_ggQCD.root".format(self.sqrts,self.appendNameAlt,self.templRange)
        templateSigNameDown_QCD = "/afs/cern.ch/work/u/usarica/public/CombineTemplates/02_04_2014/{0:.0f}TeV/{1}/{2}/HtoZZ4l_MCFM_125p6_ModifiedSmoothTemplatesForCombine__GenLevelVBF_wResolution_D_Gamma_gg_r10_SysDown_ggQCD.root".format(self.sqrts,self.appendNameAlt,self.templRange)
        #templateSigNameUp = "/afs/cern.ch/work/u/usarica/public/CombineTemplates/14_3_2014/{0:.0f}TeV/{1}/{2}/HtoZZ4l_MCFM_125p6_ModifiedTemplatesForCombine_Raw_D_Gamma_gg_r10_SysUp.root".format(self.sqrts,self.appendName,self.templRange)
        #templateSigNameDown = "/afs/cern.ch/work/u/usarica/public/CombineTemplates/14_3_2014/{0:.0f}TeV/{1}/{2}/HtoZZ4l_MCFM_125p6_ModifiedTemplatesForCombine_Raw_D_Gamma_gg_r10_SysDown.root".format(self.sqrts,self.appendName,self.templRange)
        #templateSigNameUp = "/afs/cern.ch/work/u/usarica/public/CombineTemplates/14_3_2014/{0:.0f}TeV/{1}/{2}/HtoZZ4l_MCFM_125p6_ModifiedSmoothTemplatesForCombine__GenLevelVBF_wResolution_D_Gamma_gg_r10_SysUp.root".format(self.sqrts,self.appendName,self.templRange)
        #templateSigNameDown = "/afs/cern.ch/work/u/usarica/public/CombineTemplates/14_3_2014/{0:.0f}TeV/{1}/{2}/HtoZZ4l_MCFM_125p6_ModifiedSmoothTemplatesForCombine__GenLevelVBF_wResolution_D_Gamma_gg_r10_SysDown.root".format(self.sqrts,self.appendName,self.templRange)
        #templateSigNameUp = "/afs/cern.ch/work/u/usarica/public/CombineTemplates/{0:.0f}TeV/{1}/{2}/HtoZZ4l_gg2VV_125p6_ModifiedTemplatesForCombine_D_Gamma_gg_r10_SysUp.root".format(self.sqrts,self.appendName,self.templRange)
        #templateSigNameDown = "/afs/cern.ch/work/u/usarica/public/CombineTemplates/{0:.0f}TeV/{1}/{2}/HtoZZ4l_gg2VV_125p6_ModifiedTemplatesForCombine_D_Gamma_gg_r10_SysDown.root".format(self.sqrts,self.appendName,self.templRange)
        #templateSigNameUp = "/afs/cern.ch/work/u/usarica/public/CombineTemplates/forGiacomo_OldTemplates/WidthTemplates/{0:.0f}TeV/{1}/{2}/HtoZZ4l_gg2VV_125p6_TemplatesForCombine_D_Gamma_gg_r10_SysUp.root".format(self.sqrts,self.appendName,self.templRange)
        #templateSigNameDown = "/afs/cern.ch/work/u/usarica/public/CombineTemplates/forGiacomo_OldTemplates/WidthTemplates/{0:.0f}TeV/{1}/{2}/HtoZZ4l_gg2VV_125p6_TemplatesForCombine_D_Gamma_gg_r10_SysDown.root".format(self.sqrts,self.appendName,self.templRange)
        sigTempFileUp_PDF = ROOT.TFile(templateSigNameUp_PDF)
        sigTempFileDown_PDF = ROOT.TFile(templateSigNameDown_PDF)
        sigTempFileUp_QCD = ROOT.TFile(templateSigNameUp_QCD)
        sigTempFileDown_QCD = ROOT.TFile(templateSigNameDown_QCD)

        #Sig_T_1 = TH2F("amZZ_bkg","amZZ_bkg",tmpSig_T_1.GetXaxis().GetNbins()-tmpSig_T_1.GetXaxis().FindBin(self.templRange)+1,self.templRange,tmpSig_T_1.GetXaxis().GetXmax(),tmpSig_T_1.GetYaxis().GetNbins(),tmpSig_T_1.GetYaxis().GetXmin(),tmpSig_T_1.GetYaxis().GetXmax())
        #Sig_T_2 = TH2F("amZZ_sig","amZZ_sig",tmpSig_T_2.GetXaxis().GetNbins()-tmpSig_T_2.GetXaxis().FindBin(self.templRange)+1,self.templRange,tmpSig_T_2.GetXaxis().GetXmax(),tmpSig_T_2.GetYaxis().GetNbins(),tmpSig_T_2.GetYaxis().GetXmin(),tmpSig_T_2.GetYaxis().GetXmax())
        #Sig_T_4 = TH2F("amZZ_inter","amZZ_inter",tmpSig_T_4.GetXaxis().GetNbins()-tmpSig_T_4.GetXaxis().FindBin(self.templRange)+1,self.templRange,tmpSig_T_4.GetXaxis().GetXmax(),tmpSig_T_4.GetYaxis().GetNbins(),tmpSig_T_4.GetYaxis().GetXmin(),tmpSig_T_4.GetYaxis().GetXmax())
        #
        
#         #this part here is to adapt templates if they start from a range lower than self.templRange
##         if abs(tmpBkg_T.GetXaxis().GetBinLowEdge(1)-self.templRange<0.05):
##             listtmp = [tmpSig_T_1,tmpSig_T_2,tmpSig_T_4,tmpBkg_T]
##             listSig = [Sig_T_1, Sig_T_2, Sig_T_4, Bkg_T]
##             listSigUp = []
##             listSigDown = []

##             #print "BINWIDTHSY  ",tmpSig_T_4.GetYaxis().GetBinWidth(1),"   ",Sig_T_4.GetYaxis().GetBinWidth(1)
##             #print "BINSY  ",tmpSig_T_4.GetYaxis().GetNbins(),"   ",Sig_T_4.GetYaxis().GetNbins()
##             #print "BINWIDTHSX  ",tmpSig_T_4.GetXaxis().GetBinWidth(1),"   ",Sig_T_4.GetXaxis().GetBinWidth(1)
##             #print "BINSX  ",tmpSig_T_4.GetXaxis().GetNbins(),"   ",Sig_T_4.GetXaxis().GetNbins()
            
##             for j in range(len(listSig)):
##                 #listSigUp.append(listSig[j].Clone("hist_{0}_Up".format(j)))
##                 #listSigDown.append(listSig[j].Clone("hist_{0}_Down".format(j)))
##                 if j == 3 :
##                     for ix in range(1,listSig[j].GetXaxis().GetNbins()+1):
##                         for iy in range(1,listSig[j].GetYaxis().GetNbins()+1):
##                             bincontent = listtmp[j].GetBinContent(listtmp[j].FindBin(listSig[j].GetXaxis().GetBinCenter(ix),listSig[j].GetYaxis().GetBinCenter(iy)))
##                             listSig[j].SetBinContent(ix,iy,bincontent)
##         else :
        Sig_T_1 = tmpSig_T_1.Clone("mZZ_bkg")
        Sig_T_2 = tmpSig_T_2.Clone("mZZ_sig")
        Sig_T_4 = tmpSig_T_4.Clone("mZZ_inter")
        VBF_T_1 = tmpVBF_T_1.Clone("mZZ_vbfbkg")
        VBF_T_2 = tmpVBF_T_2.Clone("mZZ_vbfsig")
        VBF_T_4 = tmpVBF_T_4.Clone("mZZ_vbfinter")
        Bkg_T = rangeBkg_T.Clone("mZZ_bkg")
        Bkg_ZX = sigTempFileU.Get("T_2D_ZX_UnConditional").Clone("Bkg_ZX_Nominal")
        Sig_T_1_Up_PDF = sigTempFileUp_PDF.Get("T_2D_2").Clone("T_2D_2_Up")
        Sig_T_2_Up_PDF = sigTempFileUp_PDF.Get("T_2D_1").Clone("T_2D_1_Up")
        Sig_T_4_Up_PDF = sigTempFileUp_PDF.Get("T_2D_4").Clone("T_2D_4_Up")
        Sig_T_1_Up_QCD = sigTempFileUp_QCD.Get("T_2D_2").Clone("T_2D_2_Up")
        Sig_T_2_Up_QCD = sigTempFileUp_QCD.Get("T_2D_1").Clone("T_2D_1_Up")
        Sig_T_4_Up_QCD = sigTempFileUp_QCD.Get("T_2D_4").Clone("T_2D_4_Up")
        VBF_T_1_Up = sigTempFileUp_PDF.Get("T_2D_VBF_2").Clone("T_2D_VBF_2_Up")
        VBF_T_2_Up = sigTempFileUp_PDF.Get("T_2D_VBF_1").Clone("T_2D_VBF_1_Up")
        VBF_T_4_Up = sigTempFileUp_PDF.Get("T_2D_VBF_4").Clone("T_2D_VBF_4_Up")
        #Bkg_T_Up = sigTempFileUp_PDF.Get("T_2D_qqZZ").Clone("T_2D_qqZZ_Up")
        Bkg_ZX_Up = sigTempFileDown_PDF.Get("T_2D_ZX_UnConditional").Clone("Bkg_ZX_Down")
        Sig_T_1_Down_PDF = sigTempFileDown_PDF.Get("T_2D_2").Clone("T_2D_2_Down")
        Sig_T_2_Down_PDF = sigTempFileDown_PDF.Get("T_2D_1").Clone("T_2D_1_Down")
        Sig_T_4_Down_PDF = sigTempFileDown_PDF.Get("T_2D_4").Clone("T_2D_4_Down")
        Sig_T_1_Down_QCD = sigTempFileDown_QCD.Get("T_2D_2").Clone("T_2D_2_Down")
        Sig_T_2_Down_QCD = sigTempFileDown_QCD.Get("T_2D_1").Clone("T_2D_1_Down")
        Sig_T_4_Down_QCD = sigTempFileDown_QCD.Get("T_2D_4").Clone("T_2D_4_Down")
        VBF_T_1_Down = sigTempFileDown_PDF.Get("T_2D_VBF_2").Clone("T_2D_VBF_2_Down")
        VBF_T_2_Down = sigTempFileDown_PDF.Get("T_2D_VBF_1").Clone("T_2D_VBF_1_Down")
        VBF_T_4_Down = sigTempFileDown_PDF.Get("T_2D_VBF_4").Clone("T_2D_VBF_4_Down")
        #Bkg_T_Down = sigTempFileDown_PDF.Get("T_2D_qqZZ").Clone("T_2D_qqZZ_Down")
        Bkg_ZX_Down = sigTempFileDown_PDF.Get("T_2D_ZX_UnConditional").Clone("Bkg_ZX_Down")

        #rates
        totalRateDown = Sig_T_1_Down_QCD.Integral("width")+Sig_T_2_Down_QCD.Integral("width")+Sig_T_4_Down_QCD.Integral("width")
        totalRateUp = Sig_T_1_Up_QCD.Integral("width")+Sig_T_2_Up_QCD.Integral("width")+Sig_T_4_Up_QCD.Integral("width")
        totalRateDown_pdf = Sig_T_1_Down_PDF.Integral("width")+Sig_T_2_Down_PDF.Integral("width")+Sig_T_4_Down_PDF.Integral("width")
        totalRateUp_pdf = Sig_T_1_Up_PDF.Integral("width")+Sig_T_2_Up_PDF.Integral("width")+Sig_T_4_Up_PDF.Integral("width")
        totalRate_ggzz = Sig_T_1.Integral("width")+Sig_T_2.Integral("width")+Sig_T_4.Integral("width")
        totalRate_ggzz = totalRate_ggzz #* 2.3
        totalRateDown = totalRateDown #*2.3
        totalRateUp  = totalRateUp #*2.3
        totalRateDown_pdf = totalRateDown_pdf #*2.3
        totalRateUp_pdf  = totalRateUp_pdf #*2.3
        rate_signal_ggzz_Shape = Sig_T_2.Integral("width")*self.lumi #*2.3
        rate_bkg_ggzz_Shape = Sig_T_1.Integral("width")*self.lumi #*2.3
        rate_interf_ggzz_Shape = Sig_T_4.Integral("width")*self.lumi #*2.3


	ggZZVarNormQCDUp_Name = "ggZZVarQCDUpNorm_{0:.0f}_{1:.0f}".format(self.channel,self.sqrts)
        sigRateQCDUpName = "signal_ggZZQCDUprate_{0:.0f}_{1:.0f}".format(self.channel,self.sqrts)
        bkgRateQCDUpName = "bkg_ggZZQCDUprate_{0:.0f}_{1:.0f}".format(self.channel,self.sqrts)
        interfRateQCDUpName = "interf_ggZZQCDUprate_{0:.0f}_{1:.0f}".format(self.channel,self.sqrts)
        sigRates_QCDUp = ROOT.RooRealVar(sigRateQCDUpName ,sigRateQCDUpName ,0.0,10000.0)
        bkgRates_QCDUp = ROOT.RooRealVar(bkgRateQCDUpName ,bkgRateQCDUpName ,0.0,10000.0)
        interfRates_QCDUp = ROOT.RooRealVar(interfRateQCDUpName,interfRateQCDUpName,0.0,10000.0)
	sigRates_QCDUp.setVal(Sig_T_2_Up_QCD.Integral("width"))
	sigRates_QCDUp.setConstant(true)
	bkgRates_QCDUp.setVal(Sig_T_1_Up_QCD.Integral("width"))
	bkgRates_QCDUp.setConstant(true)
	interfRates_QCDUp.setVal(Sig_T_4_Up_QCD.Integral("width"))
	interfRates_QCDUp.setConstant(true)
        ggZZQCDUp_norm = ROOT.RooFormulaVar(ggZZVarNormQCDUp_Name,"(@0*@3*@7*@6*@4+@1*sqrt(@3*@7*@6*@4)*sign(@5)*sqrt(abs(@5))+@2*@5)",ROOT.RooArgList(sigRates_QCDUp,interfRates_QCDUp,bkgRates_QCDUp,x,mu,kbkg,muF,Kframework))
	ggZZVarNormQCDDown_Name = "ggZZVarQCDDownNorm_{0:.0f}_{1:.0f}".format(self.channel,self.sqrts)
        sigRateQCDDownName = "signal_ggZZQCDDownrate_{0:.0f}_{1:.0f}".format(self.channel,self.sqrts)
        bkgRateQCDDownName = "bkg_ggZZQCDDownrate_{0:.0f}_{1:.0f}".format(self.channel,self.sqrts)
        interfRateQCDDownName = "interf_ggZZQCDDownrate_{0:.0f}_{1:.0f}".format(self.channel,self.sqrts)
        sigRates_QCDDown = ROOT.RooRealVar(sigRateQCDDownName ,sigRateQCDDownName ,0.0,10000.0)
        bkgRates_QCDDown = ROOT.RooRealVar(bkgRateQCDDownName ,bkgRateQCDDownName ,0.0,10000.0)
        interfRates_QCDDown = ROOT.RooRealVar(interfRateQCDDownName,interfRateQCDDownName,0.0,10000.0)
	sigRates_QCDDown.setVal(Sig_T_2_Down_QCD.Integral("width"))
	sigRates_QCDDown.setConstant(true)
	bkgRates_QCDDown.setVal(Sig_T_1_Down_QCD.Integral("width"))
	bkgRates_QCDDown.setConstant(true)
	interfRates_QCDDown.setVal(Sig_T_4_Down_QCD.Integral("width"))
	interfRates_QCDDown.setConstant(true)
        ggZZQCDDown_norm = ROOT.RooFormulaVar(ggZZVarNormQCDDown_Name,"(@0*@3*@7*@6*@4+@1*sqrt(@3*@7*@6*@4)*sign(@5)*sqrt(abs(@5))+@2*@5)",ROOT.RooArgList(sigRates_QCDDown,interfRates_QCDDown,bkgRates_QCDDown,x,mu,kbkg,muF,Kframework))

	ggZZVarNormPDFUp_Name = "ggZZVarPDFUpNorm_{0:.0f}_{1:.0f}".format(self.channel,self.sqrts)
        sigRatePDFUpName = "signal_ggZZPDFUprate_{0:.0f}_{1:.0f}".format(self.channel,self.sqrts)
        bkgRatePDFUpName = "bkg_ggZZPDFUprate_{0:.0f}_{1:.0f}".format(self.channel,self.sqrts)
        interfRatePDFUpName = "interf_ggZZPDFUprate_{0:.0f}_{1:.0f}".format(self.channel,self.sqrts)
        sigRates_PDFUp = ROOT.RooRealVar(sigRatePDFUpName ,sigRatePDFUpName ,0.0,10000.0)
        bkgRates_PDFUp = ROOT.RooRealVar(bkgRatePDFUpName ,bkgRatePDFUpName ,0.0,10000.0)
        interfRates_PDFUp = ROOT.RooRealVar(interfRatePDFUpName,interfRatePDFUpName,0.0,10000.0)
	sigRates_PDFUp.setVal(Sig_T_2_Up_PDF.Integral("width"))
	sigRates_PDFUp.setConstant(true)
	bkgRates_PDFUp.setVal(Sig_T_1_Up_PDF.Integral("width"))
	bkgRates_PDFUp.setConstant(true)
	interfRates_PDFUp.setVal(Sig_T_4_Up_PDF.Integral("width"))
	interfRates_PDFUp.setConstant(true)
        ggZZPDFUp_norm = ROOT.RooFormulaVar(ggZZVarNormPDFUp_Name,"(@0*@3*@7*@6*@4+@1*sqrt(@3*@7*@6*@4)*sign(@5)*sqrt(abs(@5))+@2*@5)",ROOT.RooArgList(sigRates_PDFUp,interfRates_PDFUp,bkgRates_PDFUp,x,mu,kbkg,muF,Kframework))
	ggZZVarNormPDFDown_Name = "ggZZVarPDFDownNorm_{0:.0f}_{1:.0f}".format(self.channel,self.sqrts)
        sigRatePDFDownName = "signal_ggZZPDFDownrate_{0:.0f}_{1:.0f}".format(self.channel,self.sqrts)
        bkgRatePDFDownName = "bkg_ggZZPDFDownrate_{0:.0f}_{1:.0f}".format(self.channel,self.sqrts)
        interfRatePDFDownName = "interf_ggZZPDFDownrate_{0:.0f}_{1:.0f}".format(self.channel,self.sqrts)
        sigRates_PDFDown = ROOT.RooRealVar(sigRatePDFDownName ,sigRatePDFDownName ,0.0,10000.0)
        bkgRates_PDFDown = ROOT.RooRealVar(bkgRatePDFDownName ,bkgRatePDFDownName ,0.0,10000.0)
        interfRates_PDFDown = ROOT.RooRealVar(interfRatePDFDownName,interfRatePDFDownName,0.0,10000.0)
	sigRates_PDFDown.setVal(Sig_T_2_Down_PDF.Integral("width"))
	sigRates_PDFDown.setConstant(true)
	bkgRates_PDFDown.setVal(Sig_T_1_Down_PDF.Integral("width"))
	bkgRates_PDFDown.setConstant(true)
	interfRates_PDFDown.setVal(Sig_T_4_Down_PDF.Integral("width"))
	interfRates_PDFDown.setConstant(true)
        ggZZPDFDown_norm = ROOT.RooFormulaVar(ggZZVarNormPDFDown_Name,"(@0*@3*@7*@6*@4+@1*sqrt(@3*@7*@6*@4)*sign(@5)*sqrt(abs(@5))+@2*@5)",ROOT.RooArgList(sigRates_PDFDown,interfRates_PDFDown,bkgRates_PDFDown,x,mu,kbkg,muF,Kframework))

	ggZZVarNorm_Name = "ggZZVarNominalNorm_{0:.0f}_{1:.0f}".format(self.channel,self.sqrts)
        sigRateNominalName = "signal_ggZZNominalrate_{0:.0f}_{1:.0f}".format(self.channel,self.sqrts)
        bkgRateNominalName = "bkg_ggZZNominalrate_{0:.0f}_{1:.0f}".format(self.channel,self.sqrts)
        interfRateNominalName = "interf_ggZZNominalrate_{0:.0f}_{1:.0f}".format(self.channel,self.sqrts)
        sigRates_Nominal = ROOT.RooRealVar(sigRateNominalName ,sigRateNominalName ,0.0,10000.0)
        bkgRates_Nominal = ROOT.RooRealVar(bkgRateNominalName ,bkgRateNominalName ,0.0,10000.0)
        interfRates_Nominal = ROOT.RooRealVar(interfRateNominalName,interfRateNominalName,0.0,10000.0)
	sigRates_Nominal.setVal(Sig_T_2.Integral("width"))
	sigRates_Nominal.setConstant(true)
	bkgRates_Nominal.setVal(Sig_T_1.Integral("width"))
	bkgRates_Nominal.setConstant(true)
	interfRates_Nominal.setVal(Sig_T_4.Integral("width"))
	interfRates_Nominal.setConstant(true)
        ggZZNominal_norm = ROOT.RooFormulaVar(ggZZVarNorm_Name,"(@0*@3*@7*@6*@4+@1*sqrt(@3*@7*@6*@4)*sign(@5)*sqrt(abs(@5))+@2*@5)",ROOT.RooArgList(sigRates_Nominal,interfRates_Nominal,bkgRates_Nominal,x,mu,kbkg,muF,Kframework))
	

        #Assume BKG and INTERF are from templates
        totalRateVBFDown = VBF_T_1_Down.Integral("width")+VBF_T_2_Down.Integral("width")+VBF_T_4_Down.Integral("width")
        totalRateVBFUp = VBF_T_1_Up.Integral("width")+VBF_T_2_Up.Integral("width")+VBF_T_4_Up.Integral("width")
        totalRate_vbf = VBF_T_1.Integral("width")+VBF_T_2.Integral("width")+VBF_T_4.Integral("width")
        totalRate_vbf_Shape = totalRate_vbf*self.lumi
        rate_signal_vbf_Shape = VBF_T_2.Integral("width")*self.lumi
        rate_bkg_vbf_Shape = VBF_T_1.Integral("width")*self.lumi
        rate_interf_vbf_Shape = VBF_T_4.Integral("width")*self.lumi

	VBFVarNormUp_Name = "VBFVarUpNorm_{0:.0f}_{1:.0f}".format(self.channel,self.sqrts)
        VBFsigRateUpName = "signal_VBFUprate_{0:.0f}_{1:.0f}".format(self.channel,self.sqrts)
        VBFbkgRateUpName = "bkg_VBFUprate_{0:.0f}_{1:.0f}".format(self.channel,self.sqrts)
        VBFinterfRateUpName = "interf_VBFUprate_{0:.0f}_{1:.0f}".format(self.channel,self.sqrts)
        VBFsigRates_Up = ROOT.RooRealVar(VBFsigRateUpName ,VBFsigRateUpName ,0.0,10000.0)
        VBFbkgRates_Up = ROOT.RooRealVar(VBFbkgRateUpName ,VBFbkgRateUpName ,0.0,10000.0)
        VBFinterfRates_Up = ROOT.RooRealVar(VBFinterfRateUpName,VBFinterfRateUpName,0.0,10000.0)
	VBFsigRates_Up.setVal(VBF_T_2_Up.Integral("width"))
	VBFsigRates_Up.setConstant(true)
	VBFbkgRates_Up.setVal(VBF_T_1_Up.Integral("width"))
	VBFbkgRates_Up.setConstant(true)
	VBFinterfRates_Up.setVal(VBF_T_4_Up.Integral("width"))
	VBFinterfRates_Up.setConstant(true)
        VBFUp_norm = ROOT.RooFormulaVar(VBFVarNormUp_Name,"(@0*@3*@6*@5*@4+@1*sqrt(@3*@6*@5*@4)+@2)",ROOT.RooArgList(VBFsigRates_Up,VBFinterfRates_Up,VBFbkgRates_Up,x,mu,muV,Kframework))
	VBFVarNormDown_Name = "VBFVarDownNorm_{0:.0f}_{1:.0f}".format(self.channel,self.sqrts)
        VBFsigRateDownName = "signal_VBFDownrate_{0:.0f}_{1:.0f}".format(self.channel,self.sqrts)
        VBFbkgRateDownName = "bkg_VBFDownrate_{0:.0f}_{1:.0f}".format(self.channel,self.sqrts)
        VBFinterfRateDownName = "interf_VBFDownrate_{0:.0f}_{1:.0f}".format(self.channel,self.sqrts)
        VBFsigRates_Down = ROOT.RooRealVar(VBFsigRateDownName ,VBFsigRateDownName ,0.0,10000.0)
        VBFbkgRates_Down = ROOT.RooRealVar(VBFbkgRateDownName ,VBFbkgRateDownName ,0.0,10000.0)
        VBFinterfRates_Down = ROOT.RooRealVar(VBFinterfRateDownName,VBFinterfRateDownName,0.0,10000.0)
	VBFsigRates_Down.setVal(VBF_T_2_Down.Integral("width"))
	VBFsigRates_Down.setConstant(true)
	VBFbkgRates_Down.setVal(VBF_T_1_Down.Integral("width"))
	VBFbkgRates_Down.setConstant(true)
	VBFinterfRates_Down.setVal(VBF_T_4_Down.Integral("width"))
	VBFinterfRates_Down.setConstant(true)
        VBFDown_norm = ROOT.RooFormulaVar(VBFVarNormDown_Name,"(@0*@3*@6*@5*@4+@1*sqrt(@3*@6*@5*@4)+@2)",ROOT.RooArgList(VBFsigRates_Down,VBFinterfRates_Down,VBFbkgRates_Down,x,mu,muV,Kframework))

	VBFVarNormNominal_Name = "VBFVarNominalNorm_{0:.0f}_{1:.0f}".format(self.channel,self.sqrts)
        VBFsigRateNominalName = "signal_VBFNominalrate_{0:.0f}_{1:.0f}".format(self.channel,self.sqrts)
        VBFbkgRateNominalName = "bkg_VBFNominalrate_{0:.0f}_{1:.0f}".format(self.channel,self.sqrts)
        VBFinterfRateNominalName = "interf_VBFNominalrate_{0:.0f}_{1:.0f}".format(self.channel,self.sqrts)
        VBFsigRates_Nominal = ROOT.RooRealVar(VBFsigRateNominalName ,VBFsigRateNominalName ,0.0,10000.0)
        VBFbkgRates_Nominal = ROOT.RooRealVar(VBFbkgRateNominalName ,VBFbkgRateNominalName ,0.0,10000.0)
        VBFinterfRates_Nominal = ROOT.RooRealVar(VBFinterfRateNominalName,VBFinterfRateNominalName,0.0,10000.0)
	VBFsigRates_Nominal.setVal(VBF_T_2.Integral("width"))
	VBFsigRates_Nominal.setConstant(true)
	VBFbkgRates_Nominal.setVal(VBF_T_1.Integral("width"))
	VBFbkgRates_Nominal.setConstant(true)
	VBFinterfRates_Nominal.setVal(VBF_T_4.Integral("width"))
	VBFinterfRates_Nominal.setConstant(true)
        VBFNominal_norm = ROOT.RooFormulaVar(VBFVarNormNominal_Name,"(@0*@3*@6*@5*@4+@1*sqrt(@3*@6*@5*@4)+@2)",ROOT.RooArgList(VBFsigRates_Nominal,VBFinterfRates_Nominal,VBFbkgRates_Nominal,x,mu,muV,Kframework))



        ## rates per lumi for scaling
        bkgRate_qqzz = theInputs['qqZZ_rate']/theInputs['qqZZ_lumi'] #*1.8
        #totalRate_ggzz = theInputs['ggZZ_rate']/theInputs['qqZZ_lumi']
        bkgRate_zjets = theInputs['zjets_rate']/theInputs['zjets_lumi']

        #totalRate_ggzz = Sig_T_1.Integral("width")+Sig_T_2.Integral("width")-Sig_T_4.Integral("width")
        totalRate_ggzz_Shape = totalRate_ggzz*self.lumi
        bkgRate_qqzz_Shape = bkgRate_qqzz*self.lumi
        bkgRate_zjets_Shape = bkgRate_zjets*self.lumi

        
        if Sig_T_4.Integral()<0 : #negative interference, turn it positive, the sign will be taken into account later when building the pdf
            for ix in range (1,Sig_T_4.GetXaxis().GetNbins()+1):
                for iy in range (1,tmpSig_T_4.GetYaxis().GetNbins()+1):
                    Sig_T_4.SetBinContent(ix,iy,-1.0*Sig_T_4.GetBinContent(ix,iy))
                    Sig_T_4_Down_PDF.SetBinContent(ix,iy,-1.0*Sig_T_4_Down_PDF.GetBinContent(ix,iy))
                    Sig_T_4_Up_PDF.SetBinContent(ix,iy,-1.0*Sig_T_4_Up_PDF.GetBinContent(ix,iy))
                    Sig_T_4_Down_QCD.SetBinContent(ix,iy,-1.0*Sig_T_4_Down_QCD.GetBinContent(ix,iy))
                    Sig_T_4_Up_QCD.SetBinContent(ix,iy,-1.0*Sig_T_4_Up_QCD.GetBinContent(ix,iy))
            rate_interf_ggzz_Shape = Sig_T_4.Integral("width")*self.lumi
        
        if VBF_T_4.Integral()<0 : #negative interference, turn it positive, the sign will be taken into account later when building the pdf
            for ix in range (1,VBF_T_4.GetXaxis().GetNbins()+1):
                for iy in range (1,tmpVBF_T_4.GetYaxis().GetNbins()+1):
                    VBF_T_4.SetBinContent(ix,iy,-1.0*VBF_T_4.GetBinContent(ix,iy))
                    VBF_T_4_Down.SetBinContent(ix,iy,-1.0*VBF_T_4_Down.GetBinContent(ix,iy))
                    VBF_T_4_Up.SetBinContent(ix,iy,-1.0*VBF_T_4_Up.GetBinContent(ix,iy))

            #Assume BKG and INTERF are from templates
            rate_interf_vbf_Shape = VBF_T_4.Integral("width")*self.lumi
            
        #protection against empty bins
        for ix in range(1,Bkg_T.GetXaxis().GetNbins()+1):
            for iy in range(1,Bkg_T.GetYaxis().GetNbins()+1):
                if Bkg_T.GetBinContent(ix,iy) == 0 : Bkg_T.SetBinContent(ix,iy,0.000001)
                if Sig_T_1.GetBinContent(ix,iy) == 0 : Sig_T_1.SetBinContent(ix,iy,0.000001)
                if Sig_T_2.GetBinContent(ix,iy) == 0 : Sig_T_2.SetBinContent(ix,iy,0.000001)
                if Sig_T_4.GetBinContent(ix,iy) == 0 : Sig_T_4.SetBinContent(ix,iy,0.000001)
                if Sig_T_1_Up_QCD.GetBinContent(ix,iy) == 0 : Sig_T_1_Up_QCD.SetBinContent(ix,iy,0.000001)
                if Sig_T_2_Up_QCD.GetBinContent(ix,iy) == 0 : Sig_T_2_Up_QCD.SetBinContent(ix,iy,0.000001)
                if Sig_T_4_Up_QCD.GetBinContent(ix,iy) == 0 : Sig_T_4_Up_QCD.SetBinContent(ix,iy,0.000001)
                if Sig_T_1_Down_QCD.GetBinContent(ix,iy) == 0 : Sig_T_1_Down_QCD.SetBinContent(ix,iy,0.000001)
                if Sig_T_2_Down_QCD.GetBinContent(ix,iy) == 0 : Sig_T_2_Down_QCD.SetBinContent(ix,iy,0.000001)
                if Sig_T_4_Down_QCD.GetBinContent(ix,iy) == 0 : Sig_T_4_Down_QCD.SetBinContent(ix,iy,0.000001)
                if Sig_T_1_Up_PDF.GetBinContent(ix,iy) == 0 : Sig_T_1_Up_PDF.SetBinContent(ix,iy,0.000001)
                if Sig_T_2_Up_PDF.GetBinContent(ix,iy) == 0 : Sig_T_2_Up_PDF.SetBinContent(ix,iy,0.000001)
                if Sig_T_4_Up_PDF.GetBinContent(ix,iy) == 0 : Sig_T_4_Up_PDF.SetBinContent(ix,iy,0.000001)
                if Sig_T_1_Down_PDF.GetBinContent(ix,iy) == 0 : Sig_T_1_Down_PDF.SetBinContent(ix,iy,0.000001)
                if Sig_T_2_Down_PDF.GetBinContent(ix,iy) == 0 : Sig_T_2_Down_PDF.SetBinContent(ix,iy,0.000001)
                if Sig_T_4_Down_PDF.GetBinContent(ix,iy) == 0 : Sig_T_4_Down_PDF.SetBinContent(ix,iy,0.000001)                                 
                if Bkg_ZX.GetBinContent(ix,iy) == 0 : Bkg_ZX.SetBinContent(ix,iy,0.000001)                                
                if Bkg_ZX_Up.GetBinContent(ix,iy) == 0 : Bkg_ZX_Up.SetBinContent(ix,iy,0.000001)                                
                if Bkg_ZX_Down.GetBinContent(ix,iy) == 0 : Bkg_ZX_Down.SetBinContent(ix,iy,0.000001)


        #normalization on background and protection against negative fluctuations
        for ix in range(1,Bkg_T.GetXaxis().GetNbins()+1):
            yNorm = Bkg_T.Integral(ix,ix,1,Bkg_T.GetYaxis().GetNbins())
            yNorm_zx = Bkg_ZX.Integral(ix,ix,1,Bkg_ZX.GetYaxis().GetNbins())
            yNorm_zx_Up = Bkg_ZX_Up.Integral(ix,ix,1,Bkg_ZX.GetYaxis().GetNbins())
            yNorm_zx_Down = Bkg_ZX_Down.Integral(ix,ix,1,Bkg_ZX.GetYaxis().GetNbins())
            #print yNorm
            if yNorm == 0: yNorm = 1.0
            if yNorm_zx == 0: yNorm = 1.0
            if yNorm_zx_Up == 0: yNorm_Up = 1.0
            if yNorm_zx_Down == 0: yNorm_Down = 1.0
            #if yNormUp == 0: yNormUp = 0.000000001
            #if yNormDown == 0: yNormDown = 0.000000001
            for iy in range(1,Bkg_T.GetYaxis().GetNbins()+1):
                Bkg_T.SetBinContent(ix,iy,Bkg_T.GetBinContent(ix,iy)/yNorm)
                if Bkg_T.GetBinContent(ix,iy) == 0: Bkg_T.SetBinContent(ix,iy,0.000001)
                Bkg_ZX.SetBinContent(ix,iy,Bkg_ZX.GetBinContent(ix,iy)/yNorm_zx)
                if Bkg_ZX.GetBinContent(ix,iy) == 0: Bkg_ZX.SetBinContent(ix,iy,0.000001)
                Bkg_ZX_Up.SetBinContent(ix,iy,Bkg_ZX_Up.GetBinContent(ix,iy)/yNorm_zx_Up)
                if Bkg_ZX_Up.GetBinContent(ix,iy) == 0: Bkg_ZX_Up.SetBinContent(ix,iy,0.000001)
                Bkg_ZX_Down.SetBinContent(ix,iy,Bkg_ZX_Down.GetBinContent(ix,iy)/yNorm_zx_Down)
                if Bkg_ZX_Down.GetBinContent(ix,iy) == 0: Bkg_ZX_Down.SetBinContent(ix,iy,0.000001)
                binI = Sig_T_4.GetBinContent(ix,iy)
                if binI > 0 : #check signs, should be < 0 for the template but I changed the sign above (secondo me >0)
                    binS = Sig_T_2.GetBinContent(ix,iy)
                    binB = Sig_T_1.GetBinContent(ix,iy)
                    if binI*binI >= 4*binS*binB:
                        Sig_T_4.SetBinContent(ix,iy,sqrt(abs(4*binS*binB))-0.00001)#check signs (secondo me 4 -0.0)
                        
                binI = VBF_T_4.GetBinContent(ix,iy)
                if binI > 0 : #check signs, should be < 0 for the template but I changed the sign above (secondo me >0)
                    binS = VBF_T_2.GetBinContent(ix,iy)
                    binB = VBF_T_1.GetBinContent(ix,iy)                
                    if binI*binI >= 4*binS*binB:
                        VBF_T_4.SetBinContent(ix,iy,sqrt(abs(4*binS*binB))-0.00001)#check signs (secondo me 4 -0.0)
                        
                binI = Sig_T_4_Up_QCD.GetBinContent(ix,iy)
                if binI > 0 : #check signs, should be < 0 for the template but I changed the sign above (secondo me >0)
                    binS = Sig_T_2_Up_QCD.GetBinContent(ix,iy)
                    binB = Sig_T_1_Up_QCD.GetBinContent(ix,iy)
                    if binI*binI >= 4*binS*binB:
                        Sig_T_4_Up_QCD.SetBinContent(ix,iy,sqrt(abs(4*binS*binB))-0.00001)#check signs (secondo me 4 -0.0)

                binI = Sig_T_4_Up_PDF.GetBinContent(ix,iy)
                if binI > 0 : #check signs, should be < 0 for the template but I changed the sign above (secondo me >0)
                    binS = Sig_T_2_Up_PDF.GetBinContent(ix,iy)
                    binB = Sig_T_1_Up_PDF.GetBinContent(ix,iy)
                    if binI*binI >= 4*binS*binB:
                        Sig_T_4_Up_PDF.SetBinContent(ix,iy,sqrt(abs(4*binS*binB))-0.00001)#check signs (secondo me 4 -0.0)

                binI = VBF_T_4_Up.GetBinContent(ix,iy)
                if binI > 0 : #check signs, should be < 0 for the template but I changed the sign above (secondo me >0)
                    binS = VBF_T_2_Up.GetBinContent(ix,iy)
                    binB = VBF_T_1_Up.GetBinContent(ix,iy)
                    if binI*binI >= 4*binS*binB:
                        VBF_T_4_Up.SetBinContent(ix,iy,sqrt(abs(4*binS*binB))-0.00001)#check signs (secondo me 4 -0.0)
                        
                binI = Sig_T_4_Down_QCD.GetBinContent(ix,iy)
                if binI > 0 : #check signs, should be < 0 for the template but I changed the sign above (secondo me >0)
                    binS = Sig_T_2_Down_QCD.GetBinContent(ix,iy)
                    binB = Sig_T_1_Down_QCD.GetBinContent(ix,iy)
                    if binI*binI >= 4*binS*binB:
                        Sig_T_4_Down_QCD.SetBinContent(ix,iy,sqrt(abs(4*binS*binB))-0.00001)#check signs (secondo me 4 -0.0)

                binI = Sig_T_4_Down_PDF.GetBinContent(ix,iy)
                if binI > 0 : #check signs, should be < 0 for the template but I changed the sign above (secondo me >0)
                    binS = Sig_T_2_Down_PDF.GetBinContent(ix,iy)
                    binB = Sig_T_1_Down_PDF.GetBinContent(ix,iy)
                    if binI*binI >= 4*binS*binB:
                        Sig_T_4_Down_PDF.SetBinContent(ix,iy,sqrt(abs(4*binS*binB))-0.00001)#check signs (secondo me 4 -0.0)

                binI = VBF_T_4_Down.GetBinContent(ix,iy)
                if binI > 0 : #check signs, should be < 0 for the template but I changed the sign above (secondo me >0)
                    binS = VBF_T_2_Down.GetBinContent(ix,iy)
                    binB = VBF_T_1_Down.GetBinContent(ix,iy)
                    if binI*binI >= 4*binS*binB:
                        VBF_T_4_Down.SetBinContent(ix,iy,sqrt(abs(4*binS*binB))-0.00001)#check signs (secondo me 4 -0.0)
                
                #Bkg_T_Up.SetBinContent(ix,iy,Bkg_T_Up.GetBinContent(ix,iy)/yNormUp)
                #Bkg_T_Down.SetBinContent(ix,iy,Bkg_T_Down.GetBinContent(ix,iy)/yNormDown)

        Proj_T_1 = Sig_T_1.ProjectionX("Proj_T_1")
        Proj_T_2 = Sig_T_2.ProjectionX("Proj_T_2")
        Proj_T_4 = Sig_T_4.ProjectionX("Proj_T_4")
 
        dBinsX = Sig_T_1.GetXaxis().GetNbins()
        print "X bins: ",dBinsX
        
        dBinsY = Sig_T_1.GetYaxis().GetNbins()
        print "Y bins: ",dBinsY
        #dLowY = Sig_T_1.GetYaxis().GetXmin()
        #dHighY = Sig_T_1.GetYaxis().GetXmax()
        
        CMS_zz4l_widthMass.setBins(dBinsX)
        ## CMS_zz4l_widthMass_FI.setBins(dBinsX)

        one = ROOT.RooRealVar("one","one",1.0)
        one.setConstant(True)

        ## -------------------------- gg2ZZ SHAPES ---------------------------------- ##
        
        sigRateName = "signal_ggZZrate_{0:.0f}_{1:.0f}".format(self.channel,self.sqrts)
        sigRates = ROOT.RooRealVar(sigRateName,sigRateName,0.0,10000.0)
        bkgRateName = "bkg_ggZZrate_{0:.0f}_{1:.0f}".format(self.channel,self.sqrts)
        bkgRates = ROOT.RooRealVar(bkgRateName,bkgRateName,0.0,10000.0)
        interfRateName = "interf_ggZZrate_{0:.0f}_{1:.0f}".format(self.channel,self.sqrts)
        interfRates = ROOT.RooRealVar(interfRateName,interfRateName,0.0,10000.0)
        
        sigRateNameNorm = "signalNorm_ggZZrate_{0:.0f}_{1:.0f}".format(self.channel,self.sqrts)
        sigRatesNorm = ROOT.RooFormulaVar(sigRateNameNorm,"@0*@4*@1*@3/(@0*@4*@1*@3-sqrt(@0*@4*@1*@3)*sign(@2)*sqrt(abs(@2))+@2)",ROOT.RooArgList(x,mu,kbkg,muF,Kframework)) 
        interfRateNameNorm = "interfNorm_ggZZrate_{0:.0f}_{1:.0f}".format(self.channel,self.sqrts)
        interfRatesNorm = ROOT.RooFormulaVar(interfRateNameNorm,"-sqrt(@0*@4*@1*@3)*sign(@2)*sqrt(abs(@2))/(@0*@4*@1*@3-sqrt(@0*@4*@1*@3)*sign(@2)*sqrt(abs(@2))+@2)",ROOT.RooArgList(x,mu,kbkg,muF,Kframework))
        bkgRateNameNorm = "bkgNorm_ggZZrate_{0:.0f}_{1:.0f}".format(self.channel,self.sqrts)
        bkgRatesNorm = ROOT.RooFormulaVar(bkgRateNameNorm,"@2/(@0*@4*@1*@3-sqrt(@0*@4*@1*@3)*sign(@2)*sqrt(abs(@2))+@2)",ROOT.RooArgList(x,mu,kbkg,muF,Kframework))

        #ggZZpdfName = "ggZZ_RooWidth_{0:.0f}_{1:.0f}".format(self.channel,self.sqrts)
        #ggZZpdf = ROOT.HZZ4lWidth(ggZZpdfName,ggZZpdfName,CMS_zz4l_widthMass,one,x,bkgRates,sigRates,interfRates,Sig_T_1,Sig_T_2,Sig_T_4)
        
        TemplateName = "ggZZsignal_TempDataHist_{0:.0f}_{1:.0f}".format(self.channel,self.sqrts)
        PdfName = "ggZZsignal_TemplatePdf_{0:.0f}_{1:.0f}".format(self.channel,self.sqrts)
        if self.dimensions > 1 :
            ggZZsignal_TempDataHist = ROOT.RooDataHist(TemplateName,TemplateName,ROOT.RooArgList(CMS_zz4l_widthMass,CMS_zz4l_widthKD),Sig_T_2) #nel rooarglist: ,CMS_zz4l_widthKD
            ggZZsignal_TemplatePdf = ROOT.RooHistFunc(PdfName,PdfName,ROOT.RooArgSet(CMS_zz4l_widthMass,CMS_zz4l_widthKD),ggZZsignal_TempDataHist)
        elif self.dimensions ==1  :
            ggZZsignal_TempDataHist = ROOT.RooDataHist(TemplateName,TemplateName,ROOT.RooArgList(CMS_zz4l_widthMass),Sig_T_2.ProjectionX()) #nel rooarglist: ,CMS_zz4l_widthKD
            ggZZsignal_TemplatePdf = ROOT.RooHistFunc(PdfName,PdfName,ROOT.RooArgSet(CMS_zz4l_widthMass),ggZZsignal_TempDataHist)
        elif self.dimensions == 0 :
            ggZZsignal_TempDataHist = ROOT.RooDataHist(TemplateName,TemplateName,ROOT.RooArgList(CMS_zz4l_widthKD),Sig_T_2.ProjectionY()) #nel rooarglist: ,CMS_zz4l_widthKD
            ggZZsignal_TemplatePdf = ROOT.RooHistFunc(PdfName,PdfName,ROOT.RooArgSet(CMS_zz4l_widthKD),ggZZsignal_TempDataHist)


        TemplateName = "ggZZbkg_TempDataHist_{0:.0f}_{1:.0f}".format(self.channel,self.sqrts)
        PdfName = "ggZZbkg_TemplatePdf_{0:.0f}_{1:.0f}".format(self.channel,self.sqrts)
        if self.dimensions > 1 :
            ggZZbkg_TempDataHist = ROOT.RooDataHist(TemplateName,TemplateName,ROOT.RooArgList(CMS_zz4l_widthMass,CMS_zz4l_widthKD),Sig_T_1)
            ggZZbkg_TemplatePdf = ROOT.RooHistFunc(PdfName,PdfName,ROOT.RooArgSet(CMS_zz4l_widthMass,CMS_zz4l_widthKD),ggZZbkg_TempDataHist)
        elif self.dimensions ==1  :
            ggZZbkg_TempDataHist = ROOT.RooDataHist(TemplateName,TemplateName,ROOT.RooArgList(CMS_zz4l_widthMass),Sig_T_1.ProjectionX())
            ggZZbkg_TemplatePdf = ROOT.RooHistFunc(PdfName,PdfName,ROOT.RooArgSet(CMS_zz4l_widthMass),ggZZbkg_TempDataHist)
        elif self.dimensions ==0  :            
            ggZZbkg_TempDataHist = ROOT.RooDataHist(TemplateName,TemplateName,ROOT.RooArgList(CMS_zz4l_widthKD),Sig_T_1.ProjectionY())
            ggZZbkg_TemplatePdf = ROOT.RooHistFunc(PdfName,PdfName,ROOT.RooArgSet(CMS_zz4l_widthKD),ggZZbkg_TempDataHist)
            
        TemplateName = "ggZZinterf_TempDataHist_{0:.0f}_{1:.0f}".format(self.channel,self.sqrts)
        PdfName = "ggZZinterf_TemplatePdf_{0:.0f}_{1:.0f}".format(self.channel,self.sqrts)
        if self.dimensions > 1 :
            ggZZinterf_TempDataHist = ROOT.RooDataHist(TemplateName,TemplateName,ROOT.RooArgList(CMS_zz4l_widthMass,CMS_zz4l_widthKD),Sig_T_4)
            ggZZinterf_TemplatePdf = ROOT.RooHistFunc(PdfName,PdfName,ROOT.RooArgSet(CMS_zz4l_widthMass,CMS_zz4l_widthKD),ggZZinterf_TempDataHist)
        elif self.dimensions ==1  :
            ggZZinterf_TempDataHist = ROOT.RooDataHist(TemplateName,TemplateName,ROOT.RooArgList(CMS_zz4l_widthMass),Sig_T_4.ProjectionX())
            ggZZinterf_TemplatePdf = ROOT.RooHistFunc(PdfName,PdfName,ROOT.RooArgSet(CMS_zz4l_widthMass),ggZZinterf_TempDataHist)
        elif self.dimensions ==0  :
            ggZZinterf_TempDataHist = ROOT.RooDataHist(TemplateName,TemplateName,ROOT.RooArgList(CMS_zz4l_widthKD),Sig_T_4.ProjectionY())
            ggZZinterf_TemplatePdf = ROOT.RooHistFunc(PdfName,PdfName,ROOT.RooArgSet(CMS_zz4l_widthKD),ggZZinterf_TempDataHist)
            
        ggZZpdfName = "ggZZ_RooWidth_Nominal_{0:.0f}_{1:.0f}".format(self.channel,self.sqrts)
        #ggZZpdf_Nominal = ROOT.RooRealSumPdf(ggZZpdfName,ggZZpdfName,ROOT.RooArgList(ggZZsignal_TemplatePdf,ggZZinterf_TemplatePdf,ggZZbkg_TemplatePdf),ROOT.RooArgList(sigRatesNorm,interfRatesNorm,bkgRatesNorm))
        ggZZpdf_Nominal = ROOT.RooRealSumPdf(ggZZpdfName,ggZZpdfName,ROOT.RooArgList(ggZZsignal_TemplatePdf,ggZZinterf_TemplatePdf,ggZZbkg_TemplatePdf),ROOT.RooArgList(sigRatesNorm,interfRatesNorm,bkgRatesNorm))

        ## for integration
##         TemplateName = "ggZZsignal_TempDataHist_{0:.0f}_{1:.0f}_FI".format(self.channel,self.sqrts)
##         PdfName = "ggZZsignal_TemplatePdf_{0:.0f}_{1:.0f}_FI".format(self.channel,self.sqrts)
        
##         ggZZsignal_TempDataHist_FI = ROOT.RooDataHist(TemplateName,TemplateName,ROOT.RooArgList(CMS_zz4l_widthMass_FI),Proj_T_2)
##         ggZZsignal_TemplatePdf_FI = ROOT.RooHistFunc(PdfName,PdfName,ROOT.RooArgSet(CMS_zz4l_widthMass_FI),ggZZsignal_TempDataHist_FI)
##       ##   PDFName = "ggZZsignal_TemplatePDF_{0:.0f}_{1:.0f}_FI".format(self.channel,self.sqrts)
##       ##   ggZZsignal_TemplatePDF_FI = ROOT.RooHistPdf(PDFName,PDFName,ROOT.RooArgSet(CMS_zz4l_widthMass_FI),ggZZsignal_TempDataHist_FI)

##         TemplateName = "ggZZbkg_TempDataHist_{0:.0f}_{1:.0f}_FI".format(self.channel,self.sqrts)
##         PdfName = "ggZZbkg_TemplatePdf_{0:.0f}_{1:.0f}_FI".format(self.channel,self.sqrts)
##         ggZZbkg_TempDataHist_FI = ROOT.RooDataHist(TemplateName,TemplateName,ROOT.RooArgList(CMS_zz4l_widthMass_FI),Proj_T_1)
##         ggZZbkg_TemplatePdf_FI = ROOT.RooHistFunc(PdfName,PdfName,ROOT.RooArgSet(CMS_zz4l_widthMass_FI),ggZZbkg_TempDataHist_FI)
        
##         TemplateName = "ggZZinterf_TempDataHist_{0:.0f}_{1:.0f}_FI".format(self.channel,self.sqrts)
##         PdfName = "ggZZinterf_TemplatePdf_{0:.0f}_{1:.0f}_FI".format(self.channel,self.sqrts)
##         ggZZinterf_TempDataHist_FI = ROOT.RooDataHist(TemplateName,TemplateName,ROOT.RooArgList(CMS_zz4l_widthMass_FI),Proj_T_4)
##         ggZZinterf_TemplatePdf_FI = ROOT.RooHistFunc(PdfName,PdfName,ROOT.RooArgSet(CMS_zz4l_widthMass_FI),ggZZinterf_TempDataHist_FI)

##         ggZZpdfName = "ggZZ_RooWidth_FI_{0:.0f}_{1:.0f}".format(self.channel,self.sqrts)
##         ggZZpdf_FI = ROOT.RooRealSumPdf(ggZZpdfName,ggZZpdfName,ROOT.RooArgList(ggZZsignal_TemplatePdf_FI,ggZZinterf_TemplatePdf_FI,ggZZbkg_TemplatePdf_FI),ROOT.RooArgList(sigRatesNorm,interfRatesNorm,bkgRatesNorm))

        ## -------------------------- SHAPE Systematic ---------------------------------- ##

        #Up Systematics pdf
        TemplateName = "ggZZsignal_TempDataHist_Up_{0:.0f}_{1:.0f}".format(self.channel,self.sqrts)
        PdfName = "ggZZsignal_TemplatePdf_Up_{0:.0f}_{1:.0f}".format(self.channel,self.sqrts)
        if self.dimensions > 1 :
            ggZZsignal_TempDataHist_Up = ROOT.RooDataHist(TemplateName,TemplateName,ROOT.RooArgList(CMS_zz4l_widthMass,CMS_zz4l_widthKD),Sig_T_2_Up_QCD)
            ggZZsignal_TemplatePdf_Up = ROOT.RooHistFunc(PdfName,PdfName,ROOT.RooArgSet(CMS_zz4l_widthMass,CMS_zz4l_widthKD),ggZZsignal_TempDataHist_Up)
        elif self.dimensions ==1  :
            ggZZsignal_TempDataHist_Up = ROOT.RooDataHist(TemplateName,TemplateName,ROOT.RooArgList(CMS_zz4l_widthMass),Sig_T_2_Up_QCD.ProjectionX())
            ggZZsignal_TemplatePdf_Up = ROOT.RooHistFunc(PdfName,PdfName,ROOT.RooArgSet(CMS_zz4l_widthMass),ggZZsignal_TempDataHist_Up)
        elif self.dimensions ==0 :
            ggZZsignal_TempDataHist_Up = ROOT.RooDataHist(TemplateName,TemplateName,ROOT.RooArgList(CMS_zz4l_widthKD),Sig_T_2_Up_QCD.ProjectionY())
            ggZZsignal_TemplatePdf_Up = ROOT.RooHistFunc(PdfName,PdfName,ROOT.RooArgSet(CMS_zz4l_widthKD),ggZZsignal_TempDataHist_Up)
            
        TemplateName = "ggZZbkg_TempDataHist_Up_{0:.0f}_{1:.0f}".format(self.channel,self.sqrts)
        PdfName = "ggZZbkg_TemplatePdf_Up_{0:.0f}_{1:.0f}".format(self.channel,self.sqrts)
        if self.dimensions > 1 :
            ggZZbkg_TempDataHist_Up = ROOT.RooDataHist(TemplateName,TemplateName,ROOT.RooArgList(CMS_zz4l_widthMass,CMS_zz4l_widthKD),Sig_T_1_Up_QCD)
            ggZZbkg_TemplatePdf_Up = ROOT.RooHistFunc(PdfName,PdfName,ROOT.RooArgSet(CMS_zz4l_widthMass,CMS_zz4l_widthKD),ggZZbkg_TempDataHist_Up)
        elif self.dimensions ==1  :
            ggZZbkg_TempDataHist_Up = ROOT.RooDataHist(TemplateName,TemplateName,ROOT.RooArgList(CMS_zz4l_widthMass),Sig_T_1_Up_QCD.ProjectionX())
            ggZZbkg_TemplatePdf_Up = ROOT.RooHistFunc(PdfName,PdfName,ROOT.RooArgSet(CMS_zz4l_widthMass),ggZZbkg_TempDataHist_Up)
        elif self.dimensions ==0  :
            ggZZbkg_TempDataHist_Up = ROOT.RooDataHist(TemplateName,TemplateName,ROOT.RooArgList(CMS_zz4l_widthKD),Sig_T_1_Up_QCD.ProjectionY())
            ggZZbkg_TemplatePdf_Up = ROOT.RooHistFunc(PdfName,PdfName,ROOT.RooArgSet(CMS_zz4l_widthKD),ggZZbkg_TempDataHist_Up)
        
        TemplateName = "ggZZinterf_TempDataHist_Up_{0:.0f}_{1:.0f}".format(self.channel,self.sqrts)
        PdfName = "ggZZinterf_TemplatePdf_Up_{0:.0f}_{1:.0f}".format(self.channel,self.sqrts)
        if self.dimensions > 1 :   
            ggZZinterf_TempDataHist_Up = ROOT.RooDataHist(TemplateName,TemplateName,ROOT.RooArgList(CMS_zz4l_widthMass,CMS_zz4l_widthKD),Sig_T_4_Up_QCD)
            ggZZinterf_TemplatePdf_Up = ROOT.RooHistFunc(PdfName,PdfName,ROOT.RooArgSet(CMS_zz4l_widthMass,CMS_zz4l_widthKD),ggZZinterf_TempDataHist_Up)
        if self.dimensions == 1 :   
            ggZZinterf_TempDataHist_Up = ROOT.RooDataHist(TemplateName,TemplateName,ROOT.RooArgList(CMS_zz4l_widthMass),Sig_T_4_Up_QCD.ProjectionX())
            ggZZinterf_TemplatePdf_Up = ROOT.RooHistFunc(PdfName,PdfName,ROOT.RooArgSet(CMS_zz4l_widthMass),ggZZinterf_TempDataHist_Up)            
        if self.dimensions == 0 :   
            ggZZinterf_TempDataHist_Up = ROOT.RooDataHist(TemplateName,TemplateName,ROOT.RooArgList(CMS_zz4l_widthKD),Sig_T_4_Up_QCD.ProjectionY())
            ggZZinterf_TemplatePdf_Up = ROOT.RooHistFunc(PdfName,PdfName,ROOT.RooArgSet(CMS_zz4l_widthKD),ggZZinterf_TempDataHist_Up)

        ggZZpdfName = "ggZZ_RooWidth_Up_{0:.0f}_{1:.0f}".format(self.channel,self.sqrts)
        ggZZpdf_Up = ROOT.RooRealSumPdf(ggZZpdfName,ggZZpdfName,ROOT.RooArgList(ggZZsignal_TemplatePdf_Up,ggZZinterf_TemplatePdf_Up,ggZZbkg_TemplatePdf_Up),ROOT.RooArgList(sigRatesNorm,interfRatesNorm,bkgRatesNorm))

        #Down Systematics pdf        
        TemplateName = "ggZZsignal_TempDataHist_Down_{0:.0f}_{1:.0f}".format(self.channel,self.sqrts)
        PdfName = "ggZZsignal_TemplatePdf_Down_{0:.0f}_{1:.0f}".format(self.channel,self.sqrts)
        if self.dimensions > 1 :
            ggZZsignal_TempDataHist_Down = ROOT.RooDataHist(TemplateName,TemplateName,ROOT.RooArgList(CMS_zz4l_widthMass,CMS_zz4l_widthKD),Sig_T_2_Down_QCD)
            ggZZsignal_TemplatePdf_Down = ROOT.RooHistFunc(PdfName,PdfName,ROOT.RooArgSet(CMS_zz4l_widthMass,CMS_zz4l_widthKD),ggZZsignal_TempDataHist_Down)
        elif self.dimensions ==1  :
            ggZZsignal_TempDataHist_Down = ROOT.RooDataHist(TemplateName,TemplateName,ROOT.RooArgList(CMS_zz4l_widthMass),Sig_T_2_Down_QCD.ProjectionX())
            ggZZsignal_TemplatePdf_Down = ROOT.RooHistFunc(PdfName,PdfName,ROOT.RooArgSet(CMS_zz4l_widthMass),ggZZsignal_TempDataHist_Down)
        elif self.dimensions ==0 :
            ggZZsignal_TempDataHist_Down = ROOT.RooDataHist(TemplateName,TemplateName,ROOT.RooArgList(CMS_zz4l_widthKD),Sig_T_2_Down_QCD.ProjectionY())
            ggZZsignal_TemplatePdf_Down = ROOT.RooHistFunc(PdfName,PdfName,ROOT.RooArgSet(CMS_zz4l_widthKD),ggZZsignal_TempDataHist_Down)
            
        TemplateName = "ggZZbkg_TempDataHist_Down_{0:.0f}_{1:.0f}".format(self.channel,self.sqrts)
        PdfName = "ggZZbkg_TemplatePdf_Down_{0:.0f}_{1:.0f}".format(self.channel,self.sqrts)
        if self.dimensions > 1 :
            ggZZbkg_TempDataHist_Down = ROOT.RooDataHist(TemplateName,TemplateName,ROOT.RooArgList(CMS_zz4l_widthMass,CMS_zz4l_widthKD),Sig_T_1_Down_QCD)
            ggZZbkg_TemplatePdf_Down = ROOT.RooHistFunc(PdfName,PdfName,ROOT.RooArgSet(CMS_zz4l_widthMass,CMS_zz4l_widthKD),ggZZbkg_TempDataHist_Down)
        elif self.dimensions ==1  :
            ggZZbkg_TempDataHist_Down = ROOT.RooDataHist(TemplateName,TemplateName,ROOT.RooArgList(CMS_zz4l_widthMass),Sig_T_1_Down_QCD.ProjectionX())
            ggZZbkg_TemplatePdf_Down = ROOT.RooHistFunc(PdfName,PdfName,ROOT.RooArgSet(CMS_zz4l_widthMass),ggZZbkg_TempDataHist_Down)
        elif self.dimensions ==0  :
            ggZZbkg_TempDataHist_Down = ROOT.RooDataHist(TemplateName,TemplateName,ROOT.RooArgList(CMS_zz4l_widthKD),Sig_T_1_Down_QCD.ProjectionY())
            ggZZbkg_TemplatePdf_Down = ROOT.RooHistFunc(PdfName,PdfName,ROOT.RooArgSet(CMS_zz4l_widthKD),ggZZbkg_TempDataHist_Down)
        
        TemplateName = "ggZZinterf_TempDataHist_Down_{0:.0f}_{1:.0f}".format(self.channel,self.sqrts)
        PdfName = "ggZZinterf_TemplatePdf_Down_{0:.0f}_{1:.0f}".format(self.channel,self.sqrts)
        if self.dimensions > 1 :   
            ggZZinterf_TempDataHist_Down = ROOT.RooDataHist(TemplateName,TemplateName,ROOT.RooArgList(CMS_zz4l_widthMass,CMS_zz4l_widthKD),Sig_T_4_Down_QCD)
            ggZZinterf_TemplatePdf_Down = ROOT.RooHistFunc(PdfName,PdfName,ROOT.RooArgSet(CMS_zz4l_widthMass,CMS_zz4l_widthKD),ggZZinterf_TempDataHist_Down)
        if self.dimensions == 1 :   
            ggZZinterf_TempDataHist_Down = ROOT.RooDataHist(TemplateName,TemplateName,ROOT.RooArgList(CMS_zz4l_widthMass),Sig_T_4_Down_QCD.ProjectionX())
            ggZZinterf_TemplatePdf_Down = ROOT.RooHistFunc(PdfName,PdfName,ROOT.RooArgSet(CMS_zz4l_widthMass),ggZZinterf_TempDataHist_Down)            
        if self.dimensions == 0 :   
            ggZZinterf_TempDataHist_Down = ROOT.RooDataHist(TemplateName,TemplateName,ROOT.RooArgList(CMS_zz4l_widthKD),Sig_T_4_Down_QCD.ProjectionY())
            ggZZinterf_TemplatePdf_Down = ROOT.RooHistFunc(PdfName,PdfName,ROOT.RooArgSet(CMS_zz4l_widthKD),ggZZinterf_TempDataHist_Down)

        ggZZpdfName = "ggZZ_RooWidth_Down_{0:.0f}_{1:.0f}".format(self.channel,self.sqrts)
        ggZZpdf_Down = ROOT.RooRealSumPdf(ggZZpdfName,ggZZpdfName,ROOT.RooArgList(ggZZsignal_TemplatePdf_Down,ggZZinterf_TemplatePdf_Down,ggZZbkg_TemplatePdf_Down),ROOT.RooArgList(sigRatesNorm,interfRatesNorm,bkgRatesNorm))


        #CMS_zz4l_APscale_syst = ROOT.RooRealVar("QCDscale_ggH","QCDscale_ggH",0.0,-1,1)
        #CMS_zz4l_APscale_syst.setConstant(true)
        CMS_zz4l_APscale_syst = w.factory("QCDscale_ggH[-7,7]")
        morphVarListggZZ = ROOT.RooArgList()
        morphVarListggZZ.add(CMS_zz4l_APscale_syst)
        MorphList_ggZZ = ROOT.RooArgList()
        MorphList_ggZZ.add(ggZZpdf_Nominal)
        MorphList_ggZZ.add(ggZZpdf_Up)
        MorphList_ggZZ.add(ggZZpdf_Down)
        

        asympowname = "kappalow_ggZZ_QCD_{0:.0f}_{1:.0f}".format(self.channel,self.sqrts)
        #kappalow = ROOT.RooRealVar(asympowname,asympowname,totalRateDown/totalRate_ggzz)#kappalow = ROOT.RooRealVar(asympowname,asympowname,rateSignal_Down+rateBkg_Down-rateInterf_Down)
        kappalow = ROOT.RooFormulaVar(asympowname,"@0/@1",ROOT.RooArgList(ggZZQCDDown_norm,ggZZNominal_norm))
        asympowname = "kappahigh_ggZZ_QCD_{0:.0f}_{1:.0f}".format(self.channel,self.sqrts)
        #kappahigh = ROOT.RooRealVar(asympowname,asympowname,totalRateUp/totalRate_ggzz)#kappahigh = ROOT.RooRealVar(asympowname,asympowname,rateSignal_Up+rateBkg_Up-rateInterf_Up)        
        kappahigh = ROOT.RooFormulaVar(asympowname,"@0/@1",ROOT.RooArgList(ggZZQCDUp_norm,ggZZNominal_norm))
        asympowname = "Asympow_ggZZ_QCD_{0:.0f}_{1:.0f}".format(self.channel,self.sqrts)
#--K-factor and alphaS have non-linear behavior
        thetaSyst_ggZZ = AsymPow(asympowname,asympowname,kappalow,kappahigh,CMS_zz4l_APscale_syst)
#        if kappahigh.getVal() > kappalow.getVal() :
#            thetaSyst_ggZZ = AsymPow(asympowname,asympowname,kappalow,kappahigh,CMS_zz4l_APscale_syst)
#        else :
#            thetaSyst_ggZZ = AsymPow(asympowname,asympowname,kappahigh,kappalow,CMS_zz4l_APscale_syst)
        ## -------------------------- SHAPE Systematic 2 ---------------------------------- ##

        #Up Systematics pdf
        TemplateName = "ggZZsignal_TempDataHist_Up_pdf_{0:.0f}_{1:.0f}".format(self.channel,self.sqrts)
        PdfName = "ggZZsignal_TemplatePdf_Up_pdf_{0:.0f}_{1:.0f}".format(self.channel,self.sqrts)
        if self.dimensions > 1 :
            ggZZsignal_TempDataHist_Up_pdf = ROOT.RooDataHist(TemplateName,TemplateName,ROOT.RooArgList(CMS_zz4l_widthMass,CMS_zz4l_widthKD),Sig_T_2_Up_PDF)
            ggZZsignal_TemplatePdf_Up_pdf = ROOT.RooHistFunc(PdfName,PdfName,ROOT.RooArgSet(CMS_zz4l_widthMass,CMS_zz4l_widthKD),ggZZsignal_TempDataHist_Up_pdf)
        elif self.dimensions ==1  :
            ggZZsignal_TempDataHist_Up_pdf = ROOT.RooDataHist(TemplateName,TemplateName,ROOT.RooArgList(CMS_zz4l_widthMass),Sig_T_2_Up_PDF.ProjectionX())
            ggZZsignal_TemplatePdf_Up_pdf = ROOT.RooHistFunc(PdfName,PdfName,ROOT.RooArgSet(CMS_zz4l_widthMass),ggZZsignal_TempDataHist_Up_pdf)
        elif self.dimensions ==0 :
            ggZZsignal_TempDataHist_Up_pdf = ROOT.RooDataHist(TemplateName,TemplateName,ROOT.RooArgList(CMS_zz4l_widthKD),Sig_T_2_Up_PDF.ProjectionY())
            ggZZsignal_TemplatePdf_Up_pdf = ROOT.RooHistFunc(PdfName,PdfName,ROOT.RooArgSet(CMS_zz4l_widthKD),ggZZsignal_TempDataHist_Up_pdf)
            
        TemplateName = "ggZZbkg_TempDataHist_Up_pdf_{0:.0f}_{1:.0f}".format(self.channel,self.sqrts)
        PdfName = "ggZZbkg_TemplatePdf_Up_pdf_{0:.0f}_{1:.0f}".format(self.channel,self.sqrts)
        if self.dimensions > 1 :
            ggZZbkg_TempDataHist_Up_pdf = ROOT.RooDataHist(TemplateName,TemplateName,ROOT.RooArgList(CMS_zz4l_widthMass,CMS_zz4l_widthKD),Sig_T_1_Up_PDF)
            ggZZbkg_TemplatePdf_Up_pdf = ROOT.RooHistFunc(PdfName,PdfName,ROOT.RooArgSet(CMS_zz4l_widthMass,CMS_zz4l_widthKD),ggZZbkg_TempDataHist_Up_pdf)
        elif self.dimensions ==1  :
            ggZZbkg_TempDataHist_Up_pdf = ROOT.RooDataHist(TemplateName,TemplateName,ROOT.RooArgList(CMS_zz4l_widthMass),Sig_T_1_Up_PDF.ProjectionX())
            ggZZbkg_TemplatePdf_Up_pdf = ROOT.RooHistFunc(PdfName,PdfName,ROOT.RooArgSet(CMS_zz4l_widthMass),ggZZbkg_TempDataHist_Up_pdf)
        elif self.dimensions ==0  :
            ggZZbkg_TempDataHist_Up_pdf = ROOT.RooDataHist(TemplateName,TemplateName,ROOT.RooArgList(CMS_zz4l_widthKD),Sig_T_1_Up_PDF.ProjectionY())
            ggZZbkg_TemplatePdf_Up_pdf = ROOT.RooHistFunc(PdfName,PdfName,ROOT.RooArgSet(CMS_zz4l_widthKD),ggZZbkg_TempDataHist_Up_pdf)
        
        TemplateName = "ggZZinterf_TempDataHist_Up_pdf_{0:.0f}_{1:.0f}".format(self.channel,self.sqrts)
        PdfName = "ggZZinterf_TemplatePdf_Up_pdf_{0:.0f}_{1:.0f}".format(self.channel,self.sqrts)
        if self.dimensions > 1 :   
            ggZZinterf_TempDataHist_Up_pdf = ROOT.RooDataHist(TemplateName,TemplateName,ROOT.RooArgList(CMS_zz4l_widthMass,CMS_zz4l_widthKD),Sig_T_4_Up_PDF)
            ggZZinterf_TemplatePdf_Up_pdf = ROOT.RooHistFunc(PdfName,PdfName,ROOT.RooArgSet(CMS_zz4l_widthMass,CMS_zz4l_widthKD),ggZZinterf_TempDataHist_Up_pdf)
        if self.dimensions == 1 :   
            ggZZinterf_TempDataHist_Up_pdf = ROOT.RooDataHist(TemplateName,TemplateName,ROOT.RooArgList(CMS_zz4l_widthMass),Sig_T_4_Up_PDF.ProjectionX())
            ggZZinterf_TemplatePdf_Up_pdf = ROOT.RooHistFunc(PdfName,PdfName,ROOT.RooArgSet(CMS_zz4l_widthMass),ggZZinterf_TempDataHist_Up_pdf)            
        if self.dimensions == 0 :   
            ggZZinterf_TempDataHist_Up_pdf = ROOT.RooDataHist(TemplateName,TemplateName,ROOT.RooArgList(CMS_zz4l_widthKD),Sig_T_4_Up_PDF.ProjectionY())
            ggZZinterf_TemplatePdf_Up_pdf = ROOT.RooHistFunc(PdfName,PdfName,ROOT.RooArgSet(CMS_zz4l_widthKD),ggZZinterf_TempDataHist_Up_pdf)

        ggZZpdfName = "ggZZ_RooWidth_Up_pdf_{0:.0f}_{1:.0f}".format(self.channel,self.sqrts)
        ggZZpdf_Up_pdf = ROOT.RooRealSumPdf(ggZZpdfName,ggZZpdfName,ROOT.RooArgList(ggZZsignal_TemplatePdf_Up_pdf,ggZZinterf_TemplatePdf_Up_pdf,ggZZbkg_TemplatePdf_Up_pdf),ROOT.RooArgList(sigRatesNorm,interfRatesNorm,bkgRatesNorm))

        #Down Systematics pdf        
        TemplateName = "ggZZsignal_TempDataHist_Down_pdf_{0:.0f}_{1:.0f}".format(self.channel,self.sqrts)
        PdfName = "ggZZsignal_TemplatePdf_Down_pdf_{0:.0f}_{1:.0f}".format(self.channel,self.sqrts)
        if self.dimensions > 1 :
            ggZZsignal_TempDataHist_Down_pdf = ROOT.RooDataHist(TemplateName,TemplateName,ROOT.RooArgList(CMS_zz4l_widthMass,CMS_zz4l_widthKD),Sig_T_2_Down_PDF)
            ggZZsignal_TemplatePdf_Down_pdf = ROOT.RooHistFunc(PdfName,PdfName,ROOT.RooArgSet(CMS_zz4l_widthMass,CMS_zz4l_widthKD),ggZZsignal_TempDataHist_Down_pdf)
        elif self.dimensions ==1  :
            ggZZsignal_TempDataHist_Down_pdf = ROOT.RooDataHist(TemplateName,TemplateName,ROOT.RooArgList(CMS_zz4l_widthMass),Sig_T_2_Down_PDF.ProjectionX())
            ggZZsignal_TemplatePdf_Down_pdf = ROOT.RooHistFunc(PdfName,PdfName,ROOT.RooArgSet(CMS_zz4l_widthMass),ggZZsignal_TempDataHist_Down_pdf)
        elif self.dimensions ==0 :
            ggZZsignal_TempDataHist_Down_pdf = ROOT.RooDataHist(TemplateName,TemplateName,ROOT.RooArgList(CMS_zz4l_widthKD),Sig_T_2_Down_PDF.ProjectionY())
            ggZZsignal_TemplatePdf_Down_pdf = ROOT.RooHistFunc(PdfName,PdfName,ROOT.RooArgSet(CMS_zz4l_widthKD),ggZZsignal_TempDataHist_Down_pdf)
            
        TemplateName = "ggZZbkg_TempDataHist_Down_pdf_{0:.0f}_{1:.0f}".format(self.channel,self.sqrts)
        PdfName = "ggZZbkg_TemplatePdf_Down_pdf_{0:.0f}_{1:.0f}".format(self.channel,self.sqrts)
        if self.dimensions > 1 :
            ggZZbkg_TempDataHist_Down_pdf = ROOT.RooDataHist(TemplateName,TemplateName,ROOT.RooArgList(CMS_zz4l_widthMass,CMS_zz4l_widthKD),Sig_T_1_Down_PDF)
            ggZZbkg_TemplatePdf_Down_pdf = ROOT.RooHistFunc(PdfName,PdfName,ROOT.RooArgSet(CMS_zz4l_widthMass,CMS_zz4l_widthKD),ggZZbkg_TempDataHist_Down_pdf)
        elif self.dimensions ==1  :
            ggZZbkg_TempDataHist_Down_pdf = ROOT.RooDataHist(TemplateName,TemplateName,ROOT.RooArgList(CMS_zz4l_widthMass),Sig_T_1_Down_PDF.ProjectionX())
            ggZZbkg_TemplatePdf_Down_pdf = ROOT.RooHistFunc(PdfName,PdfName,ROOT.RooArgSet(CMS_zz4l_widthMass),ggZZbkg_TempDataHist_Down_pdf)
        elif self.dimensions ==0  :
            ggZZbkg_TempDataHist_Down_pdf = ROOT.RooDataHist(TemplateName,TemplateName,ROOT.RooArgList(CMS_zz4l_widthKD),Sig_T_1_Down_PDF.ProjectionY())
            ggZZbkg_TemplatePdf_Down_pdf = ROOT.RooHistFunc(PdfName,PdfName,ROOT.RooArgSet(CMS_zz4l_widthKD),ggZZbkg_TempDataHist_Down_pdf)
        
        TemplateName = "ggZZinterf_TempDataHist_Down_pdf_{0:.0f}_{1:.0f}".format(self.channel,self.sqrts)
        PdfName = "ggZZinterf_TemplatePdf_Down_pdf_{0:.0f}_{1:.0f}".format(self.channel,self.sqrts)
        if self.dimensions > 1 :   
            ggZZinterf_TempDataHist_Down_pdf = ROOT.RooDataHist(TemplateName,TemplateName,ROOT.RooArgList(CMS_zz4l_widthMass,CMS_zz4l_widthKD),Sig_T_4_Down_PDF)
            ggZZinterf_TemplatePdf_Down_pdf = ROOT.RooHistFunc(PdfName,PdfName,ROOT.RooArgSet(CMS_zz4l_widthMass,CMS_zz4l_widthKD),ggZZinterf_TempDataHist_Down_pdf)
        if self.dimensions == 1 :   
            ggZZinterf_TempDataHist_Down_pdf = ROOT.RooDataHist(TemplateName,TemplateName,ROOT.RooArgList(CMS_zz4l_widthMass),Sig_T_4_Down_PDF.ProjectionX())
            ggZZinterf_TemplatePdf_Down_pdf = ROOT.RooHistFunc(PdfName,PdfName,ROOT.RooArgSet(CMS_zz4l_widthMass),ggZZinterf_TempDataHist_Down_pdf)            
        if self.dimensions == 0 :   
            ggZZinterf_TempDataHist_Down_pdf = ROOT.RooDataHist(TemplateName,TemplateName,ROOT.RooArgList(CMS_zz4l_widthKD),Sig_T_4_Down_PDF.ProjectionY())
            ggZZinterf_TemplatePdf_Down_pdf = ROOT.RooHistFunc(PdfName,PdfName,ROOT.RooArgSet(CMS_zz4l_widthKD),ggZZinterf_TempDataHist_Down_pdf)

        ggZZpdfName = "ggZZ_RooWidth_Down_pdf_{0:.0f}_{1:.0f}".format(self.channel,self.sqrts)
        ggZZpdf_Down_pdf = ROOT.RooRealSumPdf(ggZZpdfName,ggZZpdfName,ROOT.RooArgList(ggZZsignal_TemplatePdf_Down_pdf,ggZZinterf_TemplatePdf_Down_pdf,ggZZbkg_TemplatePdf_Down_pdf),ROOT.RooArgList(sigRatesNorm,interfRatesNorm,bkgRatesNorm))


        #CMS_zz4l_pdf_gg_syst = ROOT.RooRealVar("pdf_gg","pdf_gg",0.0,-1,1)
        CMS_zz4l_pdf_gg_syst = w.factory("pdf_gg[-7,7]")
        morphVarListggZZ.add(CMS_zz4l_pdf_gg_syst)
        MorphList_ggZZ.add(ggZZpdf_Up_pdf)
        MorphList_ggZZ.add(ggZZpdf_Down_pdf)
        
        ggZZpdf = ROOT.VerticalInterpPdf("ggzz","ggzz",MorphList_ggZZ,morphVarListggZZ)
        #ggZZpdf = ggZZpdf_Nominal
        

        asympowname = "kappalow_ggZZ_pdf_{0:.0f}_{1:.0f}".format(self.channel,self.sqrts)
        #kappalow_pdf = ROOT.RooRealVar(asympowname,asympowname,totalRateDown_pdf/totalRate_ggzz)
        kappalow_pdf = ROOT.RooFormulaVar(asympowname,"@0/@1",ROOT.RooArgList(ggZZPDFDown_norm,ggZZNominal_norm))
        asympowname = "kappahigh_ggZZ_pdf_{0:.0f}_{1:.0f}".format(self.channel,self.sqrts)
        #kappahigh_pdf = ROOT.RooRealVar(asympowname,asympowname,totalRateUp_pdf/totalRate_ggzz)    
        kappahigh_pdf = ROOT.RooFormulaVar(asympowname,"@0/@1",ROOT.RooArgList(ggZZPDFUp_norm,ggZZNominal_norm))
        asympowname = "Asympow_ggZZ_pdf_{0:.0f}_{1:.0f}".format(self.channel,self.sqrts)
#--kappahigh>kappalow comparison does not make sense for anti-correlated uncertainty here
        thetaSyst_ggZZ_pdf = AsymPow(asympowname,asympowname,kappalow_pdf,kappahigh_pdf,CMS_zz4l_pdf_gg_syst)
#        if kappahigh_pdf > kappalow_pdf :
#            thetaSyst_ggZZ_pdf = AsymPow(asympowname,asympowname,kappalow_pdf,kappahigh_pdf,CMS_zz4l_pdf_gg_syst)
#        else :
#            thetaSyst_ggZZ_pdf = AsymPow(asympowname,asympowname,kappahigh_pdf,kappalow_pdf,CMS_zz4l_pdf_gg_syst)
         ## -------------------------- VBF offshell SHAPES ---------------------------------- ##
        
        sigRateName = "signal_VBFrate_{0:.0f}_{1:.0f}".format(self.channel,self.sqrts)
        VBFsigRates = ROOT.RooRealVar(sigRateName,sigRateName,0.0,10000.0)
        bkgRateName = "bkg_VBFrate_{0:.0f}_{1:.0f}".format(self.channel,self.sqrts)
        VBFbkgRates = ROOT.RooRealVar(bkgRateName,bkgRateName,0.0,10000.0)
        interfRateName = "interf_VBFrate_{0:.0f}_{1:.0f}".format(self.channel,self.sqrts)
        VBFinterfRates = ROOT.RooRealVar(interfRateName,interfRateName,0.0,10000.0)

        ##Assume BKG & INTERF are from templates
        sigRateNameNorm = "signalNorm_VBFrate_{0:.0f}_{1:.0f}".format(self.channel,self.sqrts)
        VBFsigRatesNorm = ROOT.RooFormulaVar(sigRateNameNorm,"@0*@3*@1*@2/(@0*@3*@1*@2-sqrt(@0*@3*@1*@2)+1)",ROOT.RooArgList(x,mu,muV,Kframework))
        interfRateNameNorm = "interfNorm_VBFrate_{0:.0f}_{1:.0f}".format(self.channel,self.sqrts)
        VBFinterfRatesNorm = ROOT.RooFormulaVar(interfRateNameNorm,"-sqrt(@0*@3*@1*@2)/(@0*@3*@1*@2-sqrt(@0*@3*@1*@2)+1)",ROOT.RooArgList(x,mu,muV,Kframework))
        bkgRateNameNorm = "bkgNorm_VBFrate_{0:.0f}_{1:.0f}".format(self.channel,self.sqrts)
        VBFbkgRatesNorm = ROOT.RooFormulaVar(bkgRateNameNorm,"1/(@0*@3*@1*@2-sqrt(@0*@3*@1*@2)+1)",ROOT.RooArgList(x,mu,muV,Kframework))

        TemplateName = "VBFsignal_TempDataHist_{0:.0f}_{1:.0f}".format(self.channel,self.sqrts)
        PdfName = "VBFsignal_TemplatePdf_{0:.0f}_{1:.0f}".format(self.channel,self.sqrts)
        if self.dimensions > 1 :
            VBFsignal_TempDataHist = ROOT.RooDataHist(TemplateName,TemplateName,ROOT.RooArgList(CMS_zz4l_widthMass,CMS_zz4l_widthKD),VBF_T_2) #nel rooarglist: ,CMS_zz4l_widthKD
            VBFsignal_TemplatePdf = ROOT.RooHistFunc(PdfName,PdfName,ROOT.RooArgSet(CMS_zz4l_widthMass,CMS_zz4l_widthKD),VBFsignal_TempDataHist)
        elif self.dimensions ==1  :
            VBFsignal_TempDataHist = ROOT.RooDataHist(TemplateName,TemplateName,ROOT.RooArgList(CMS_zz4l_widthMass),VBF_T_2.ProjectionX()) #nel rooarglist: ,CMS_zz4l_widthKD
            VBFsignal_TemplatePdf = ROOT.RooHistFunc(PdfName,PdfName,ROOT.RooArgSet(CMS_zz4l_widthMass),VBFsignal_TempDataHist)
        elif self.dimensions == 0 :
            VBFsignal_TempDataHist = ROOT.RooDataHist(TemplateName,TemplateName,ROOT.RooArgList(CMS_zz4l_widthKD),VBF_T_2.ProjectionY()) #nel rooarglist: ,CMS_zz4l_widthKD
            VBFsignal_TemplatePdf = ROOT.RooHistFunc(PdfName,PdfName,ROOT.RooArgSet(CMS_zz4l_widthKD),VBFsignal_TempDataHist)


        TemplateName = "VBFbkg_TempDataHist_{0:.0f}_{1:.0f}".format(self.channel,self.sqrts)
        PdfName = "VBFbkg_TemplatePdf_{0:.0f}_{1:.0f}".format(self.channel,self.sqrts)
        if self.dimensions > 1 :
            VBFbkg_TempDataHist = ROOT.RooDataHist(TemplateName,TemplateName,ROOT.RooArgList(CMS_zz4l_widthMass,CMS_zz4l_widthKD),VBF_T_1)
            VBFbkg_TemplatePdf = ROOT.RooHistFunc(PdfName,PdfName,ROOT.RooArgSet(CMS_zz4l_widthMass,CMS_zz4l_widthKD),VBFbkg_TempDataHist)
        elif self.dimensions ==1  :
            VBFbkg_TempDataHist = ROOT.RooDataHist(TemplateName,TemplateName,ROOT.RooArgList(CMS_zz4l_widthMass),VBF_T_1.ProjectionX())
            VBFbkg_TemplatePdf = ROOT.RooHistFunc(PdfName,PdfName,ROOT.RooArgSet(CMS_zz4l_widthMass),VBFbkg_TempDataHist)
        elif self.dimensions ==0  :            
            VBFbkg_TempDataHist = ROOT.RooDataHist(TemplateName,TemplateName,ROOT.RooArgList(CMS_zz4l_widthKD),VBF_T_1.ProjectionY())
            VBFbkg_TemplatePdf = ROOT.RooHistFunc(PdfName,PdfName,ROOT.RooArgSet(CMS_zz4l_widthKD),VBFbkg_TempDataHist)
            
        TemplateName = "VBFinterf_TempDataHist_{0:.0f}_{1:.0f}".format(self.channel,self.sqrts)
        PdfName = "VBFinterf_TemplatePdf_{0:.0f}_{1:.0f}".format(self.channel,self.sqrts)
        if self.dimensions > 1 :
            VBFinterf_TempDataHist = ROOT.RooDataHist(TemplateName,TemplateName,ROOT.RooArgList(CMS_zz4l_widthMass,CMS_zz4l_widthKD),VBF_T_4)
            VBFinterf_TemplatePdf = ROOT.RooHistFunc(PdfName,PdfName,ROOT.RooArgSet(CMS_zz4l_widthMass,CMS_zz4l_widthKD),VBFinterf_TempDataHist)
        elif self.dimensions ==1  :
            VBFinterf_TempDataHist = ROOT.RooDataHist(TemplateName,TemplateName,ROOT.RooArgList(CMS_zz4l_widthMass),VBF_T_4.ProjectionX())
            VBFinterf_TemplatePdf = ROOT.RooHistFunc(PdfName,PdfName,ROOT.RooArgSet(CMS_zz4l_widthMass),VBFinterf_TempDataHist)
        elif self.dimensions ==0  :
            VBFinterf_TempDataHist = ROOT.RooDataHist(TemplateName,TemplateName,ROOT.RooArgList(CMS_zz4l_widthKD),VBF_T_4.ProjectionY())
            VBFinterf_TemplatePdf = ROOT.RooHistFunc(PdfName,PdfName,ROOT.RooArgSet(CMS_zz4l_widthKD),VBFinterf_TempDataHist)

        #can = ROOT.TCanvas("c0","c0",800,800)
        #VBFsignal_TemplatePdf.createHistogram("CMS_zz4l_widthMass,CMS_zz4l_widthKD").Draw("COLZ")
        #can.SaveAs("tempVBF_T_1_{0}.png".format(self.appendName))
        #VBFbkg_TemplatePdf.createHistogram("CMS_zz4l_widthMass,CMS_zz4l_widthKD").Draw("COLZ")
        #can.SaveAs("tempVBF_T_2_{0}.png".format(self.appendName))
        #VBFinterf_TemplatePdf.createHistogram("CMS_zz4l_widthMass,CMS_zz4l_widthKD").Draw("COLZ")
        #can.SaveAs("tempVBF_T_4_{0}.png".format(self.appendName))
            
        VBFpdfName = "VBF_RooWidth_Nominal_{0:.0f}_{1:.0f}".format(self.channel,self.sqrts)
        VBFpdf_Nominal = ROOT.RooRealSumPdf(VBFpdfName,VBFpdfName,ROOT.RooArgList(VBFsignal_TemplatePdf,VBFinterf_TemplatePdf,VBFbkg_TemplatePdf),ROOT.RooArgList(VBFsigRatesNorm,VBFinterfRatesNorm,VBFbkgRatesNorm))
        #VBFpdf = ROOT.RooRealSumPdf(VBFpdfName,VBFpdfName,ROOT.RooArgList(VBFsignal_TemplatePdf,VBFinterf_TemplatePdf,VBFbkg_TemplatePdf),ROOT.RooArgList(VBFsigRatesNorm,VBFinterfRatesNorm,VBFbkgRatesNorm))


        #can = ROOT.TCanvas("c1","c1",800,800)
        #VBFpdf_Nominal.createHistogram("CMS_zz4l_widthMass,CMS_zz4l_widthKD").Draw("COLZ")
        #can.SaveAs("tempVBF_T_pdf_{0}.png".format(self.appendName))
        #VBFbkg_TemplatePdf.createHistogram("CMS_zz4l_widthMass,CMS_zz4l_widthKD").Draw("COLZ")
        #can.SaveAs("tempVBF_T_2_{0}.png".format(self.appendName))
        #VBFinterf_TemplatePdf.createHistogram("CMS_zz4l_widthMass,CMS_zz4l_widthKD").Draw("COLZ")
        #can.SaveAs("tempVBF_T_4_{0}.png".format(self.appendName))

        #VBF Up systematics
        TemplateName = "VBFsignal_TempDataHist_{0:.0f}_{1:.0f}_Up".format(self.channel,self.sqrts)
        PdfName = "VBFsignal_TemplatePdf_{0:.0f}_{1:.0f}_Up".format(self.channel,self.sqrts)
        if self.dimensions > 1 :
            VBFsignal_TempDataHist_Up = ROOT.RooDataHist(TemplateName,TemplateName,ROOT.RooArgList(CMS_zz4l_widthMass,CMS_zz4l_widthKD),VBF_T_2_Up) #nel rooarglist: ,CMS_zz4l_widthKD
            VBFsignal_TemplatePdf_Up = ROOT.RooHistFunc(PdfName,PdfName,ROOT.RooArgSet(CMS_zz4l_widthMass,CMS_zz4l_widthKD),VBFsignal_TempDataHist_Up)
        elif self.dimensions ==1  :
            VBFsignal_TempDataHist_Up = ROOT.RooDataHist(TemplateName,TemplateName,ROOT.RooArgList(CMS_zz4l_widthMass),VBF_T_2_Up.ProjectionX()) #nel rooarglist: ,CMS_zz4l_widthKD
            VBFsignal_TemplatePdf_Up = ROOT.RooHistFunc(PdfName,PdfName,ROOT.RooArgSet(CMS_zz4l_widthMass),VBFsignal_TempDataHist_Up)
        elif self.dimensions == 0 :
            VBFsignal_TempDataHist_Up = ROOT.RooDataHist(TemplateName,TemplateName,ROOT.RooArgList(CMS_zz4l_widthKD),VBF_T_2_Up.ProjectionY()) #nel rooarglist: ,CMS_zz4l_widthKD
            VBFsignal_TemplatePdf_Up = ROOT.RooHistFunc(PdfName,PdfName,ROOT.RooArgSet(CMS_zz4l_widthKD),VBFsignal_TempDataHist_Up)


        TemplateName = "VBFbkg_TempDataHist_{0:.0f}_{1:.0f}_Up".format(self.channel,self.sqrts)
        PdfName = "VBFbkg_TemplatePdf_{0:.0f}_{1:.0f}_Up".format(self.channel,self.sqrts)
        if self.dimensions > 1 :
            VBFbkg_TempDataHist_Up = ROOT.RooDataHist(TemplateName,TemplateName,ROOT.RooArgList(CMS_zz4l_widthMass,CMS_zz4l_widthKD),VBF_T_1_Up)
            VBFbkg_TemplatePdf_Up = ROOT.RooHistFunc(PdfName,PdfName,ROOT.RooArgSet(CMS_zz4l_widthMass,CMS_zz4l_widthKD),VBFbkg_TempDataHist_Up)
        elif self.dimensions ==1  :
            VBFbkg_TempDataHist_Up = ROOT.RooDataHist(TemplateName,TemplateName,ROOT.RooArgList(CMS_zz4l_widthMass),VBF_T_1_Up.ProjectionX())
            VBFbkg_TemplatePdf_Up = ROOT.RooHistFunc(PdfName,PdfName,ROOT.RooArgSet(CMS_zz4l_widthMass),VBFbkg_TempDataHist_Up)
        elif self.dimensions ==0  :            
            VBFbkg_TempDataHist_Up = ROOT.RooDataHist(TemplateName,TemplateName,ROOT.RooArgList(CMS_zz4l_widthKD),VBF_T_1_Up.ProjectionY())
            VBFbkg_TemplatePdf_Up = ROOT.RooHistFunc(PdfName,PdfName,ROOT.RooArgSet(CMS_zz4l_widthKD),VBFbkg_TempDataHist_Up)
            
        TemplateName = "VBFinterf_TempDataHist_{0:.0f}_{1:.0f}_Up".format(self.channel,self.sqrts)
        PdfName = "VBFinterf_TemplatePdf_{0:.0f}_{1:.0f}_Up".format(self.channel,self.sqrts)
        if self.dimensions > 1 :
            VBFinterf_TempDataHist_Up = ROOT.RooDataHist(TemplateName,TemplateName,ROOT.RooArgList(CMS_zz4l_widthMass,CMS_zz4l_widthKD),VBF_T_4_Up)
            VBFinterf_TemplatePdf_Up = ROOT.RooHistFunc(PdfName,PdfName,ROOT.RooArgSet(CMS_zz4l_widthMass,CMS_zz4l_widthKD),VBFinterf_TempDataHist_Up)
        elif self.dimensions ==1  :
            VBFinterf_TempDataHist_Up = ROOT.RooDataHist(TemplateName,TemplateName,ROOT.RooArgList(CMS_zz4l_widthMass),VBF_T_4_Up.ProjectionX())
            VBFinterf_TemplatePdf_Up = ROOT.RooHistFunc(PdfName,PdfName,ROOT.RooArgSet(CMS_zz4l_widthMass),VBFinterf_TempDataHist_Up)
        elif self.dimensions ==0  :
            VBFinterf_TempDataHist_Up = ROOT.RooDataHist(TemplateName,TemplateName,ROOT.RooArgList(CMS_zz4l_widthKD),VBF_T_4_Up.ProjectionY())
            VBFinterf_TemplatePdf_Up = ROOT.RooHistFunc(PdfName,PdfName,ROOT.RooArgSet(CMS_zz4l_widthKD),VBFinterf_TempDataHist_Up)

        VBFpdfName = "VBF_RooWidth_Nominal_{0:.0f}_{1:.0f}_Up".format(self.channel,self.sqrts)
        VBFpdf_Up = ROOT.RooRealSumPdf(VBFpdfName,VBFpdfName,ROOT.RooArgList(VBFsignal_TemplatePdf_Up,VBFinterf_TemplatePdf_Up,VBFbkg_TemplatePdf_Up),ROOT.RooArgList(VBFsigRatesNorm,VBFinterfRatesNorm,VBFbkgRatesNorm))
        

        #VBF Down systematics
        TemplateName = "VBFsignal_TempDataHist_{0:.0f}_{1:.0f}_Down".format(self.channel,self.sqrts)
        PdfName = "VBFsignal_TemplatePdf_{0:.0f}_{1:.0f}_Down".format(self.channel,self.sqrts)
        if self.dimensions > 1 :
            VBFsignal_TempDataHist_Down = ROOT.RooDataHist(TemplateName,TemplateName,ROOT.RooArgList(CMS_zz4l_widthMass,CMS_zz4l_widthKD),VBF_T_2_Down) #nel rooarglist: ,CMS_zz4l_widthKD
            VBFsignal_TemplatePdf_Down = ROOT.RooHistFunc(PdfName,PdfName,ROOT.RooArgSet(CMS_zz4l_widthMass,CMS_zz4l_widthKD),VBFsignal_TempDataHist_Down)
        elif self.dimensions ==1  :
            VBFsignal_TempDataHist_Down = ROOT.RooDataHist(TemplateName,TemplateName,ROOT.RooArgList(CMS_zz4l_widthMass),VBF_T_2_Down.ProjectionX()) #nel rooarglist: ,CMS_zz4l_widthKD
            VBFsignal_TemplatePdf_Down = ROOT.RooHistFunc(PdfName,PdfName,ROOT.RooArgSet(CMS_zz4l_widthMass),VBFsignal_TempDataHist_Down)
        elif self.dimensions == 0 :
            VBFsignal_TempDataHist_Down = ROOT.RooDataHist(TemplateName,TemplateName,ROOT.RooArgList(CMS_zz4l_widthKD),VBF_T_2_Down.ProjectionY()) #nel rooarglist: ,CMS_zz4l_widthKD
            VBFsignal_TemplatePdf_Down = ROOT.RooHistFunc(PdfName,PdfName,ROOT.RooArgSet(CMS_zz4l_widthKD),VBFsignal_TempDataHist_Down)


        TemplateName = "VBFbkg_TempDataHist_{0:.0f}_{1:.0f}_Down".format(self.channel,self.sqrts)
        PdfName = "VBFbkg_TemplatePdf_{0:.0f}_{1:.0f}_Down".format(self.channel,self.sqrts)
        if self.dimensions > 1 :
            VBFbkg_TempDataHist_Down = ROOT.RooDataHist(TemplateName,TemplateName,ROOT.RooArgList(CMS_zz4l_widthMass,CMS_zz4l_widthKD),VBF_T_1_Down)
            VBFbkg_TemplatePdf_Down = ROOT.RooHistFunc(PdfName,PdfName,ROOT.RooArgSet(CMS_zz4l_widthMass,CMS_zz4l_widthKD),VBFbkg_TempDataHist_Down)
        elif self.dimensions ==1  :
            VBFbkg_TempDataHist_Down = ROOT.RooDataHist(TemplateName,TemplateName,ROOT.RooArgList(CMS_zz4l_widthMass),VBF_T_1_Down.ProjectionX())
            VBFbkg_TemplatePdf_Down = ROOT.RooHistFunc(PdfName,PdfName,ROOT.RooArgSet(CMS_zz4l_widthMass),VBFbkg_TempDataHist_Down)
        elif self.dimensions ==0  :            
            VBFbkg_TempDataHist_Down = ROOT.RooDataHist(TemplateName,TemplateName,ROOT.RooArgList(CMS_zz4l_widthKD),VBF_T_1_Down.ProjectionY())
            VBFbkg_TemplatePdf_Down = ROOT.RooHistFunc(PdfName,PdfName,ROOT.RooArgSet(CMS_zz4l_widthKD),VBFbkg_TempDataHist_Down)
            
        TemplateName = "VBFinterf_TempDataHist_{0:.0f}_{1:.0f}_Down".format(self.channel,self.sqrts)
        PdfName = "VBFinterf_TemplatePdf_{0:.0f}_{1:.0f}_Down".format(self.channel,self.sqrts)
        if self.dimensions > 1 :
            VBFinterf_TempDataHist_Down = ROOT.RooDataHist(TemplateName,TemplateName,ROOT.RooArgList(CMS_zz4l_widthMass,CMS_zz4l_widthKD),VBF_T_4_Down)
            VBFinterf_TemplatePdf_Down = ROOT.RooHistFunc(PdfName,PdfName,ROOT.RooArgSet(CMS_zz4l_widthMass,CMS_zz4l_widthKD),VBFinterf_TempDataHist_Down)
        elif self.dimensions ==1  :
            VBFinterf_TempDataHist_Down = ROOT.RooDataHist(TemplateName,TemplateName,ROOT.RooArgList(CMS_zz4l_widthMass),VBF_T_4_Down.ProjectionX())
            VBFinterf_TemplatePdf_Down = ROOT.RooHistFunc(PdfName,PdfName,ROOT.RooArgSet(CMS_zz4l_widthMass),VBFinterf_TempDataHist_Down)
        elif self.dimensions ==0  :
            VBFinterf_TempDataHist_Down = ROOT.RooDataHist(TemplateName,TemplateName,ROOT.RooArgList(CMS_zz4l_widthKD),VBF_T_4_Down.ProjectionY())
            VBFinterf_TemplatePdf_Down = ROOT.RooHistFunc(PdfName,PdfName,ROOT.RooArgSet(CMS_zz4l_widthKD),VBFinterf_TempDataHist_Down)

        VBFpdfName = "VBF_RooWidth_Nominal_{0:.0f}_{1:.0f}_Down".format(self.channel,self.sqrts)
        VBFpdf_Down = ROOT.RooRealSumPdf(VBFpdfName,VBFpdfName,ROOT.RooArgList(VBFsignal_TemplatePdf_Down,VBFinterf_TemplatePdf_Down,VBFbkg_TemplatePdf_Down),ROOT.RooArgList(VBFsigRatesNorm,VBFinterfRatesNorm,VBFbkgRatesNorm))


        CMS_zz4l_VBFscale_syst = ROOT.RooRealVar("CMS_zz4l_VBFscale_syst","CMS_zz4l_VBFscale_syst",0.0,-1,1)
        morphVarListVBF = ROOT.RooArgList()
        morphVarListVBF.add(CMS_zz4l_VBFscale_syst)
        MorphList_VBF = ROOT.RooArgList()
        MorphList_VBF.add(VBFpdf_Nominal)
        MorphList_VBF.add(VBFpdf_Up)
        MorphList_VBF.add(VBFpdf_Down)


        VBFpdf = ROOT.VerticalInterpPdf("VBFpdf","VBFpdf",MorphList_VBF,morphVarListVBF)

        asympowname = "kappalow_VBF_{0:.0f}_{1:.0f}".format(self.channel,self.sqrts)
        #kappalowVBF = ROOT.RooRealVar(asympowname,asympowname,totalRateVBFDown/totalRate_vbf)#kappalow = ROOT.RooRealVar(asympowname,asympowname,rateSignal_Down+rateBkg_Down-rateInterf_Down)
        kappalowVBF = ROOT.RooFormulaVar(asympowname,"@0/@1",ROOT.RooArgList(VBFDown_norm,VBFNominal_norm))#kappalow = ROOT.RooRealVar(asympowname,asympowname,rateSignal_Down+rateBkg_Down-rateInterf_Down)
        asympowname = "kappahigh_VBF_{0:.0f}_{1:.0f}".format(self.channel,self.sqrts)
        #kappahighVBF = ROOT.RooRealVar(asympowname,asympowname,totalRateVBFUp/totalRate_vbf)#kappahigh = ROOT.RooRealVar(asympowname,asympowname,rateSignal_Up+rateBkg_Up-rateInterf_Up)        
        kappahighVBF = ROOT.RooFormulaVar(asympowname,"@0/@1",ROOT.RooArgList(VBFUp_norm,VBFNominal_norm))#kappalow = ROOT.RooRealVar(asympowname,asympowname,rateSignal_Down+rateBkg_Down-rateInterf_Down)
        asympowname = "Asympow_VBF_{0:.0f}_{1:.0f}".format(self.channel,self.sqrts)
#--kappahigh>kappalow comparison does not matter here
        thetaSyst_VBF = AsymPow(asympowname,asympowname,kappalowVBF,kappahighVBF,CMS_zz4l_VBFscale_syst)
#        if kappahighVBF > kappalowVBF :
#            thetaSyst_VBF = AsymPow(asympowname,asympowname,kappalowVBF,kappahighVBF,CMS_zz4l_VBFscale_syst)
#        else :
#            thetaSyst_VBF = AsymPow(asympowname,asympowname,kappahighVBF,kappalowVBF,CMS_zz4l_VBFscale_syst)
        #Provo con formule Ulash
        
        ## -------------------------- OTHER BACKGROUND SHAPES ---------------------------------- ##
    
        ## qqZZ contribution
        name = "CMS_qqzzbkg_a0_{0:.0f}_{1:.0f}".format( self.channel,self.sqrts )
        CMS_qqzzbkg_a0 = ROOT.RooRealVar(name,"CMS_qqzzbkg_a0",115.3,0.,200.)
        name = "CMS_qqzzbkg_a1_{0:.0f}_{1:.0f}".format( self.channel,self.sqrts )
        CMS_qqzzbkg_a1 = ROOT.RooRealVar(name,"CMS_qqzzbkg_a1",21.96,0.,200.)
        name = "CMS_qqzzbkg_a2_{0:.0f}_{1:.0f}".format( self.channel,self.sqrts )
        CMS_qqzzbkg_a2 = ROOT.RooRealVar(name,"CMS_qqzzbkg_a2",122.8,0.,200.)
        name = "CMS_qqzzbkg_a3_{0:.0f}_{1:.0f}".format( self.channel,self.sqrts )
        CMS_qqzzbkg_a3 = ROOT.RooRealVar(name,"CMS_qqzzbkg_a3",0.03479,0.,1.)
        name = "CMS_qqzzbkg_a4_{0:.0f}_{1:.0f}".format( self.channel,self.sqrts )
        CMS_qqzzbkg_a4 = ROOT.RooRealVar(name,"CMS_qqzzbkg_a4",185.5,0.,200.)
        name = "CMS_qqzzbkg_a5_{0:.0f}_{1:.0f}".format( self.channel,self.sqrts )
        CMS_qqzzbkg_a5 = ROOT.RooRealVar(name,"CMS_qqzzbkg_a5",12.67,0.,200.)
        name = "CMS_qqzzbkg_a6_{0:.0f}_{1:.0f}".format( self.channel,self.sqrts )
        CMS_qqzzbkg_a6 = ROOT.RooRealVar(name,"CMS_qqzzbkg_a6",34.81,0.,100.)
        name = "CMS_qqzzbkg_a7_{0:.0f}_{1:.0f}".format( self.channel,self.sqrts )
        CMS_qqzzbkg_a7 = ROOT.RooRealVar(name,"CMS_qqzzbkg_a7",0.1393,0.,1.)
        name = "CMS_qqzzbkg_a8_{0:.0f}_{1:.0f}".format( self.channel,self.sqrts )
        CMS_qqzzbkg_a8 = ROOT.RooRealVar(name,"CMS_qqzzbkg_a8",66.,0.,200.)
        name = "CMS_qqzzbkg_a9_{0:.0f}_{1:.0f}".format( self.channel,self.sqrts )
        CMS_qqzzbkg_a9 = ROOT.RooRealVar(name,"CMS_qqzzbkg_a9",0.07191,0.,1.)
        name = "CMS_qqzzbkg_a10_{0:.0f}_{1:.0f}".format(self.channel,self.sqrts )
        CMS_qqzzbkg_a10 = ROOT.RooRealVar(name,"CMS_qqzzbkg_a10",94.11,0.,200.)
        name = "CMS_qqzzbkg_a11_{0:.0f}_{1:.0f}".format(self.channel,self.sqrts )
        CMS_qqzzbkg_a11 = ROOT.RooRealVar(name,"CMS_qqzzbkg_a11",-5.111,-100.,100.)
        name = "CMS_qqzzbkg_a12_{0:.0f}_{1:.0f}".format(self.channel,self.sqrts )
        CMS_qqzzbkg_a12 = ROOT.RooRealVar(name,"CMS_qqzzbkg_a12",4834,0.,10000.)
        name = "CMS_qqzzbkg_a13_{0:.0f}_{1:.0f}".format(self.channel,self.sqrts )
        CMS_qqzzbkg_a13 = ROOT.RooRealVar(name,"CMS_qqzzbkg_a13",0.2543,0.,1.)
        
        CMS_qqzzbkg_a0.setVal(theInputs['qqZZshape_a0'])
        CMS_qqzzbkg_a1.setVal(theInputs['qqZZshape_a1'])
        CMS_qqzzbkg_a2.setVal(theInputs['qqZZshape_a2'])
        CMS_qqzzbkg_a3.setVal(theInputs['qqZZshape_a3'])
        CMS_qqzzbkg_a4.setVal(theInputs['qqZZshape_a4'])
        CMS_qqzzbkg_a5.setVal(theInputs['qqZZshape_a5'])
        CMS_qqzzbkg_a6.setVal(theInputs['qqZZshape_a6'])
        CMS_qqzzbkg_a7.setVal(theInputs['qqZZshape_a7'])
        CMS_qqzzbkg_a8.setVal(theInputs['qqZZshape_a8'])
        CMS_qqzzbkg_a9.setVal(theInputs['qqZZshape_a9'])
        CMS_qqzzbkg_a10.setVal(theInputs['qqZZshape_a10'])
        CMS_qqzzbkg_a11.setVal(theInputs['qqZZshape_a11'])
        CMS_qqzzbkg_a12.setVal(theInputs['qqZZshape_a12'])
        CMS_qqzzbkg_a13.setVal(theInputs['qqZZshape_a13'])
        
        CMS_qqzzbkg_a0.setConstant(True)
        CMS_qqzzbkg_a1.setConstant(True)
        CMS_qqzzbkg_a2.setConstant(True)
        CMS_qqzzbkg_a3.setConstant(True)
        CMS_qqzzbkg_a4.setConstant(True)
        CMS_qqzzbkg_a5.setConstant(True)
        CMS_qqzzbkg_a6.setConstant(True)
        CMS_qqzzbkg_a7.setConstant(True)
        CMS_qqzzbkg_a8.setConstant(True)
        CMS_qqzzbkg_a9.setConstant(True)
        CMS_qqzzbkg_a10.setConstant(True)
        CMS_qqzzbkg_a11.setConstant(True)
        CMS_qqzzbkg_a12.setConstant(True)
        CMS_qqzzbkg_a13.setConstant(True)

        #TO BE CLEANED UP ->this part should be moved in inputs
        CMS_qqzzbkg_p0=ROOT.RooRealVar("CMS_qqzzbkg_p0","CMS_qqzzbkg_p0",1.04012)
        CMS_qqzzbkg_p1=ROOT.RooRealVar("CMS_qqzzbkg_p1","CMS_qqzzbkg_p1",-0.000125088)
        CMS_qqzzbkg_p2=ROOT.RooRealVar("CMS_qqzzbkg_p2","CMS_qqzzbkg_p2",2.39404e-07)
        CMS_qqzzbkg_p3=ROOT.RooRealVar("CMS_qqzzbkg_p3","CMS_qqzzbkg_p3",1-0.034)
        CMS_qqzzbkg_p4=ROOT.RooRealVar("CMS_qqzzbkg_p4","CMS_qqzzbkg_p4",1+0.027)
        CMS_qqzzbkg_p0.setConstant(True)
        CMS_qqzzbkg_p1.setConstant(True)
        CMS_qqzzbkg_p2.setConstant(True)
        CMS_qqzzbkg_p3.setConstant(True)
        CMS_qqzzbkg_p4.setConstant(True)

        #TO BE CLEANED UP ->this part should be moved in inputs
        CMS_qqzzbkg_EWK_p0=ROOT.RooRealVar("CMS_qqzzbkg_EWK_p0","CMS_qqzzbkg_EWK_p0",0.953385)
        CMS_qqzzbkg_EWK_p1=ROOT.RooRealVar("CMS_qqzzbkg_EWK_p1","CMS_qqzzbkg_EWK_p1",0.000412406)
        CMS_qqzzbkg_EWK_p2=ROOT.RooRealVar("CMS_qqzzbkg_EWK_p2","CMS_qqzzbkg_EWK_p2",-5.45148e-07)
        CMS_qqzzbkg_EWK_p3=ROOT.RooRealVar("CMS_qqzzbkg_EWK_p3","CMS_qqzzbkg_EWK_p3",2.63944e-10)
        CMS_qqzzbkg_EWK_p4=ROOT.RooRealVar("CMS_qqzzbkg_EWK_p4","CMS_qqzzbkg_EWK_p4",1-0.029)
        CMS_qqzzbkg_EWK_p5=ROOT.RooRealVar("CMS_qqzzbkg_EWK_p5","CMS_qqzzbkg_EWK_p5",1+0.029)
        CMS_qqzzbkg_EWK_p0.setConstant(True)
        CMS_qqzzbkg_EWK_p1.setConstant(True)
        CMS_qqzzbkg_EWK_p2.setConstant(True)
        CMS_qqzzbkg_EWK_p3.setConstant(True)
        CMS_qqzzbkg_EWK_p4.setConstant(True)
        CMS_qqzzbkg_EWK_p5.setConstant(True)
        
        bkg_qqzz_mass_temp = ROOT.RooqqZZPdf_v2("bkg_qqzz_mass_temp","bkg_qqzz_mass_temp",CMS_zz4l_widthMass,CMS_qqzzbkg_a0,CMS_qqzzbkg_a1,CMS_qqzzbkg_a2,CMS_qqzzbkg_a3,CMS_qqzzbkg_a4,CMS_qqzzbkg_a5,CMS_qqzzbkg_a6,CMS_qqzzbkg_a7,CMS_qqzzbkg_a8,CMS_qqzzbkg_a9,CMS_qqzzbkg_a10,CMS_qqzzbkg_a11,CMS_qqzzbkg_a12,CMS_qqzzbkg_a13)

        qqZZ_Scale_Syst = w.factory("QCDscale_VV[-7,7]")
        #bkg_qqzz_syst_shape = ROOT.RooGenericPdf("bkg_qqzz_syst_shape","TMath::Max(1+@0*(@1-1+@2*@4+@3*@4*@4),0.)",ROOT.RooArgList(qqZZ_Scale_Syst,CMS_qqzzbkg_p0,CMS_qqzzbkg_p1,CMS_qqzzbkg_p2,CMS_zz4l_widthMass))
        bkg_qqzz_syst_shape = ROOT.RooFormulaVar("bkg_qqzz_syst_shape","TMath::Max(1+@0*(@1-1+@2*@4+@3*@4*@4),0.)",ROOT.RooArgList(qqZZ_Scale_Syst,CMS_qqzzbkg_p0,CMS_qqzzbkg_p1,CMS_qqzzbkg_p2,CMS_zz4l_widthMass))
        qqZZ_EWK_Syst = w.factory("EWKcorr_VV[-7,7]")
        #bkg_qqzz_EWK_syst_shape = ROOT.RooGenericPdf("bkg_qqzz_EWK_syst_shape","TMath::Max(1+@0*(@1-1+@2*@5+@3*@5*@5+@4*@5*@5*@5),0.)",ROOT.RooArgList(qqZZ_EWK_Syst,CMS_qqzzbkg_EWK_p0,CMS_qqzzbkg_EWK_p1,CMS_qqzzbkg_EWK_p2,CMS_qqzzbkg_EWK_p3,CMS_zz4l_widthMass))
        bkg_qqzz_EWK_syst_shape = ROOT.RooFormulaVar("bkg_qqzz_EWK_syst_shape","TMath::Max(1+@0*(@1-1+@2*@5+@3*@5*@5+@4*@5*@5*@5),0.)",ROOT.RooArgList(qqZZ_EWK_Syst,CMS_qqzzbkg_EWK_p0,CMS_qqzzbkg_EWK_p1,CMS_qqzzbkg_EWK_p2,CMS_qqzzbkg_EWK_p3,CMS_zz4l_widthMass))
        
        asympowname = "kappalow_qqZZ_QCD_{0:.0f}_{1:.0f}".format(self.channel,self.sqrts)
        kappalow_QCD_qqzz = ROOT.RooRealVar(asympowname,asympowname,CMS_qqzzbkg_p3.getVal())
        asympowname = "kappahigh_qqZZ_QCD_{0:.0f}_{1:.0f}".format(self.channel,self.sqrts)
        kappahigh_QCD_qqzz = ROOT.RooRealVar(asympowname,asympowname,CMS_qqzzbkg_p4.getVal())
        asympowname = "Asympow_qqZZ_QCD_{0:.0f}_{1:.0f}".format(self.channel,self.sqrts)
        thetaSyst_qqZZ_QCD = AsymPow(asympowname,asympowname,kappalow_QCD_qqzz,kappahigh_QCD_qqzz,qqZZ_Scale_Syst)

        asympowname = "kappalow_qqZZ_EWK_{0:.0f}_{1:.0f}".format(self.channel,self.sqrts)
        kappalow_EWK_qqzz = ROOT.RooRealVar(asympowname,asympowname,CMS_qqzzbkg_EWK_p4.getVal())
        asympowname = "kappahigh_qqZZ_EWK_{0:.0f}_{1:.0f}".format(self.channel,self.sqrts)
        kappahigh_EWK_qqzz = ROOT.RooRealVar(asympowname,asympowname,CMS_qqzzbkg_EWK_p5.getVal())
        asympowname = "Asympow_qqZZ_EWK_{0:.0f}_{1:.0f}".format(self.channel,self.sqrts)
        thetaSyst_qqZZ_EWK = AsymPow(asympowname,asympowname,kappalow_EWK_qqzz,kappahigh_EWK_qqzz,qqZZ_EWK_Syst)
        #asympowname = "Asympow_qqZZ_EWK_{0:.0f}_{1:.0f}".format(self.channel,self.sqrts)
        #thetaSyst_qqZZ_EWK = w.factory("EWKcorr_VV[-7,7]")
        
        bkg_qqzz_norm = ROOT.RooFormulaVar("qqzz_norm","@0*@1",ROOT.RooArgList(thetaSyst_qqZZ_QCD,thetaSyst_qqZZ_EWK))
        #bkg_qqzz_mass = ROOT.RooProdPdf("bkg_qqzz_mass","bkg_qqzz_mass",ROOT.RooArgList(bkg_qqzz_mass_temp,bkg_qqzz_syst_shape,bkg_qqzz_EWK_syst_shape))
        #bkg_qqzz_mass = ROOT.RooProdPdf("bkg_qqzz_mass","bkg_qqzz_mass",ROOT.RooArgList(bkg_qqzz_mass_temp,bkg_qqzz_syst_shape))
        qqzzarglist = ROOT.RooArgList(qqZZ_EWK_Syst,CMS_qqzzbkg_EWK_p0,CMS_qqzzbkg_EWK_p1,CMS_qqzzbkg_EWK_p2,CMS_qqzzbkg_EWK_p3,CMS_zz4l_widthMass,qqZZ_Scale_Syst,CMS_qqzzbkg_p0,CMS_qqzzbkg_p1)
        #qqzzarglist = ROOT.RooArgList(qqZZ_EWK_Syst,CMS_qqzzbkg_EWK_p0,CMS_qqzzbkg_EWK_p1,CMS_qqzzbkg_EWK_p2,CMS_zz4l_widthMass,qqZZ_Scale_Syst,CMS_qqzzbkg_p0,CMS_qqzzbkg_p1)
        qqzzarglist.add(CMS_qqzzbkg_p2)
        #qqzzarglist.add(bkg_qqzz_mass_temp)
        #bkg_qqzz_mass = ROOT.RooGenericPdf("bkg_qqzz_mass","bkg_qqzz_mass","TMath::Max((1+@0*(@1-1+@2*@5+@3*@5*@5+@4*@5*@5*@5))*(1+@6*(@7-1+@8*@5+@9*@5*@5))*@10,0)",qqzzarglist)
        #bkg_qqzz_mass = ROOT.RooGenericPdf("bkg_qqzz_mass","bkg_qqzz_mass","TMath::Max((1+@0*(@1-1+@2*@4+@3*@4*@4))*(1+@5*(@6-1+@7*@4+@8*@4*@4))*@9,0)",qqzzarglist)
        #bkg_qqzz_mass = ROOT.RooGenericPdf("bkg_qqzz_mass","bkg_qqzz_mass","@0*@1*@2",ROOT.RooArgList(bkg_qqzz_mass_temp,bkg_qqzz_EWK_syst_shape,bkg_qqzz_syst_shape))
        #bkg_qqzz_mass = ROOT.RooGenericPdf("bkg_qqzz_mass","bkg_qqzz_mass","@0",ROOT.RooArgList(bkg_qqzz_mass_temp))
        #bkg_qqzz_mass =  bkg_qqzz_mass_temp.Clone()
        #bkg_qqzz_mass.SetNameTitle("bkg_qqzz_mass","bkg_qqzz_mass")
        bkg_qqzz_mass_shape = ROOT.RooGenericPdf("bkg_qqzz_mass_shape","bkg_qqzz_mass_shape","TMath::Max((1+@0*(@1-1+@2*@5+@3*@5*@5+@4*@5*@5*@5))*(1+@6*(@7-1+@8*@5+@9*@5*@5)),0)",qqzzarglist)
        bkg_qqzz_mass = ROOT.RooProdPdf("bkg_qqzz_mass","bkg_qqzz_mass",ROOT.RooArgList(bkg_qqzz_mass_temp,bkg_qqzz_mass_shape))
        
        TemplateName = "qqzz_TempDataHist_{0:.0f}_{1:.0f}".format(self.channel,self.sqrts)
        qqzz_TempDataHist = ROOT.RooDataHist(TemplateName,TemplateName,ROOT.RooArgList(CMS_zz4l_widthMass,CMS_zz4l_widthKD),Bkg_T)
        PdfName = "qqzz_TemplatePdf_{0:.0f}_{1:.0f}".format(self.channel,self.sqrts)
        qqzz_TemplatePdf = ROOT.RooHistPdf(PdfName,PdfName,ROOT.RooArgSet(CMS_zz4l_widthMass,CMS_zz4l_widthKD),qqzz_TempDataHist)
        #qqzz_TemplatePdf.forceNumInt(True)
        #bkg_qqzz_orig = ROOT.RooProdPdf("qqzz_orig_{0:.0f}_{1:.0f}".format(self.channel,self.sqrts),"qqzz_orig_{0:.0f}_{1:.0f}".format(self.channel,self.sqrts),ROOT.RooArgSet(bkg_qqzz_mass),ROOT.RooFit.Conditional(ROOT.RooArgSet(qqzz_TemplatePdf),ROOT.RooArgSet(CMS_zz4l_widthKD)))
        bkg_qqzz = ROOT.RooProdPdf("bkg_qqzz","bkg_qqzz",ROOT.RooArgSet(bkg_qqzz_mass),ROOT.RooFit.Conditional(ROOT.RooArgSet(qqzz_TemplatePdf),ROOT.RooArgSet(CMS_zz4l_widthKD)))
        #TemplateName = "qqzz_orig_TempDataHist_{0:.0f}_{1:.0f}".format(self.channel,self.sqrts)
        #qqzz_TempDataHist1 = ROOT.RooDataHist(TemplateName,TemplateName,ROOT.RooArgList(CMS_zz4l_widthMass,CMS_zz4l_widthKD),bkg_qqzz_orig.createHistogram("CMS_zz4l_widthMass,CMS_zz4l_widthKD"))
        #bkg_qqzz = ROOT.RooHistPdf("bkg_qqzz","bkg_qqzz",ROOT.RooArgSet(CMS_zz4l_widthMass,CMS_zz4l_widthKD),qqzz_TempDataHist1)
        if self.dimensions ==1 :
            #bkg_qqzz = bkg_qqzz_mass
            qqzz_TempDataHist1 = ROOT.RooDataHist(TemplateName,TemplateName,ROOT.RooArgList(CMS_zz4l_widthMass),bkg_qqzz.createHistogram("CMS_zz4l_widthMass,CMS_zz4l_widthKD").ProjectionX())
            bkg_qqzz = ROOT.RooHistPdf("bkg_qqzz","bkg_qqzz",ROOT.RooArgSet(CMS_zz4l_widthMass),qqzz_TempDataHist1)
        elif self.dimensions == 0:
            #qqzz_TempDataHist1 = ROOT.RooDataHist(TemplateName,TemplateName,ROOT.RooArgList(CMS_zz4l_widthKD),Bkg_T.ProjectionY())
            #bkg_qqzz = ROOT.RooHistPdf(PdfName,PdfName,ROOT.RooArgSet(CMS_zz4l_widthKD),qqzz_TempDataHist1)
            #bkg_qqzz = qqzz_TemplatePdf.createProjection(ROOT.RooArgSet(CMS_zz4l_widthMass))
            qqzz_TempDataHist1 = ROOT.RooDataHist(TemplateName,TemplateName,ROOT.RooArgList(CMS_zz4l_widthKD),bkg_qqzz.createHistogram("CMS_zz4l_widthMass,CMS_zz4l_widthKD").ProjectionY())
            bkg_qqzz = ROOT.RooHistPdf(PdfName,PdfName,ROOT.RooArgSet(CMS_zz4l_widthKD),qqzz_TempDataHist1)
            bkg_qqzz.SetNameTitle("bkg_qqzz","bkg_qqzz")
##         TemplateName = "qqzz_TempDataHist_Up_{0:.0f}_{1:.0f}".format(self.channel,self.sqrts)
##         qqzz_TempDataHist_Up = ROOT.RooDataHist(TemplateName,TemplateName,ROOT.RooArgList(CMS_zz4l_widthMass,CMS_zz4l_widthKD),Bkg_T_Up)
##         PdfName = "qqzz_TemplatePdf_Up_{0:.0f}_{1:.0f}".format(self.channel,self.sqrts)
##         qqzz_TemplatePdf_Up = ROOT.RooHistPdf(PdfName,PdfName,ROOT.RooArgSet(CMS_zz4l_widthMass,CMS_zz4l_widthKD),qqzz_TempDataHist_Up)
##         bkg_qqzz_Up = ROOT.RooProdPdf("bkg_qqzzUp","bkg_qqzzUp",ROOT.RooArgSet(bkg_qqzz_mass),ROOT.RooFit.Conditional(ROOT.RooArgSet(qqzz_TemplatePdf_Up),ROOT.RooArgSet(CMS_zz4l_widthKD)))
        
##         TemplateName = "qqzz_TempDataHist_Down_{0:.0f}_{1:.0f}".format(self.channel,self.sqrts)
##         qqzz_TempDataHist_Down = ROOT.RooDataHist(TemplateName,TemplateName,ROOT.RooArgList(CMS_zz4l_widthMass,CMS_zz4l_widthKD),Bkg_T_Down)
##         PdfName = "qqzz_TemplatePdf_Down_{0:.0f}_{1:.0f}".format(self.channel,self.sqrts)
##         qqzz_TemplatePdf_Down = ROOT.RooHistPdf(PdfName,PdfName,ROOT.RooArgSet(CMS_zz4l_widthMass,CMS_zz4l_widthKD),qqzz_TempDataHist_Down)
##         bkg_qqzz_Down = ROOT.RooProdPdf("bkg_qqzzDown","bkg_qqzzDown",ROOT.RooArgSet(bkg_qqzz_mass),ROOT.RooFit.Conditional(ROOT.RooArgSet(qqzz_TemplatePdf_Down),ROOT.RooArgSet(CMS_zz4l_widthKD)))


        ## for integration
        bkg_qqzz_FI = ROOT.RooqqZZPdf_v2("bkg_qqzzTmp_FI","bkg_qqzzTmp_FI",CMS_zz4l_widthMass_FI,CMS_qqzzbkg_a0,CMS_qqzzbkg_a1,CMS_qqzzbkg_a2,CMS_qqzzbkg_a3,CMS_qqzzbkg_a4,CMS_qqzzbkg_a5,CMS_qqzzbkg_a6,CMS_qqzzbkg_a7,CMS_qqzzbkg_a8,CMS_qqzzbkg_a9,CMS_qqzzbkg_a10,CMS_qqzzbkg_a11,CMS_qqzzbkg_a12,CMS_qqzzbkg_a13)
            
        ## Reducible backgrounds
        val_meanL_3P1F = float(theInputs['zjetsShape_mean_3P1F'])
        val_sigmaL_3P1F = float(theInputs['zjetsShape_sigma_3P1F'])
        val_normL_3P1F = float(theInputs['zjetsShape_norm_3P1F'])
        
        val_meanL_2P2F = float(theInputs['zjetsShape_mean_2P2F'])
        val_sigmaL_2P2F = float(theInputs['zjetsShape_sigma_2P2F'])
        val_normL_2P2F = float(theInputs['zjetsShape_norm_2P2F'])
        val_pol0_2P2F = float(theInputs['zjetsShape_pol0_2P2F'])
        val_pol1_2P2F = float(theInputs['zjetsShape_pol1_2P2F'])
        
        val_meanL_2P2F_2 = float(theInputs['zjetsShape_mean_2P2F_2e2mu'])
        val_sigmaL_2P2F_2 = float(theInputs['zjetsShape_sigma_2P2F_2e2mu'])
        val_normL_2P2F_2 = float(theInputs['zjetsShape_norm_2P2F_2e2mu'])

        TemplateName = "zjet_TempDataHist_{0:.0f}_{1:.0f}".format(self.channel,self.sqrts)
        zjet_TempDataHist = ROOT.RooDataHist(TemplateName,TemplateName,ROOT.RooArgList(CMS_zz4l_widthMass,CMS_zz4l_widthKD),Bkg_ZX)
        PdfName = "zjet_TemplatePdf_{0:.0f}_{1:.0f}".format(self.channel,self.sqrts)
        zjet_TemplatePdfNominal = ROOT.RooHistPdf(PdfName,PdfName,ROOT.RooArgSet(CMS_zz4l_widthMass,CMS_zz4l_widthKD),zjet_TempDataHist)

        TemplateName = "zjet_TempDataHist_Up_{0:.0f}_{1:.0f}".format(self.channel,self.sqrts)
        zjet_TempDataHistUp = ROOT.RooDataHist(TemplateName,TemplateName,ROOT.RooArgList(CMS_zz4l_widthMass,CMS_zz4l_widthKD),Bkg_ZX_Up)
        PdfName = "zjet_TemplatePdf_Up_{0:.0f}_{1:.0f}".format(self.channel,self.sqrts)
        zjet_TemplatePdfUp = ROOT.RooHistPdf(PdfName,PdfName,ROOT.RooArgSet(CMS_zz4l_widthMass,CMS_zz4l_widthKD),zjet_TempDataHistUp)

        TemplateName = "zjet_TempDataHist_Down_{0:.0f}_{1:.0f}".format(self.channel,self.sqrts)
        zjet_TempDataHistDown = ROOT.RooDataHist(TemplateName,TemplateName,ROOT.RooArgList(CMS_zz4l_widthMass,CMS_zz4l_widthKD),Bkg_ZX_Down)
        PdfName = "zjet_TemplatePdf_Down_{0:.0f}_{1:.0f}".format(self.channel,self.sqrts)
        zjet_TemplatePdfDown = ROOT.RooHistPdf(PdfName,PdfName,ROOT.RooArgSet(CMS_zz4l_widthMass,CMS_zz4l_widthKD),zjet_TempDataHistDown)

        #CMS_zz4l_ZXshape_syst = ROOT.RooRealVar("CMS_zz4l_ZXshape_syst","CMS_zz4l_ZXshape_syst",0.0,-1,1)
        #morphVarListZX = ROOT.RooArgList()
        #morphVarListZX.add(CMS_zz4l_ZXshape_syst)
        #MorphList_ZX = ROOT.RooArgList()
        #MorphList_ZX.add(zjet_TemplatePdfNominal)
        #MorphList_ZX.add(zjet_TemplatePdfUp)
        #MorphList_ZX.add(zjet_TemplatePdfDown)
        
        #zjet_TemplatePdf = ROOT.VerticalInterpPdf("ZXshapeInterp","ZXshapeInterp",MorphList_ZX,morphVarListZX)

        if (self.channel == self.ID_4mu):
            name = "mlZjet_{0:.0f}_{1:.0f}".format(self.channel,self.sqrts)
            mlZjet = ROOT.RooRealVar(name,"mean landau Zjet",val_meanL_2P2F)
            name = "slZjet_{0:.0f}_{1:.0f}".format(self.channel,self.sqrts)
            slZjet = ROOT.RooRealVar(name,"sigma landau Zjet",val_sigmaL_2P2F)
            print "mean 4mu: ",mlZjet.getVal()
            print "sigma 4mu: ",slZjet.getVal()
            bkg_zjets_mass = ROOT.RooLandau("bkg_zjetsTmp","bkg_zjetsTmp",CMS_zz4l_widthMass,mlZjet,slZjet)
            bkg_zjets_Nominal = ROOT.RooProdPdf()
            bkg_zjets_Nominal = ROOT.RooProdPdf("bkg_zjets_Nominal","bkg_zjets_Nominal",ROOT.RooArgSet(bkg_zjets_mass),ROOT.RooFit.Conditional(ROOT.RooArgSet(zjet_TemplatePdfNominal),ROOT.RooArgSet(CMS_zz4l_widthKD)))
            bkg_zjets_Up = ROOT.RooProdPdf()
            bkg_zjets_Up = ROOT.RooProdPdf("bkg_zjets_Up","bkg_zjets_Up",ROOT.RooArgSet(bkg_zjets_mass),ROOT.RooFit.Conditional(ROOT.RooArgSet(zjet_TemplatePdfUp),ROOT.RooArgSet(CMS_zz4l_widthKD))) 
            bkg_zjets_Down = ROOT.RooProdPdf()
            bkg_zjets_Down = ROOT.RooProdPdf("bkg_zjets_Dn","bkg_zjets_Dn",ROOT.RooArgSet(bkg_zjets_mass),ROOT.RooFit.Conditional(ROOT.RooArgSet(zjet_TemplatePdfDown),ROOT.RooArgSet(CMS_zz4l_widthKD))) 
            
            bkg_zjets_FI = ROOT.RooLandau("bkg_zjetsTmp_FI","bkg_zjetsTmp_FI",CMS_zz4l_widthMass_FI,mlZjet,slZjet)
            
        elif (self.channel == self.ID_4e):

            summa = val_normL_2P2F + val_normL_3P1F
            
            name = "mlZjet_2p2f_{0:.0f}_{1:.0f}".format(self.channel,self.sqrts)
            mlZjet_2p2f = ROOT.RooRealVar(name,"mean landau Zjet 2p2f",val_meanL_2P2F)
            name = "slZjet_2p2f_{0:.0f}_{1:.0f}".format(self.channel,self.sqrts)
            slZjet_2p2f = ROOT.RooRealVar(name,"sigma landau Zjet 2p2f",val_sigmaL_2P2F)
            name = "nlZjet_2p2f_{0:.0f}_{1:.0f}".format(self.channel,self.sqrts)
            nlZjet_2p2f = ROOT.RooRealVar(name,"norm landau Zjet 2p2f",val_normL_2P2F/summa)
            name = "p0Zjet_2p2f_{0:.0f}_{1:.0f}".format(self.channel,self.sqrts)
            p0Zjet_2p2f = ROOT.RooRealVar(name,"p0 Zjet 2p2f",val_pol0_2P2F)
            name = "p1Zjet_2p2f_{0:.0f}_{1:.0f}".format(self.channel,self.sqrts)
            p1Zjet_2p2f = ROOT.RooRealVar(name,"p1 Zjet 2p2f",val_pol1_2P2F)
            print "mean 2p2f 4e: ",mlZjet_2p2f.getVal()
            print "sigma 2p2f 4e: ",slZjet_2p2f.getVal()
            print "norm 2p2f 4e: ",nlZjet_2p2f.getVal()
            print "pol0 2p2f 4e: ",p0Zjet_2p2f.getVal()
            print "pol1 2p2f 4e: ",p1Zjet_2p2f.getVal()
            bkg_zjets_2p2f = ROOT.RooGenericPdf("bkg_zjetsTmp_2p2f","bkg_zjetsTmp_2p2f","(TMath::Landau(@0,@1,@2))*(1.+ TMath::Exp(@3+@4*@0))",RooArgList(CMS_zz4l_widthMass,mlZjet_2p2f,slZjet_2p2f,p0Zjet_2p2f,p1Zjet_2p2f))

            bkg_zjets_2p2f_FI = ROOT.RooGenericPdf("bkg_zjetsTmp_2p2f_FI","bkg_zjetsTmp_2p2f_FI","(TMath::Landau(@0,@1,@2))*(1.+ TMath::Exp(@3+@4*@0))",RooArgList(CMS_zz4l_widthMass_FI,mlZjet_2p2f,slZjet_2p2f,p0Zjet_2p2f,p1Zjet_2p2f))
            
            name = "mlZjet_3p1f_{0:.0f}_{1:.0f}".format(self.channel,self.sqrts)
            mlZjet_3p1f = ROOT.RooRealVar(name,"mean landau Zjet 3p1f",val_meanL_3P1F)
            name = "slZjet_3p1f_{0:.0f}_{1:.0f}".format(self.channel,self.sqrts)
            slZjet_3p1f = ROOT.RooRealVar(name,"sigma landau Zjet 3p1f",val_sigmaL_3P1F)
            name = "nlZjet_3p1f_{0:.0f}_{1:.0f}".format(self.channel,self.sqrts)
            nlZjet_3p1f = ROOT.RooRealVar(name,"norm landau Zjet 3p1f",val_normL_3P1F/summa)
            print "mean 3p1f 4e: ",mlZjet_3p1f.getVal()
            print "sigma 3p1f 4e: ",slZjet_3p1f.getVal()
            print "norm 3p1f 4e: ",nlZjet_3p1f.getVal()

            bkg_zjets_3p1f = ROOT.RooLandau("bkg_zjetsTmp_3p1f","bkg_zjetsTmp_3p1f",CMS_zz4l_widthMass,mlZjet_3p1f,slZjet_3p1f)

            bkg_zjets_3p1f_FI = ROOT.RooLandau("bkg_zjetsTmp_3p1f_FI","bkg_zjetsTmp_3p1f_FI",CMS_zz4l_widthMass_FI,mlZjet_3p1f,slZjet_3p1f)
            
            bkg_zjets_mass = ROOT.RooAddPdf("bkg_zjetsTmp","bkg_zjetsTmp",ROOT.RooArgList(bkg_zjets_2p2f,bkg_zjets_3p1f),ROOT.RooArgList(nlZjet_2p2f,nlZjet_3p1f))
            bkg_zjets_Nominal = ROOT.RooProdPdf()
            bkg_zjets_Nominal = ROOT.RooProdPdf("bkg_zjets_Nominal","bkg_zjets_Nominal",ROOT.RooArgSet(bkg_zjets_mass),ROOT.RooFit.Conditional(ROOT.RooArgSet(zjet_TemplatePdfNominal),ROOT.RooArgSet(CMS_zz4l_widthKD)))
            bkg_zjets_Up = ROOT.RooProdPdf()
            bkg_zjets_Up = ROOT.RooProdPdf("bkg_zjets_Up","bkg_zjets_Up",ROOT.RooArgSet(bkg_zjets_mass),ROOT.RooFit.Conditional(ROOT.RooArgSet(zjet_TemplatePdfUp),ROOT.RooArgSet(CMS_zz4l_widthKD))) 
            bkg_zjets_Down = ROOT.RooProdPdf()
            bkg_zjets_Down = ROOT.RooProdPdf("bkg_zjets_Down","bkg_zjets_Down",ROOT.RooArgSet(bkg_zjets_mass),ROOT.RooFit.Conditional(ROOT.RooArgSet(zjet_TemplatePdfDown),ROOT.RooArgSet(CMS_zz4l_widthKD)))  
            
            bkg_zjets_FI = ROOT.RooAddPdf("bkg_zjetsTmp_FI","bkg_zjetsTmp_FI",ROOT.RooArgList(bkg_zjets_2p2f_FI,bkg_zjets_3p1f_FI),ROOT.RooArgList(nlZjet_2p2f,nlZjet_3p1f))
            
        elif (self.channel == self.ID_2e2mu):

            summa = val_normL_2P2F + val_normL_2P2F_2 + val_normL_3P1F
            
            name = "mlZjet_2p2f_{0:.0f}_{1:.0f}".format(self.channel,self.sqrts)
            mlZjet_2p2f = ROOT.RooRealVar(name,"mean landau Zjet 2p2f",val_meanL_2P2F)
            name = "slZjet_2p2f_{0:.0f}_{1:.0f}".format(self.channel,self.sqrts)
            slZjet_2p2f = ROOT.RooRealVar(name,"sigma landau Zjet 2p2f",val_sigmaL_2P2F)
            name = "nlZjet_2p2f_{0:.0f}_{1:.0f}".format(self.channel,self.sqrts)
            nlZjet_2p2f = ROOT.RooRealVar(name,"norm landau Zjet 2p2f",val_normL_2P2F/summa)
            name = "p0Zjet_2p2f_{0:.0f}_{1:.0f}".format(self.channel,self.sqrts)
            p0Zjet_2p2f = ROOT.RooRealVar(name,"p0 Zjet 2p2f",val_pol0_2P2F)
            name = "p1Zjet_2p2f_{0:.0f}_{1:.0f}".format(self.channel,self.sqrts)
            p1Zjet_2p2f = ROOT.RooRealVar(name,"p1 Zjet 2p2f",val_pol1_2P2F)
            print "mean 2p2f 2mu2e: ",mlZjet_2p2f.getVal()
            print "sigma 2p2f 2mu2e: ",slZjet_2p2f.getVal()
            print "norm 2p2f 2mu2e: ",nlZjet_2p2f.getVal()
            print "pol0 2p2f 2mu2e: ",p0Zjet_2p2f.getVal()
            print "pol1 2p2f 2mu2e: ",p1Zjet_2p2f.getVal()
            bkg_zjets_2p2f = ROOT.RooGenericPdf("bkg_zjetsTmp_2p2f","bkg_zjetsTmp_2p2f","(TMath::Landau(@0,@1,@2))*(1.+ TMath::Exp(@3+@4*@0))",RooArgList(CMS_zz4l_widthMass,mlZjet_2p2f,slZjet_2p2f,p0Zjet_2p2f,p1Zjet_2p2f))
            bkg_zjets_2p2f_FI = ROOT.RooGenericPdf("bkg_zjetsTmp_2p2f_FI","bkg_zjetsTmp_2p2f_FI","(TMath::Landau(@0,@1,@2))*(1.+ TMath::Exp(@3+@4*@0))",RooArgList(CMS_zz4l_widthMass_FI,mlZjet_2p2f,slZjet_2p2f,p0Zjet_2p2f,p1Zjet_2p2f))
            
            name = "mlZjet_2p2f_2_{0:.0f}_{1:.0f}".format(self.channel,self.sqrts)
            mlZjet_2p2f_2 = ROOT.RooRealVar(name,"mean landau Zjet 2p2f 2e2mu",val_meanL_2P2F_2)
            name = "slZjet_2p2f_2_{0:.0f}_{1:.0f}".format(self.channel,self.sqrts)
            slZjet_2p2f_2 = ROOT.RooRealVar(name,"sigma landau Zjet 2p2f 2e2mu",val_sigmaL_2P2F_2)
            name = "nlZjet_2p2f_2_{0:.0f}_{1:.0f}".format(self.channel,self.sqrts)
            nlZjet_2p2f_2 = ROOT.RooRealVar(name,"norm landau Zjet 2p2f 2e2mu",val_normL_2P2F_2/summa)
            print "mean 2p2f 2e2mu: ",mlZjet_2p2f_2.getVal()
            print "sigma 2p2f 2e2mu: ",slZjet_2p2f_2.getVal()
            print "norm 2p2f 2e2mu: ",nlZjet_2p2f_2.getVal()
            bkg_zjets_2p2f_2 = ROOT.RooLandau("bkg_zjetsTmp_2p2f_2","bkg_zjetsTmp_2p2f_2",CMS_zz4l_widthMass,mlZjet_2p2f_2,slZjet_2p2f_2)
            
            bkg_zjets_2p2f_2_FI = ROOT.RooLandau("bkg_zjetsTmp_2p2f_2_FI","bkg_zjetsTmp_2p2f_2_FI",CMS_zz4l_widthMass_FI,mlZjet_2p2f_2,slZjet_2p2f_2)
            
            name = "mlZjet_3p1f_{0:.0f}_{1:.0f}".format(self.channel,self.sqrts)
            mlZjet_3p1f = ROOT.RooRealVar(name,"mean landau Zjet 3p1f",val_meanL_3P1F)
            name = "slZjet_3p1f_{0:.0f}_{1:.0f}".format(self.channel,self.sqrts)
            slZjet_3p1f = ROOT.RooRealVar(name,"sigma landau Zjet 3p1f",val_sigmaL_3P1F)
            name = "nlZjet_3p1f_{0:.0f}_{1:.0f}".format(self.channel,self.sqrts)
            nlZjet_3p1f = ROOT.RooRealVar(name,"norm landau Zjet 3p1f",val_normL_3P1F/summa)
            print "mean 3p1f 2mu2e: ",mlZjet_3p1f.getVal()
            print "sigma 3p1f 2mu2e: ",slZjet_3p1f.getVal()
            print "norm 3p1f 2mu2e: ",nlZjet_3p1f.getVal()
            bkg_zjets_3p1f = ROOT.RooLandau("bkg_zjetsTmp_3p1f","bkg_zjetsTmp_3p1f",CMS_zz4l_widthMass,mlZjet_3p1f,slZjet_3p1f)
       
            bkg_zjets_3p1f_FI = ROOT.RooLandau("bkg_zjetsTmp_3p1f_FI","bkg_zjetsTmp_3p1f_FI",CMS_zz4l_widthMass_FI,mlZjet_3p1f,slZjet_3p1f)
            
            bkg_zjets_mass = ROOT.RooAddPdf("bkg_zjetsTmp","bkg_zjetsTmp",ROOT.RooArgList(bkg_zjets_2p2f,bkg_zjets_3p1f,bkg_zjets_2p2f_2),ROOT.RooArgList(nlZjet_2p2f,nlZjet_3p1f,nlZjet_2p2f_2))
            bkg_zjets_Nominal = ROOT.RooProdPdf()
            bkg_zjets_Nominal = ROOT.RooProdPdf("bkg_zjets_Nominal","bkg_zjets_Nominal",ROOT.RooArgSet(bkg_zjets_mass),ROOT.RooFit.Conditional(ROOT.RooArgSet(zjet_TemplatePdfNominal),ROOT.RooArgSet(CMS_zz4l_widthKD)))
            bkg_zjets_Up = ROOT.RooProdPdf()
            bkg_zjets_Up = ROOT.RooProdPdf("bkg_zjets_Up","bkg_zjets_Up",ROOT.RooArgSet(bkg_zjets_mass),ROOT.RooFit.Conditional(ROOT.RooArgSet(zjet_TemplatePdfUp),ROOT.RooArgSet(CMS_zz4l_widthKD))) 
            bkg_zjets_Down = ROOT.RooProdPdf()
            bkg_zjets_Down = ROOT.RooProdPdf("bkg_zjets_Down","bkg_zjets_Down",ROOT.RooArgSet(bkg_zjets_mass),ROOT.RooFit.Conditional(ROOT.RooArgSet(zjet_TemplatePdfDown),ROOT.RooArgSet(CMS_zz4l_widthKD)))  

            bkg_zjets_FI = ROOT.RooAddPdf("bkg_zjetsTmp_FI","bkg_zjetsTmp_FI",ROOT.RooArgList(bkg_zjets_2p2f_FI,bkg_zjets_3p1f_FI,bkg_zjets_2p2f_2_FI),ROOT.RooArgList(nlZjet_2p2f,nlZjet_3p1f,nlZjet_2p2f_2))


        DataName = "ZX_FullDataHist_{0:.0f}_{1:.0f}".format(self.channel,self.sqrts)
        PdfName = "ZX_FullPdf_{0:.0f}_{1:.0f}".format(self.channel,self.sqrts)
        zjet_DataHistNominal = RooDataHist(DataName,DataName,ROOT.RooArgList(CMS_zz4l_widthMass,CMS_zz4l_widthKD),bkg_zjets_Nominal.createHistogram("{0},{1}".format(CMS_zz4l_widthMass.GetName(),CMS_zz4l_widthKD.GetName())))
        zjet_HistPdfNominaltemp = ROOT.RooHistPdf(PdfName,PdfName,ROOT.RooArgSet(CMS_zz4l_widthMass,CMS_zz4l_widthKD),zjet_DataHistNominal)

        DataName = "ZX_FullDataHist_Up_{0:.0f}_{1:.0f}".format(self.channel,self.sqrts)
        PdfName = "ZX_FullPdf_Up_{0:.0f}_{1:.0f}".format(self.channel,self.sqrts)
        zjet_DataHistUp = RooDataHist(DataName,DataName,ROOT.RooArgList(CMS_zz4l_widthMass,CMS_zz4l_widthKD),bkg_zjets_Up.createHistogram("{0},{1}".format(CMS_zz4l_widthMass.GetName(),CMS_zz4l_widthKD.GetName())))
        zjet_HistPdfUptemp = ROOT.RooHistPdf(PdfName,PdfName,ROOT.RooArgSet(CMS_zz4l_widthMass,CMS_zz4l_widthKD),zjet_DataHistUp)

        DataName = "ZX_FullDataHist_Down_{0:.0f}_{1:.0f}".format(self.channel,self.sqrts)
        PdfName = "ZX_FullPdf_Down_{0:.0f}_{1:.0f}".format(self.channel,self.sqrts)
        zjet_DataHistDown = RooDataHist(DataName,DataName,ROOT.RooArgList(CMS_zz4l_widthMass,CMS_zz4l_widthKD),bkg_zjets_Down.createHistogram("{0},{1}".format(CMS_zz4l_widthMass.GetName(),CMS_zz4l_widthKD.GetName())))
        zjet_HistPdfDowntemp = ROOT.RooHistPdf(PdfName,PdfName,ROOT.RooArgSet(CMS_zz4l_widthMass,CMS_zz4l_widthKD),zjet_DataHistDown)

        if self.dimensions == 0:
            #zjet_HistPdfUptemp.forceNumInt(True)
            #zjet_HistPdfNominaltemp.forceNumInt(True)
            #zjet_HistPdfDowntemp.forceNumInt(True)
            #createHistogram("CMS_zz4l_widthMass,CMS_zz4l_widthKD")
            #zjet_HistPdfUpP = zjet_HistPdfUptemp.createProjection(RooArgSet(CMS_zz4l_widthMass))
            #zjet_HistPdfNominalP = zjet_HistPdfNominaltemp.createProjection(RooArgSet(CMS_zz4l_widthMass))
            #zjet_HistPdfDownP = zjet_HistPdfDowntemp.createProjection(RooArgSet(CMS_zz4l_widthMass))

            PdfName = "ZX_FullPdf_Nominal1_{0:.0f}_{1:.0f}".format(self.channel,self.sqrts)
            TemplateName = "zjet_TempDataHist1_{0:.0f}_{1:.0f}_Nominal".format(self.channel,self.sqrts)
            #zjet_TempDataHist1_Nominal = ROOT.RooDataHist(TemplateName,TemplateName,ROOT.RooArgList(CMS_zz4l_widthKD),Bkg_ZX.ProjectionY())
            zjet_TempDataHist1_Nominal = ROOT.RooDataHist(TemplateName,TemplateName,ROOT.RooArgList(CMS_zz4l_widthKD),bkg_zjets_Nominal.createHistogram("CMS_zz4l_widthMass,CMS_zz4l_widthKD").ProjectionY())
            #zjet_TempDataHist1_Nominal = ROOT.RooDataHist(TemplateName,TemplateName,ROOT.RooArgList(CMS_zz4l_widthKD),zjet_HistPdfNominalP.createHistogram("histNom",CMS_zz4l_widthKD))
            zjet_HistPdfNominal = ROOT.RooHistPdf(PdfName,PdfName,ROOT.RooArgSet(CMS_zz4l_widthKD),zjet_TempDataHist1_Nominal)

            PdfName = "ZX_FullPdf_Up1_{0:.0f}_{1:.0f}".format(self.channel,self.sqrts)
            TemplateName = "zjet_TempDataHist1_{0:.0f}_{1:.0f}_Up".format(self.channel,self.sqrts)           
            #zjet_TempDataHist1_Up = ROOT.RooDataHist(TemplateName,TemplateName,ROOT.RooArgList(CMS_zz4l_widthKD),Bkg_T.ProjectionY())
            zjet_TempDataHist1_Up = ROOT.RooDataHist(TemplateName,TemplateName,ROOT.RooArgList(CMS_zz4l_widthKD),bkg_zjets_Up.createHistogram("CMS_zz4l_widthMass,CMS_zz4l_widthKD").ProjectionY())
            #zjet_TempDataHist1_Up = ROOT.RooDataHist(TemplateName,TemplateName,ROOT.RooArgList(CMS_zz4l_widthKD),zjet_HistPdfUpP.createHistogram("histUp",CMS_zz4l_widthKD))
            zjet_HistPdfUp = ROOT.RooHistPdf(PdfName,PdfName,ROOT.RooArgSet(CMS_zz4l_widthKD),zjet_TempDataHist1_Up)

            PdfName = "ZX_FullPdf_Down1_{0:.0f}_{1:.0f}".format(self.channel,self.sqrts)
            TemplateName = "zjet_TempDataHist1_{0:.0f}_{1:.0f}_Down".format(self.channel,self.sqrts)
            #zjet_TempDataHist1_Down = ROOT.RooDataHist(TemplateName,TemplateName,ROOT.RooArgList(CMS_zz4l_widthKD),Bkg_ZX_Down.ProjectionY())
            zjet_TempDataHist1_Down = ROOT.RooDataHist(TemplateName,TemplateName,ROOT.RooArgList(CMS_zz4l_widthKD),bkg_zjets_Down.createHistogram("CMS_zz4l_widthMass,CMS_zz4l_widthKD").ProjectionY())
            #zjet_TempDataHist1_Down = ROOT.RooDataHist(TemplateName,TemplateName,ROOT.RooArgList(CMS_zz4l_widthKD),zjet_HistPdfDownP.createHistogram("histUp",CMS_zz4l_widthKD))
            zjet_HistPdfDown = ROOT.RooHistPdf(PdfName,PdfName,ROOT.RooArgSet(CMS_zz4l_widthKD),zjet_TempDataHist1_Down)

        if self.dimensions == 2:
            zjet_HistPdfNominal=zjet_HistPdfNominaltemp
            zjet_HistPdfUp=zjet_HistPdfUptemp
            zjet_HistPdfDown=zjet_HistPdfDowntemp
        if self.dimensions == 1 :
            PdfName = "ZX_FullPdf_Nominal1_{0:.0f}_{1:.0f}".format(self.channel,self.sqrts)
            TemplateName = "zjet_TempDataHist1_{0:.0f}_{1:.0f}_Nominal".format(self.channel,self.sqrts)
            zjet_TempDataHist1_Nominal = ROOT.RooDataHist(TemplateName,TemplateName,ROOT.RooArgList(CMS_zz4l_widthMass),bkg_zjets_Nominal.createHistogram("CMS_zz4l_widthMass,CMS_zz4l_widthKD").ProjectionX())
            bkg_zjets = ROOT.RooHistPdf("bkg_zjets","bkg_zjets",ROOT.RooArgSet(CMS_zz4l_widthMass),zjet_TempDataHist1_Nominal)
            #bkg_zjets = bkg_zjets_mass
            #bkg_zjets.SetNameTitle("bkg_zjets","bkg_zjets")
        else:
            CMS_zz4l_ZXshape_syst = ROOT.RooRealVar("CMS_zz4l_ZXshape_syst","CMS_zz4l_ZXshape_syst",0.0,-1,1)
            morphVarListZX = ROOT.RooArgList()
            morphVarListZX.add(CMS_zz4l_ZXshape_syst)
            MorphList_ZX = ROOT.RooArgList()
            MorphList_ZX.add(zjet_HistPdfNominal)
            #MorphList_ZX.add(zjet_HistPdfDown)
            #MorphList_ZX.add(zjet_HistPdfUp)
            MorphList_ZX.add(zjet_HistPdfUp)            
            MorphList_ZX.add(zjet_HistPdfDown)
        
            bkg_zjets = ROOT.VerticalInterpPdf("bkg_zjets","bkg_zjets",MorphList_ZX,morphVarListZX)
        
        ## ------------------- LUMI -------------------- ##
        
        rrvLumi = ROOT.RooRealVar("cmshzz4l_lumi","cmshzz4l_lumi",self.lumi)  
        
        ## ----------------------- RANGES ----------------------- ##
        
        CMS_zz4l_widthMass_FI.setRange("shape",self.low_M,self.high_M)            

        CMS_zz4l_widthMass_FI.setRange("fullrangesignal",self.templRange,1400)
        CMS_zz4l_widthMass_FI.setRange("fullrange",self.templRange,1400)

             
        ## ----------------------- SIGNAL AND BACKGROUND RATES ----------------------- ##

        #bkgRate_qqzz_Shape = Bkg_T.Integral()*self.lumi
        
        ## rate_signal_ggzz = theInputs['ggZZ_signal_rate']/theInputs['qqZZ_lumi']
        ## print " @@@@@@ initial rate: ",theInputs['ggZZ_signal_rate']
        ## print " @@@@@@ corrected rate: ",rate_signal_ggzz
        ## rate_bkg_ggzz = theInputs['ggZZbkg_rate']/theInputs['qqZZ_lumi']
        ## rate_interf_ggzz = theInputs['ggZZ_interf_rate']/theInputs['qqZZ_lumi']
                
##         # Get Normalizations  - Do I still need this part?
##         normalizationBackground_qqzz = bkg_qqzz_FI.createIntegral( ROOT.RooArgSet(CMS_zz4l_widthMass_FI), ROOT.RooFit.Range("fullrange") ).getVal()
##         print 
##         normalizationBackground_ggzz = ggZZpdf_FI.createIntegral( ROOT.RooArgSet(CMS_zz4l_widthMass_FI), ROOT.RooFit.Range("fullrange") ).getVal()
##         #normalizationsignal_ggzz = ggZZsignal_TemplatePdf_FI.createIntegral( ROOT.RooArgSet(CMS_zz4l_widthMass_FI), ROOT.RooFit.Range("fullrange") ).getVal()
##         print " @@@@@@ total normalization: ",normalizationBackground_ggzz
##         #normalizationbkg_ggzz = ggZZbkg_TemplatePdf_FI.createIntegral( ROOT.RooArgSet(CMS_zz4l_widthMass_FI), ROOT.RooFit.Range("fullrange") ).getVal()
##         #normalizationinterf_ggzz = ggZZinterf_TemplatePdf_FI.createIntegral( ROOT.RooArgSet(CMS_zz4l_widthMass_FI), ROOT.RooFit.Range("fullrange") ).getVal()
##         normalizationBackground_zjets = bkg_zjets_FI.createIntegral( ROOT.RooArgSet(CMS_zz4l_widthMass_FI), ROOT.RooFit.Range("fullrange") ).getVal()

##         #print " @@@@@@ channel: "+self.appendName
##         #print " @@@@@@ fullrange zz: ",normalizationBackground_qqzz
##         #print " @@@@@@ fullrange zjets: ",normalizationBackground_zjets
        
##         sclFactorBkg_qqzz = self.lumi*bkgRate_qqzz/normalizationBackground_qqzz
##         sclFactorTotal_ggzz = self.lumi*totalRate_ggzz/normalizationBackground_ggzz
##         #sclFactor_signal_ggzz = self.lumi*rate_signal_ggzz/normalizationsignal_ggzz
##         print " @@@@@@ scale factor: ",sclFactorTotal_ggzz
##         #sclFactor_bkg_ggzz = self.lumi*rate_bkg_ggzz/normalizationbkg_ggzz
##         #sclFactor_interf_ggzz = self.lumi*rate_interf_ggzz/normalizationinterf_ggzz
##         sclFactorBkg_zjets = self.lumi*bkgRate_zjets/normalizationBackground_zjets
               
##         bkgRate_qqzz_Shape = sclFactorBkg_qqzz * bkg_qqzz_FI.createIntegral( ROOT.RooArgSet(CMS_zz4l_widthMass_FI), ROOT.RooFit.Range("shape") ).getVal()
##         #totalRate_ggzz_Shape = sclFactorTotal_ggzz * ggZZpdfFI.createIntegral( ROOT.RooArgSet(CMS_zz4l_widthMassFI), ROOT.RooFit.Range("shape") ).getVal()
##         rate_signal_ggzz_Shape = sclFactorTotal_ggzz * ggZZsignal_TemplatePdf_FI.createIntegral( ROOT.RooArgSet(CMS_zz4l_widthMass_FI), ROOT.RooFit.Range("shape") ).getVal() 
##         rate_bkg_ggzz_Shape = sclFactorTotal_ggzz * ggZZbkg_TemplatePdf_FI.createIntegral( ROOT.RooArgSet(CMS_zz4l_widthMass_FI), ROOT.RooFit.Range("shape") ).getVal() 
##         rate_interf_ggzz_Shape = sclFactorTotal_ggzz * ggZZinterf_TemplatePdf_FI.createIntegral( ROOT.RooArgSet(CMS_zz4l_widthMass_FI), ROOT.RooFit.Range("shape") ).getVal() 
##         totalRate_ggzz_Shape = rate_signal_ggzz_Shape + rate_bkg_ggzz_Shape - rate_interf_ggzz_Shape
##         bkgRate_zjets_Shape = sclFactorBkg_zjets * bkg_zjets_FI.createIntegral( ROOT.RooArgSet(CMS_zz4l_widthMass_FI), ROOT.RooFit.Range("shape") ).getVal()
##         print " @@@@@@ signal normalization in signal region: ",rate_signal_ggzz_Shape
##         print " @@@@@@ total normalization in signal region TEST: ",totalRate_ggzz_Shape
##         print " @@@@@@ interf normalization in signal region: ",rate_interf_ggzz_Shape
##         print " @@@@@@ bkg normalization in signal region: ",rate_bkg_ggzz_Shape

        sigRates.setVal(rate_signal_ggzz_Shape)
        sigRates.setConstant(True)
        bkgRates.setVal(rate_bkg_ggzz_Shape)
        bkgRates.setConstant(True)
        interfRates.setVal(rate_interf_ggzz_Shape)
        interfRates.setConstant(True)

        VBFsigRates.setVal(rate_signal_vbf_Shape)
        VBFsigRates.setConstant(True)
        VBFbkgRates.setVal(rate_bkg_vbf_Shape)
        VBFbkgRates.setConstant(True)
        VBFinterfRates.setVal(rate_interf_vbf_Shape)
        VBFinterfRates.setConstant(True)
        
        if(DEBUG):
            print "Shape signal rate: ",sigRate_ggH_Shape,", background rate: ",bkgRate_qqzz_Shape,", ",bkgRate_zjets_Shape," in ",low_M," - ",high_M
            CMS_zz4l_widthMass.setRange("shapiro",100.,160.)
            bkgRate_qqzz_shapiro = sclFactorBkg_qqzz * bkg_qqzz.createIntegral( ROOT.RooArgSet(CMS_zz4l_widthMass), ROOT.RooFit.Range("shapiro") ).getVal()
            totalRate_ggzz_shapiro = sclFactorTotal_ggzz * ggZZpdf.createIntegral( ROOT.RooArgSet(CMS_zz4l_widthMass), ROOT.RooFit.Range("shapiro") ).getVal()
            bkgRate_zjets_shapiro = sclFactorBkg_zjets * bkg_zjets.createIntegral( ROOT.RooArgSet(CMS_zz4l_widthMass), ROOT.RooFit.Range("shapiro") ).getVal()
            lowmassyield = bkgRate_qqzz_shapiro + totalRate_ggzz_shapiro + bkgRate_zjets_shapiro
            print "low mass yield: ",lowmassyield
        
        ## --------------------------- DATASET --------------------------- ##

        dataFileDir = "CMSdata"
        dataTreeName = "data_obs" 
        dataFileName = "{0}/hzz{1}_{2}.root".format(dataFileDir,self.appendName,self.inputlumi)
        if (DEBUG): print dataFileName," ",dataTreeName 
        data_obs_file = ROOT.TFile(dataFileName)

        print data_obs_file.Get(dataTreeName)
        
        if not (data_obs_file.Get(dataTreeName)):
            print "File, \"",dataFileName,"\", or tree, \"",dataTreeName,"\", not found" 
            print "Exiting..."
            sys.exit()
        
        data_obs_tree = data_obs_file.Get(dataTreeName)
        data_obs = ROOT.RooDataSet()
        datasetName = "data_obs_{0}".format(self.appendName)
        

        data_obs = ROOT.RooDataSet(datasetName,datasetName,data_obs_tree,ROOT.RooArgSet(CMS_zz4l_widthMass,CMS_zz4l_widthKD))
        data_obs_red = data_obs.reduce("CMS_zz4l_widthMass > {0}".format(self.low_M))
  #      data_obs_red.append(data_obs_red)
  #      data_obs_red.append(data_obs_red)  ## 4 times the data!

            
        ## --------------------------- WORKSPACE -------------------------- ##

        endsInP5 = False
        tmpMH = self.low_M
        if ( math.fabs(math.floor(tmpMH)-self.low_M) > 0.001): endsInP5 = True
        if (DEBUG): print "ENDS IN P5  ",endsInP5

        name_Shape = ""
        name_ShapeWS = ""
        name_ShapeWS2 = ""
        name_ShapeWSXSBR = ""

        if (endsInP5): name_Shape = "{0}/HCG/{1:.1f}/hzz4l_{2}S_{3:.0f}TeV.txt".format(self.outputDir,self.low_M,self.appendName,self.sqrts)
        else: name_Shape = "{0}/HCG/{1:.0f}/hzz4l_{2}S_{3:.0f}TeV.txt".format(self.outputDir,self.low_M,self.appendName,self.sqrts)
        
        if (endsInP5): name_ShapeWS = "{0}/HCG/{1:.1f}/hzz4l_{2}S_{3:.0f}TeV.input.root".format(self.outputDir,self.low_M,self.appendName,self.sqrts)
        else: name_ShapeWS = "{0}/HCG/{1:.0f}/hzz4l_{2}S_{3:.0f}TeV.input.root".format(self.outputDir,self.low_M,self.appendName,self.sqrts)
        
        
        name_ShapeWS2 = "hzz4l_{0}S_{1:.0f}TeV.input.root".format(self.appendName,self.sqrts)

        if(DEBUG): print name_Shape,"  ",name_ShapeWS2
        
        w.importClassCode(RooqqZZPdf_v2.Class(),True)
##        w.importClassCode(RooggZZPdf_v2.Class(),True)
##         w.importClassCode(RooRelBWUFParam.Class(),True)
##         w.importClassCode(RooDoubleCB.Class(),True)
        w.importClassCode(RooFormulaVar.Class(),True)
##         if self.isHighMass :
##             w.importClassCode(RooRelBWHighMass.Class(),True)
            
                
                
        getattr(w,'import')(data_obs_red,ROOT.RooFit.Rename("data_obs")) ### Should this be renamed?

        #ggZZpdf_nominal.SetNameTitle("ggzz_nominal","ggzz_nominal")
        #getattr(w,'import')(ggZZpdf_nominal, ROOT.RooFit.RecycleConflictNodes())

        ggZZpdf.SetNameTitle("ggzz","ggzz")
        getattr(w,'import')(ggZZpdf, ROOT.RooFit.RecycleConflictNodes())

        #ggZZpdf_Down.SetNameTitle("ggzz_CMS_zz4l_scale_systDown","ggzz_CMS_zz4l_scale_systDown")
        #getattr(w,'import')(ggZZpdf_Down, ROOT.RooFit.RecycleConflictNodes())

        #ggZZpdf_Up.SetNameTitle("ggzz_CMS_zz4l_scale_systUp","ggzz_CMS_zz4l_scale_systUp")
        #getattr(w,'import')(ggZZpdf_Up, ROOT.RooFit.RecycleConflictNodes())

        VBFpdf.SetNameTitle("vbf_offshell","vbf_offshell")
        getattr(w,'import')(VBFpdf, ROOT.RooFit.RecycleConflictNodes())

        #getattr(w,'import')(CMS_zz4l_syst, ROOT.RooFit.RecycleConflictNodes())

        #w.factory("EXPR::ggzz('ggzz_nominal*(one+ggzz_CMS_zz4l_scale_systUp*CMS_zz4l_syst)',one[1],ggzz_nominal,ggzz_CMS_zz4l_scale_systUp,CMS_zz4l_syst)")
        
        ggZZpdfNormName = "ggZZ_RooWidth_{0:.0f}_{1:.0f}_norm".format(self.channel,self.sqrts)
        #ggZZpdf_norm = ROOT.RooFormulaVar(ggZZpdfNormName,"@0*@3*@4-@1*sqrt(@3*@4)*sign(@5)*sqrt(abs(@5))+@2*@5",ROOT.RooArgList(sigRates,interfRates,bkgRates,x,mu,kbkg))
        ggzzpdf_normarglist = ROOT.RooArgList(sigRates,interfRates,bkgRates,x,mu,kbkg,thetaSyst_ggZZ,muF,thetaSyst_ggZZ_pdf)
        ggzzpdf_normarglist.add(Kframework)
        ggZZpdf_norm = ROOT.RooFormulaVar(ggZZpdfNormName,"(@0*@3*@9*@7*@4-@1*sqrt(@3*@9*@7*@4)*sign(@5)*sqrt(abs(@5))+@2*@5)*@6*@8",ggzzpdf_normarglist)
        ggZZpdf_norm.SetNameTitle("ggzz_norm","ggzz_norm")
        getattr(w,'import')(ggZZpdf_norm, ROOT.RooFit.RecycleConflictNodes())

        VBFpdfNormName = "VBF_RooWidth_{0:.0f}_{1:.0f}_norm".format(self.channel,self.sqrts)
        VBFpdf_norm = ROOT.RooFormulaVar(VBFpdfNormName,"(@0*@3*@7*@6*@4-@1*sqrt(@3*@7*@6*@4)+@2)*@5",ROOT.RooArgList(VBFsigRates,VBFinterfRates,VBFbkgRates,x,mu,thetaSyst_VBF,muV,Kframework))
        VBFpdf_norm.SetNameTitle("vbf_offshell_norm","vbf_offshell_norm")
        getattr(w,'import')(VBFpdf_norm, ROOT.RooFit.RecycleConflictNodes())

        bkg_qqzz.SetNameTitle("bkg_qqzz","bkg_qqzz")
        getattr(w,'import')(bkg_qqzz, ROOT.RooFit.RecycleConflictNodes())

        bkg_qqzz_norm.SetNameTitle("bkg_qqzz_norm","bkg_qqzz_norm")
        if self.dimensions>0 : getattr(w,'import')(bkg_qqzz_norm, ROOT.RooFit.RecycleConflictNodes())
        ##ggZZsignal_TemplatePdf.SetNameTitle("ggsignalzz","ggsignalzz")
        ##ggZZbkg_TemplatePdf.SetNameTitle("ggbkgzz","ggbkgzz")
        ##ggZZinterf_TemplatePdf.SetNameTitle("gginterfzz","gginterfzz")
        bkg_zjets.SetNameTitle("bkg_zjets","bkg_zjets")
        ##getattr(w,'import')(ggZZsignal_TemplatePdf, ROOT.RooFit.RecycleConflictNodes())
        ##getattr(w,'import')(ggZZbkg_TemplatePdf, ROOT.RooFit.RecycleConflictNodes())
        ##getattr(w,'import')(ggZZinterf_TemplatePdf, ROOT.RooFit.RecycleConflictNodes())
        getattr(w,'import')(bkg_zjets, ROOT.RooFit.RecycleConflictNodes())
  
        w.writeToFile(name_ShapeWS)
        
        ## --------------------------- DATACARDS -------------------------- ##

        systematics.setSystematics(bkgRate_qqzz_Shape, totalRate_ggzz_Shape, bkgRate_zjets_Shape)
        systematics_forXSxBR.setSystematics(bkgRate_qqzz_Shape, totalRate_ggzz_Shape,bkgRate_zjets_Shape)

        ## If the channel is not declared in inputs, set rate = 0
        if not self.ggH_chan:  sigRate_ggH_Shape = 0
        if not self.qqH_chan:  sigRate_VBF_Shape = 0
        if not self.WH_chan:   sigRate_WH_Shape = 0
        if not self.ZH_chan:   sigRate_ZH_Shape = 0
        if not self.ttH_chan:  sigRate_ttH_Shape = 0

        if not self.qqZZ_chan:  bkgRate_qqzz_Shape = 0
        if not self.ggZZ_chan:  totalRate_ggzz_Shape = 0
        if not self.zjets_chan: bkgRate_zjets_Shape = 0
        if not self.VBF_offshell_chan: totalRate_vbf_Shape = 0

        rates = {}
        rates['ggH'] = sigRate_ggH_Shape
        rates['qqH'] = sigRate_VBF_Shape
        rates['WH']  = sigRate_WH_Shape
        rates['ZH']  = sigRate_ZH_Shape
        rates['ttH'] = sigRate_ttH_Shape

        rates['qqZZ']  = bkgRate_qqzz_Shape
        rates['ggZZ']  = 1
        rates['VBF_offshell'] = 1
        rates['ggZZ_signal']  = rate_signal_ggzz_Shape
        rates['ggZZbkg']  = rate_bkg_ggzz_Shape
        rates['ggZZ_interf']  = rate_interf_ggzz_Shape
        rates['VBF_offshell_signal']  = rate_signal_vbf_Shape
        rates['VBF_offshell_bkg']  = rate_bkg_vbf_Shape
        rates['VBF_offshell_interf']  = rate_interf_vbf_Shape
        rates['zjets'] = bkgRate_zjets_Shape
        rates['ggZZ_tot'] = totalRate_ggzz_Shape
        rates['VBF_offshell_tot'] = totalRate_vbf_Shape
        rates['ttbar'] = 0
        rates['zbb']   = 0
        

        ## Write Datacards
        fo = open( name_Shape, "wb")
        self.WriteDatacard(fo,theInputs, name_ShapeWS2, rates, data_obs_red.numEntries())
        
        systematics.WriteSystematics(fo, theInputs)
        systematics.WriteShapeSystematics(fo,theInputs)

        print "GO THERE"
        fo.close()
        print "GOT HERE"
        
        


    def WriteDatacard(self,file,theInputs,nameWS,theRates,obsEvents):

        numberSig = self.numberOfSigChan(theInputs)
        numberBg  = self.numberOfBgChan(theInputs)
        
        file.write("imax 1\n")
        file.write("jmax {0}\n".format(numberSig+numberBg-1))
        file.write("kmax *\n")
        
        file.write("------------\n")
        file.write("shapes * * {0} w:$PROCESS w:$PROCESS_$SYSTEMATIC\n".format(nameWS))
        file.write("------------\n")
        

        file.write("bin a{0} \n".format(self.channel))
        file.write("observation {0} \n".format(obsEvents))
        
        file.write("------------\n")
        file.write("## mass window [{0},{1}] \n".format(self.low_M,self.high_M))
        file.write("## signal,bkg,interf,tot rates [{0:.4f}, {1:.4f}, -{2:.4f}, {3:.4f}] \n".format(theRates["ggZZ_signal"],theRates["ggZZbkg"],theRates["ggZZ_interf"],theRates["ggZZ_tot"]))
        file.write("## vbfsig,vbfbkg,vbfinterf,vbftot rates [{0:.4f}, {1:.4f}, -{2:.4f}, {3:.4f}] \n".format(theRates["VBF_offshell_signal"],theRates["VBF_offshell_bkg"],theRates["VBF_offshell_interf"],theRates["VBF_offshell_tot"]))
        file.write("bin ")        

        #channelList=['ggZZ_signal','ggZZ_interf','ggZZbkg','qqZZ','zjets']
        channelList=['ggZZ','VBF_offshell','qqZZ','zjets'] 

        #channelName=['ggsignalzz','gginterfzz','ggZZbkg','bkg_qqzz','bkg_zjets']
        channelName=['ggzz','vbf_offshell','bkg_qqzz','bkg_zjets'] 
         
        for chan in channelList:
            if theInputs[chan]:
                file.write("a{0} ".format(self.channel))
        file.write("\n")
                                        
        file.write("process ")

        i=0

        for chan in channelList:
            #print 'checking if ',chan,' is in the list of to-do'
            #print "{0} ".format(channelName[i])
            if theInputs[chan]:
                file.write("{0} ".format(channelName[i]))
                #print 'writing in card index=',i,'  chan=',chan
                #print "{0} ".format(channelName[i])
            i+=1

        
        file.write("\n")
            
        processLine = "process "

        for x in range(-numberSig+1,1):
            processLine += "{0} ".format(x)

        for y in range(1,numberBg+1):
            processLine += "{0} ".format(y)

        file.write(processLine)
        file.write("\n")
            
        file.write("rate ")
        for chan in channelList:
            if theInputs[chan]:
                file.write("{0:.4f} ".format(theRates[chan]))
        file.write("\n")
        file.write("------------\n")


        
    def numberOfSigChan(self,inputs):

        counter=0

        if inputs['ggZZ']:  counter+=1
        if inputs['ggZZ_signal']: counter+=1
        if inputs['ggZZ_interf']: counter+=1
        if inputs['VBF_offshell']: counter+=1
  ##       if inputs['qqH']: counter+=1
##         if inputs['WH']:  counter+=1
##         if inputs['ZH']:  counter+=1
##         if inputs['ttH']: counter+=1
        
        return counter

    def numberOfBgChan(self,inputs):

        counter=0

        ##if inputs['ggZZ']:  counter+=1
        if inputs['qqZZ']:  counter+=1
        if inputs['ggZZbkg']:  counter+=1
        if inputs['zjets']: counter+=1
        if inputs['ttbar']: counter+=1
        if inputs['zbb']:   counter+=1
        
        return counter

