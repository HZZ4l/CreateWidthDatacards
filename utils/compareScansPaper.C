void compareScansPaper(){
  gStyle->SetOptTitle(0);
  TString sets[7]={"1DDgg","1Dm4l","4l","2l2n","incl","All","Combined"};
   for(int is=0;is<6;is++){
     for(int in=2;in<4;in++){
       compare(sets[is].Data(),in,false);
       if(in==2 && is>1)compare(sets[is].Data(),in,true);
       if(is>1)compare(sets[is].Data(),in,false,true);
     }
   }
  
//   for(int is=2;is<6;is++){
//     for(int in=2;in<4;in++){
//       compare(sets[is].Data(),in,false,true);
//     }
//   }
//   compare("incl",2,false,false);
//   compare("incl",3,false,false);
//   compare("All",2,false,false);
//   compare("All",3,false,false);

//   compare("incl",2,true,false);
//   compare("All",2,true,false);

//   compare("All",2,false,false);
//   compare("All",2,false,true);
//   compare("All",3,false,false);
//   compare("All",3,false,true);

//   compare("2l2n",2,false,false);
//   compare("2l2n",2,false,true);
//   compare("2l2n",3,false,false);
//   compare("2l2n",3,false,true);

}

void compare(TString set="All", int nFiles=9, bool lowR=false, bool up120=false){

  //TString files[]={"/afs/cern.ch/work/c/chmartin/public/7and8TeVwidth/HCG/220/","/afs/cern.ch/work/c/chmartin/public/7and8TeVwidth/HCG/220/","/afs/cern.ch/work/c/chmartin/public/7and8TeVwidth/HCG/only2l2nu/","/afs/cern.ch/work/c/chmartin/public/7and8TeVwidth/HCG/only2l2nu/","/afs/cern.ch/work/c/chmartin/public/7and8TeVwidth/HCG/220_2l2nu/","/afs/cern.ch/work/c/chmartin/public/7and8TeVwidth/HCG/220_2l2nu/"};
  TString dir = "cards_Paper_V3/HCG/220/";
  TString files[]={"4l","4l","4l","2l2n","2l2n","2l2n","incl","incl","incl","Combined","Combined","Combined"};
  int colors[] = {kRed+3,kRed+3,kRed+3,kRed-3,kRed-3,kRed-3,kBlue+1,kBlue+1,kBlue+1,kGreen+2,kGreen+2,kGreen+2};
  //int colors[] = {kRed,kRed,kRed,kAzure+10,kAzure+10,kAzure+10,kBlack,kBlack,kBlack,kGreen+2,kGreen+2,kGreen+2};
  TString grnames[]={"4#font[12]{l} observed","4#font[12]{l} expected","4#font[12]{l} no systematics","2#font[12]{l}2#nu + 4#font[12]{l}_{on-shell} observed","2#font[12]{l}2#nu + 4#font[12]{l}_{on-shell} expected","2#font[12]{l}2#nu + 4#font[12]{l}_{on-shell} no systematics","Combined ZZ observed","Combined ZZ expected","Combined ZZ no systematics"};
  int obs[] = {1,0,-1,1,0,-1,1,0,-1,1,0,-1,1,0,-1,0,1,0,1,0,1,0};
  double mass[] = {125.6,125.6,125.6,125.6,125.6,125.6,125.6,125.6,125.6,125.6,125.6,125.6};
  int maxwidth = 16.0;
  //int maxwidth = 30.0;
  //int maxwidth = 2.0;
  float upLim =10.5;
  bool mev=true;
  TString outString = "FitPaper_30_04_14";//"03_17_2DchanExp_093";
  outString.Prepend(set.Data());

  if(lowR){
    for(int il=0;il<9;il++)files[il].Append("lowR");
    mev=false;
    outString.Append("_lowR");
    maxwidth=2.0;
  }

  if(set=="1Dm4l"){
    maxwidth = 30.0;
    dir = "cards_Paper_V3_1Dm4l/HCG/220/";
    grnames[0]="4#font[12]{l}(m_{4#font[12]{l}}) observed";
    grnames[1]="4#font[12]{l}(m_{4#font[12]{l}}) expected";
    grnames[2]="4#font[12]{l}(m_{4#font[12]{l}}) no systematics";
  }

  if(set=="1DDgg"){
    maxwidth = 30.0;
    dir = "cards_Paper_V3_1DDgg/HCG/220/";
    grnames[0]="4#font[12]{l}(D_{gg}) observed";
    grnames[1]="4#font[12]{l}(D_{gg}) expected";
    grnames[2]="4#font[12]{l}(D_{gg}) no systematics";
  }

  if(set=="All")nFiles=nFiles*3;

  if(set=="2l2n"){
    for(ill=0;ill<3;ill++){
      files[ill]=files[ill+3];
      grnames[ill]=grnames[ill+3];
      colors[ill]=colors[ill+3];
    }
  }

  if(set=="incl"){
    for(ill=0;ill<3;ill++){
      files[ill]=files[ill+6];
      grnames[ill]=grnames[ill+6];
      colors[ill]=colors[ill+6];
    }
  }

  if(set=="Combined"){
    for(ill=0;ill<3;ill++){
      files[ill]=files[ill+9];
      grnames[ill]=grnames[ill+9];
      colors[ill]=colors[ill+9];
    }
  }

  if(nFiles==6){
    files[2]=files[3];
    files[4]=files[6];
    files[5]=files[6];
    colors[2]=colors[3];
    colors[4]=colors[6];
    colors[5]=colors[6];
    obs[2]=1;
    obs[3]=0;
    obs[4]=1;
    obs[5]=0;
    grnames[2]=grnames[3];
    grnames[3]=grnames[4];
    grnames[4]=grnames[6];
    grnames[5]=grnames[7];
  }

  if(nFiles==9 || nFiles == 3)outString.Append("_noSyst");

  if(up120){
    maxwidth=30;
    outString.Append("_120");
    upLim =20.0;
  }

  const int nfiles = nFiles;

  TString plotLabel = "CMS";

  //TString toyPlotname = "toyParallel2D_093_95/toPlot.root";
  //TFile toyPlotFile = "toPlot";

  //tell this flag which are obsered
  //int obs[] = {0,1,-1,0,1,-1,0,1,-1,0,-1,1,0,1,0,1,0,1,0,1,0};
  bool printpval=false;
  bool uncBand =false;
  bool toyPlot =false;
  if(uncBand)toyPlot=false;


  //values for 1DDgg_093, expected mu=0.93
  //double limits95[]={6.05994,7.97529,12.1601,18.8235,26.9906};
  //double limits68[]={2.40192,3.22084,5.71285,10.862,16.2785};
  //values for 1Dm4l_093, expected mu=0.93
  //double limits95[]={ 8.00674,10.8502,16.7568,26.2496,35.4528};
  //double limits68[]={3.09662,4.28213,7.78485,14.8901,22.1333 }:
  //values for 2D_093, expected mu=0.93
  double limits95[]={ 5.01781,6.99495,10.6292,17.0564,24.4662};
  double limits68[]={ 1.65029,2.7713,4.90192,9.99193,15.0928 };
  //values for 4l+2l2n Combination (from Chris)
  //double limits95[]={4.382,5.973,9.09,13.879,18.823};
  //double limits68[]={1.594,2.567,4.925,8.409,11.752};

  // gROOT->ProcessLine(".x tdrstyle.cc");
  gStyle->SetPadLeftMargin(0.16);
  gStyle->SetPadTopMargin(0.09);
  float gglimit = float(maxwidth);

  TGraph *g[nfiles];

  TLegend *leg = new TLegend(0.16,0.63,0.54,0.90);
  //TLegend *leg = new TLegend(0.18,0.55,0.5,0.93);
  //TLegend *leg = new TLegend(0.55,0.41,0.81,0.71);
  //leg->SetX1(0.22);
  //leg->SetX2(0.5);
  //leg->SetY1(0.7);
  //leg->SetY2(0.93);
  leg->SetFillColor(0);
  leg->SetLineColor(0);
  leg->SetBorderSize(0);
  // leg->SetMargin(0.05);
  leg->SetFillStyle(0);
  leg->SetTextFont(42);
  // TLegendEntry *tentry = leg->AddEntry((TObject*)0,plotLabel.Data(),"");
  // tentry->SetTextSize(0.04);
  // tentry->SetTextFont(42);
  // leg->AddEntry((TObject*)0, "","");

  double limitObs =0;

  if(mev){
    for (int imev=0;imev<5;imev++){
      limits95[imev]=limits95[imev]*4.15;
      limits68[imev]=limits68[imev]*4.15;
    }
    maxwidth=maxwidth*4.15;
    outString+="_MeV";
    gglimit*=4.15;
  }

  for(int i=0;i<nfiles;i++){
    char boh[200];
    //printf("%d\n",i);
    //if(i==3)mass=240;
    //TString filepath;filepath.Form("HCG/%d/",mass);
    TString obsString = "Exp";
    //if(i)obsString="NoSyst";
    if(obs[i])obsString="Obs";
    if(obs[i]<0)obsString="ExpNoSyst";
    int nDi =2;
    //printf("%d\n",i);
    sprintf(boh,"%shiggsCombine%s_%s_nLL_scan.MultiDimFit.mH%.1f.root", dir.Data(),obsString.Data(),files[i].Data(),mass[i]);
    TFile *f1=TFile::Open(boh);
    TTree *t1=(TTree*)f1->Get("limit");
    t1->Draw("2*deltaNLL:CMS_zz4l_GGsm", "deltaNLL > 0","PL");
    TGraph *gr0 = (TGraph*)gROOT->FindObject("Graph")->Clone();
    if(!lowR && !set.Contains("1D") && !set.Contains("2l")){
      sprintf(boh,"%shiggsCombine%s_%slowR_nLL_scan.MultiDimFit.mH%.1f.root", dir.Data(),obsString.Data(),files[i].Data(),mass[i]);
      TFile *f2=TFile::Open(boh);
      TTree *t2=(TTree*)f2->Get("limit");
      t2->Draw("2*deltaNLL:CMS_zz4l_GGsm", "deltaNLL > 0","PL");
      TGraph *grlow = (TGraph*)gROOT->FindObject("Graph")->Clone();
      int norig = gr0->GetN();
      gr0->Set(gr0->GetN()+grlow->GetN());
      double *ylow=grlow->GetY();
      double *xlow=grlow->GetX();
      for(int ipoint=0;ipoint<grlow->GetN();ipoint++)gr0->SetPoint(norig+ipoint,xlow[ipoint],ylow[ipoint]);
    }
    gr0->Sort();
    TString name;name.Format("%s_%d",grnames[i].Data(),i);
    gr0->SetName(name.Data());
    gr0->SetLineWidth(2);
    if ((files[i]=="Combined"||files[i]=="incl") && i> 3) gr0->SetLineWidth(3);
    //if(files[i]=="2l2n"&& nfiles>3)gr0->SetLineWidth(1);
    //else gr0->SetLineWidth(2);
    gr0->SetLineColor(colors[i]);
    if(obs[i]==0) gr0->SetLineStyle(2);
    if(obs[i]==-1) gr0->SetLineStyle(10);
    //if(files[i]=="2l2n" && obs[i]==1){gr0->RemovePoint(95);gr0->RemovePoint(94);gr0->RemovePoint(94);}//gr0->Print();}
    //if(files[i]=="Combined" && obs[i]==1){gr0->RemovePoint(93);}//gr0->Print();}
    //if(i==1) { 
    //gr0->Print();
      //gr0->RemovePoint(86);
    //}
    // else if (i == 2)gr0->SetLineStyle(2);
    // else if (i == 3)gr0->SetLineStyle(10);
    int nPoints = gr0->GetN();
    double *y = gr0->GetY();
    for(int j=0;j<nPoints;j++){
      if(y[j]<4)continue;
      if(y[j]<=y[j-1]){
	gr0->RemovePoint(j);
	j--;
	nPoints--;
      }
    }
    gr0->SetTitle(grnames[i].Data());
    leg->AddEntry(gr0);
    //gr0->SetTitle(gr0->GetName());
    g[i]=(TGraph*)gr0->Clone();
    double *y = gr0->GetY();
    double *x = gr0->GetX();
    int ipol=-1,ipol68=-1;
    for(int ipo=0;ipo<gr0->GetN();ipo++){
      if(y[ipo]<3.84&&y[ipo+1]>3.84){
	ipol = ipo;
	//printf("ipo %f\n",ipo);
      }
      if(y[ipo]<1&&y[ipo+1]>1){
	ipol68 = ipo;
      }
      if(mev)g[i]->SetPoint(ipo,x[ipo]*4.15,y[ipo]);
    }
    double fact=1;
    if(mev)fact=4.15;
    double a =  (y[ipol+1]-y[ipol])/(x[ipol+1]-x[ipol])/fact;
    double b = y[ipol]-a*x[ipol]*fact;
    if(obs[i] && limitObs<1)limitObs=(3.84-b)/a;
    printf("%s limit@95CL %.2f\n",grnames[i].Data(),(3.84-b)/a);
    a =  (y[ipol68+1]-y[ipol68])/(x[ipol68+1]-x[ipol68])/fact;
    b = y[ipol68]-a*x[ipol68]*fact;
    printf("%s limit@68CL %.2f\n",grnames[i].Data(),(1-b)/a);
  }


  //  leg->AddEntry(gr0, "Expected - no Syst","l");
  //  leg->AddEntry(gr1, "Expected","l");
  //  leg->Draw();

  float lumi7TeV=5.1;
  float lumi8TeV=19.7;

  //TFile *fToy = TFile::Open(toyPlotname.Data());
  //TCanvas *cToy = fToy->Get("toPlot");
  //TH1F *htoy = (TH1F*)toPlot->FindObject("Toys");

  TCanvas *c1=new TCanvas("can1","CANVAS-SCAN1D",800,800);
  c1->SetBottomMargin(0.13);
  c1->Range(0,0,1,1);
  c1->SetFillColor(0);
  c1->SetBorderMode(0);
  c1->SetBorderSize(2);
  c1->SetLeftMargin(0.16);
  c1->SetFrameBorderMode(0);
  c1->cd();
  g[0]->Draw("AL");
  g[0]->GetXaxis()->SetTitle("#Gamma/#Gamma_{SM}");
  if(mev)  g[0]->GetXaxis()->SetTitle("#Gamma_{H} (MeV)");
  g[0]->GetXaxis()->SetTitleOffset(1.05);
  g[0]->GetYaxis()->SetTitle("-2 #Delta lnL");
  g[0]->GetYaxis()->SetTitleSize(0.05);
  g[0]->GetXaxis()->SetTitleSize(0.05);
  g[0]->GetXaxis()->SetLabelSize(0.04);
  g[0]->GetYaxis()->SetLabelSize(0.04);
  if(gglimit<10)upLim=1.01;
  g[0]->GetYaxis()->SetRangeUser(0.,upLim);//12
  g[0]->GetXaxis()->SetRangeUser(0.,gglimit);

  if(uncBand){
    TLine *l2_95=new TLine();
    //l2_95->SetLineStyle(9);
    l2_95->SetLineWidth(20);
    l2_95->SetLineColor(kYellow);
    l2_95->DrawLine(limits95[0],3.84,TMath::Min(limits95[4],gglimit),3.84);
    l2_95->Draw();
    
    TLine *l2_68=new TLine();
    //l2_68->SetLineStyle(9);
    l2_68->SetLineWidth(20);
    l2_68->SetLineColor(kGreen);
    l2_68->DrawLine(limits95[1],3.84,limits95[3],3.84);
    l2_68->Draw("same");
   
    TLine *l1_95=new TLine();
    //l1_95->SetLineStyle(9);
    l1_95->SetLineWidth(20);
    l1_95->SetLineColor(kYellow);
    l1_95->DrawLine(limits68[0],1,TMath::Min(limits68[4],gglimit),1);
    l1_95->Draw("same");

    TLine *l1_68=new TLine();
    //l1_68->SetLineStyle(9);
    l1_68->SetLineWidth(20);
    l1_68->SetLineColor(kGreen);
    l1_68->DrawLine(limits68[1],1,limits68[3],1);
    leg->AddEntry(l1_68,"68% CL","l");
    leg->AddEntry(l1_95,"95% CL","l");
    l1_68->Draw("same");

  }
//   //p-value 0.13;
  if(printpval){
    TPaveText *pval = new TPaveText(0.54,0.35,0.85,0.45,"brNDC");
    pval->SetBorderSize(0);
    pval->SetTextAlign(12);
    pval->SetFillStyle(0);
    pval->SetTextFont(42);
    pval->SetTextSize(0.03);
    pval->AddText(0,0,"p-value @ 95%CL = 0.12");
    pval->Draw();
  }

  TPaveText *cll = new TPaveText(0.74,0.39,0.98,0.47,"brNDC");
  cll->SetBorderSize(0);
  cll->SetTextAlign(12);
  cll->SetFillStyle(0);
  cll->SetTextFont(42);
  cll->SetTextSize(0.03);
  cll->AddText(0,0,"95% CL");
  if(gglimit>10)cll->Draw();

  TPaveText *cll2 = new TPaveText(0.74,0.19,0.98,0.25,"brNDC");
  cll2->SetBorderSize(0);
  cll2->SetTextAlign(12);
  cll2->SetFillStyle(0);
  cll2->SetTextFont(42);
  cll2->SetTextSize(0.03);
  cll2->AddText(0,0,"68% CL");
  if(gglimit>10)cll2->Draw();

  TPaveText *hzz = new TPaveText(0.20,0.50,0.28,0.60,"brNDC");
  hzz->SetBorderSize(0);
  hzz->SetTextAlign(12);
  hzz->SetFillStyle(0);
  hzz->SetTextFont(42);
  hzz->SetTextSize(0.05);
  hzz->AddText(0,0,"H #rightarrow ZZ");
  hzz->Draw();


   pt = new TPaveText(0.15,0.8857692,0.85,0.995,"blNDC");
   pt->SetBorderSize(0);
   pt->SetFillStyle(0);
   pt->SetTextAlign(12);
   pt->SetTextFont(42);
   pt->SetTextSize(0.04);
   text = pt->AddText(0.02,0.45,"#font[42]{CMS}");
   text->SetTextFont(62);
   text->SetTextSize(0.044);
   text = pt->AddText(0.47,0.45,"#font[42]{19.7 fb^{-1} (8 TeV) + 5.1 fb^{-1} (7 TeV)}");
   text->SetTextFont(62);
   text->SetTextSize(0.03146853);
   pt->Draw();


//    pt = new TPaveText(0.1492308,0.9076433,0.9492308,0.9761146,"brNDC");
//    pt->SetBorderSize(0);
//    pt->SetFillStyle(0);
//    pt->SetTextAlign(12);
//    pt->SetTextFont(42);
//    //pt->SetTextSize(0.03);
//    text = pt->AddText(0.02,0.45,"#font[42]{CMS}");
//    text = pt->AddText(0.4,0.45,"#font[42]{L = 19.7 fb^{-1} (8 TeV) + 5.1 fb^{-1} (7 TeV)}"); 
//    //text = pt->AddText(0.01,0.6,"CMS");
//    //text->SetTextFont(62);
//    //text->SetTextSize(0.03946853);
//    //text = pt->AddText(0.2,0.6,"#sqrt{s} = 7 TeV, L = 5.1 fb^{-1}  #sqrt{s} = 8 TeV, L = 19.7 fb^{-1}");
//    //text->SetTextFont(62);
//    //text->SetTextSize(0.03146853);
//    pt->Draw();



//   TPaveText *pt = new TPaveText(0.1577181,0.9062937,0.9580537,0.9747552,"brNDC");
//   pt->SetBorderSize(0);
//   pt->SetTextAlign(12);
//   pt->SetFillStyle(0);
//   pt->SetTextFont(42);
//   pt->SetTextSize(0.03);
//   //TText *text = pt->AddText(0.01,0.5,"CMS Preliminary");
//   TText *text = pt->AddText(0.01,0.6,"CMS");
//   text->SetTextFont(62);
//   text->SetTextSize(0.03946853);
//   text = pt->AddText(0.20,0.6,Form("#sqrt{s} = 7 TeV, L = %.1f fb^{-1}  #sqrt{s} = 8 TeV, L = %.1f fb^{-1}",lumi7TeV,lumi8TeV));
//   //text = pt->AddText(0.5,0.5,Form("#sqrt{s} = 8 TeV, L = %.1f fb^{-1}",lumi8TeV));
//   text->SetTextFont(62);
//   text->SetTextSize(0.03146853);
//   pt->Draw();  

  TPaveText *oneSig = new TPaveText(0.85,0.18,0.9,0.22,"NDC");
  oneSig->SetFillColor(0);
  oneSig->SetTextFont(42);
  oneSig->SetTextColor(kRed);
  oneSig->SetBorderSize(0);
  oneSig->AddText("1#sigma"); 
  //  oneSig->Draw();

  TPaveText *twoSig = new TPaveText(0.85,0.44,0.9,0.48,"NDC");
  twoSig->SetFillColor(0);
  twoSig->SetTextFont(42);
  twoSig->SetTextColor(kRed);
  twoSig->SetBorderSize(0);
  twoSig->AddText("2#sigma"); 
  //  twoSig->Draw();

  TLine *l1=new TLine();
  l1->SetLineStyle(9);
  l1->SetLineWidth(1);
  l1->SetLineColor(kBlack);
  l1->DrawLine(0.0,1.0,gglimit,1.0);
  l1->Draw("same");
  TLine *l2=new TLine();
  l2->SetLineStyle(9);
  l2->SetLineWidth(1);
  l2->SetLineColor(kBlack);
  l2->DrawLine(0.0,3.84,gglimit,3.84);
  l2->Draw("same");

  for(int i=0;i<nfiles;i++)g[i]->Draw("LSAME");
  leg->SetFillStyle(0);
  leg->Draw("SAME");

  if(uncBand){
    TGraph *medians = new TGraph(2);
    medians->SetPoint(0,limits95[2],3.84);
    medians->SetPoint(1,limits68[2],1.0);
    medians->SetFillStyle(0);
    medians->SetMarkerStyle(30);
    medians->SetMarkerSize(1.5);
    medians->SetMarkerColor(kBlue);
    medians->SetLineColor(0);
    //medians->Draw("PSAME");  
    //leg->AddEntry(medians,"Expected median","p");
  }
  if(toyPlot){
    TPad *p = new TPad("p","p",0.6,4.5/12.0,0.9,7.3/12.0);
    p->SetMargin(0.05,0,0.05,0);
    p->Draw();
    p->cd();
    htoy->SetStats(0);
    htoy->Draw();
    //TText *pvalt = new TText(limitObs+1,20,"p-value @ 95%CL = 0.12");
    TText *pvalt = new TText(12,200,"p-value @ 95%CL = 0.12");
    pvalt->SetTextSize(0.08);
    TArrow *ar2 = new TArrow(limitObs,0.0,limitObs,htoy->GetBinContent(htoy->FindBin(limitObs)),0.02,"<|");
    ar2->SetAngle(30);
    ar2->Draw();  
    pvalt->Draw();
  }

  TString saveString;
  saveString.Form("%s.C",outString.Data());
  c1->SaveAs(saveString.Data());
  //saveString.Form("%s.gif",outString.Data());
  //c1->SaveAs(saveString.Data());
  saveString.Form("%s.eps",outString.Data());
  c1->SaveAs(saveString.Data());
  saveString.Form("%s.pdf",outString.Data());
  c1->SaveAs(saveString.Data());
  saveString.Form("%s.png",outString.Data());
  c1->SaveAs(saveString.Data());
  saveString.Form("%s.root",outString.Data());
  c1->SaveAs(saveString.Data());

}
