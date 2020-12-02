import ROOT
from ROOT import gROOT
c1 = ROOT.TCanvas( 'c1', 'Histogram Drawing Options', 200, 10, 700, 900 )
pad1=ROOT.TPad('pad1','pad',.03,.6,0.5,0.9,21)
f = ROOT.TFile('../paulsimmerl_analysis_code/q2w_hs.root')
pad1.Draw()
f.ls()
pad1.cd()
pad1.GetFrame().SetFillColor(18)
h = gROOT.FindObject('hq2w_sec1_proton')
h.SetFillColor(45)
h.Draw()
c1.Print('out.pdf')
