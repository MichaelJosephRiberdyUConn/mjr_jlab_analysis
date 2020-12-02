import ROOT, sys, os, math

ROOT.gROOT.SetBatch()
#ROOT.gStyle.SetOptStat("")
#ROOT.gStyle.SetOptFit(0111)

ff =  ROOT.TFile('q2w_hs.root')#sys.argv[1]) #Opens data file

target = [2,3,4,5] #Here to make it easier to perform certain actions

#def fitf( x, par):
  #return par[0]*math.exp(-0.5*((x[0]-par[1])/par[2])**2)+par[3]+par[4]*x[0]+par[5]*(x[0]**2)
  #return self.background(x, par[3:])+self.gaussian(x, par[:3])
    
#def background(x, par):
  #return par[0]+par[1]*x[0]+par[2]*(x[0]**2)

#def gaussian(x, par):
  #return par[0]*math.exp(-0.5*((x[0]-par[1])/par[2])**2)
  #return par[0]/(par[2]*math.sqrt(2*math.pi))*math.exp(-0.5*((x[0]-par[1])/par[2])**2) #A set of 3 user-defined functions to fit

legend = ROOT.TLegend(0.1,0.6,0.5,0.9) #Creates an object of TLegend class to use for histograms
legend.SetTextFont(72)
legend.SetTextSize(0.04)

hists = [] #A list for the generated histograms
fits = [] #A list for the fits
pros = [] #A list for the gaussian proton peak fits
bgs = [] #A list for the background fits
ls = [] #A list of legends associated with the histograms

def my_draw(hists, fits, pros, bgs): #A function to perform the fits and draw them
  hnum = len(hists) #Counts the number of histograms
  fits.append(ROOT.TF1("fit"+str(hnum), fitf, 0.7, 1.1, 6)) #Creates an instance of function to be fit corresponding to each histogram. The fit happens only over the region [0.7,1.1]
  fits[-1].SetLineWidth(4) #Establishes the line width of the fit functions for when they are drawn

  pros.append(ROOT.TF1("pFit"+str(hnum), gaussian, 0.7, 1.1, 3)) #Creates a fit function instance of a gaussian 
  pros[-1].SetLineWidth(4) #Sets up how the fit is going to look by setting line width and color
  pros[-1].SetLineColor(ROOT.kMagenta)
  bgs.append(ROOT.TF1("bgFit"+str(hnum), background, 0.7, 1.1, 3)) #Creates polynomial of degree 2 fit function instance for each histogram
  bgs[-1].SetLineWidth(4) #Same as before
  bgs[-1].SetLineColor(ROOT.kGreen)

  if hnum > 16: #This decides how big the legends should be depending on how many histograms are going to be displayed
    ls.append(ROOT.TLegend(.1,.6,.4,.9)) #If there are more than 16 histograms to display the legends with the bottom left corners at (x,y)=(.1,.6) and top right corners at (.4,.9)
  else:
    ls.append(ROOT.TLegend(.1,.6,.5,.9)) #(0,0) is the bottom left corner of the plot, and (1,1) is the top right 
  ls[-1].SetTextFont(72)
  ls[-1].SetTextSize(0.04)

  hists[-1].GetXaxis().SetTitle("W (GeV)") #This sets the x axis title  
  hists[-1].SetStats(0) #This removes the statistics from the histogram display (Things like the mean, median, etc. of the data will not be displayed)
  hists[-1].SetLineWidth(3)

  fits[-1].SetParameters(100, 0.94, 0.1, 100, 1, 0) #This sets the fit parameters to be some certain initial values.  
  hists[-1].Fit(fits[-1], "R") #This fits the histograms in the list using a user-defined fit function defines 
  hists[-1].Draw() #This displays the fit on the histogram

  pars = fits[-1].GetParameters() #This collects the resulting parameters from the fit
  errs = fits[-1].GetParErrors() #This collects the errors of the resulting parameters from the fit
  pros[-1].SetParameters(pars[0],pars[1],pars[2]) #This sets the parameters of the proton peak fit to be the parameters from the fit just performed
  pros[-1].Draw("same") #"same" refers to drawing on the same canvas as was drawn on when we last called the Draw() function
  bgs[-1].SetParameters(pars[3],pars[4],pars[5])
  bgs[-1].Draw("same")

  ls[-1].AddEntry(hists[-1],           "Data",           "l") #This adds a legend entry for the histograms
  ls[-1].AddEntry(fits[-1],            "Global Fit",     "l") #Adds a legend entry for the total fits
  ls[-1].AddEntry(bgs[-1],         "Background Fit", "l") 
  ls[-1].AddEntry(pros[-1],     "Proton Fit",     "l") 
  ls[-1].AddEntry(None,"\mu {:.5f}".format(pars[1]), "") #Adds legend entry to display the fit parameters of the gaussian
  ls[-1].AddEntry(None," \pm{:.5f} GeV".format(errs[1]), "")
  ls[-1].AddEntry(None,"\sigma {:.5f}".format(pars[2]), "")
  ls[-1].AddEntry(None," \pm{:.5f} GeV".format(errs[2]), "")
  ls[-1].Draw() #Draws the legends
  

if 1 in target: #len(h1s) > 0: 
  h1s =[ff.Get("hq2w_sec"+str(sec)+"_q2bin"+str(q2bin)) for sec in range(1,7) for q2bin in range(10)] #Gets data listed under certain names in data file
  c1 = ROOT.TCanvas("c1","c1",2200,1600) #Creates and instance of ROoT::TCanvas
  c1.Divide(5,2) #Divides the canvas into 10 regions
  for sec in range(6): #
    #l1 = ROOT.TLegend(.75,.8,.95,.95)
    for i in range(10):
      #l1.AddEntry(h1s[sec*10+i], "Sector "+str(sec))
      c1.cd(i+1) #Changes which part of the canvas is being referenced
      h1s[sec*10+i].Fit("gaus","","",0.75,1.1) #Conducts fit
      h1s[sec*10+i].Draw("same") #Draws fit
      #l1.Draw()
      #h1s[sec*10+i].SetLineColor(sec)
  c1.Print("hists/out10h6s.pdf") #Exports histogram

if 2 in target: #len(h1s) > 0:
  c2 = ROOT.TCanvas("c2","c2",2200,1600)
  c2p = ROOT.TCanvas("c2p","c2p",2200,1600)
  c2.Divide(5,2)
  c2p.Divide(5,2)
  for i in range(10):
    hists.append(ff.Get("hq2w_q2bin"+str(i)))
    c2.cd(i+1)
    c2.SetGrid()
    my_draw(hists, fits, pros, bgs) #This code block uses the proton data specifically from the data file
    hists.append(ff.Get("hq2w_q2bin"+str(i)+"_proton"))
    c2p.cd(i+1)
    c2p.SetGrid()
    my_draw(hists, fits, pros, bgs)
  c2.Print("hists/out10h.pdf")
  c2p.Print("hists/out10h_proton.pdf")

if 3 in target: #len(h1s) > 0:
  c3 = ROOT.TCanvas("c3","c3",2200,1600)
  c3p = ROOT.TCanvas("c3p","c3p",2200,1600)
  c3.Divide(3,2)
  c3p.Divide(3,2)
  for sec in range(6):
    hists.append(ff.Get("hq2w_sec"+str(sec+1)))
    c3.cd(sec+1)
    c3.SetGrid()
    my_draw(hists, fits, pros, bgs)
    
    hists.append(ff.Get("hq2w_sec"+str(sec+1)+"_proton"))
    c3p.cd(sec+1)
    c3p.SetGrid()
    my_draw(hists, fits, pros, bgs)
  c3.Print("hists/out6s.pdf")
  c3p.Print("hists/out6s_proton.pdf")

if 4 in target: #len(h1s) > 0:
  c4 = ROOT.TCanvas("c4","c4",2750,2000)
  c4.cd()
  c4.SetGrid()

  hists.append(ff.Get("hq2w_complete"))
  my_draw(hists, fits, pros, bgs)  
  c4.Print("hists/out1h.pdf")

if 5 in target: #len(h1s) > 0:
  c5 = ROOT.TCanvas("c5","c5",2750,2000)
  c5.cd()
  c5.SetGrid()
  
  hists.append(ff.Get("hq2w_proton"))
  my_draw(hists, fits, pros, bgs) 
  c5.Print("hists/out_proton.pdf")


#raw_input("Waiting for key")
