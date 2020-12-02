import ROOT, sys, os, math

ROOT.gROOT.SetBatch()

ff =  ROOT.TFile('../paulsimmerl_analysis_code/q2w_hs.root') #Opens data file
#print(ff.GetListOfKeys())
#exit()
#ff.ls()
#exit
target = [3] #Action choice

legend = ROOT.TLegend(0.1,0.6,0.5,0.9) #Creates an object of TLegend class to use for histograms
legend.SetTextFont(72)
legend.SetTextSize(0.04)

hists = [] #A list for the generated histograms
fits = [] #A list for the fits
pros = [] #A list for the gaussian proton peak fits
bgs = [] #A list for the background fits
ls = [] #A list of legends associated with the histograms

def fitf(x, par):
  sum1 = par[0]*math.exp(-0.5*((x[0]-par[1])/par[2])**2)
  l = len(par) 
  for i in range(3,l):
    sum1 += par[i]*x[0]**(i-3)
  return sum1

def poly(x, par):
  sum1 = 0
  l = len(par)
  for i in range(l):
    sum1 += par[i]*x[0]**(i)
  return sum1

def my_draw(hists, fits, pros, bgs): #A function to perform the fits and draw them
  hnum = len(hists) #Counts the number of histograms


  boundary_left = 0.7 #Initial x coordinate of left boundary 
  boundary_right = 1.1 #Initial x coordinate of right boundary
  dummy_hist = hists[-1] #Making a copy of the current histogram as to not associate hundreds of fit functions with the original histogram (hists[-1])
  best_fit = dummy_hist.Fit("gaus","S,Q") #Creating an initial fit whose form is completely unimportant
  param_vec = [200,0.9,1] 
  degree = 0
  for iteration in range(2):
    for order in range(1,3): #Looping through polynomials of different degrees, where 5 is an arbitrary cap on the degre
      gauss_polN = ROOT.TF1("gauss_polN",fitf,boundary_left,boundary_right,3+order+1)
      zeroes = [0] * (order + 1)
      gauss_polN.SetParameters(*(param_vec+zeroes))
      gauss_polN.SetParLimits(0,100,300)
      gauss_polN.SetParLimits(1,0.8,1.2)
      gauss_polN.SetParLimits(3,0.04,0.06) 
      loop_fit = dummy_hist.Fit("gauss_polN","S,Q","",boundary_left,boundary_right) #Trial fit
      if loop_fit.Chi2() < best_fit.Chi2():
        best_fit = loop_fit 
        degree = order
        param_vec2 = gauss_polN.GetParameters()
        boundary_left = max(param_vec2[1] - 4 * abs(param_vec2[2]),0.7) 
        boundary_right = min(param_vec2[1] + 4 * abs(param_vec2[2]),1.1)
        print(param_vec2[1])
        print(param_vec2[2])
  
  #exit()     
  fits.append(gauss_polN) #Adds the best fit to the list of fits
  fits[-1].SetLineWidth(4) #Establishes the line width of the fit functions for when they are drawn

  pros.append(ROOT.TF1("pFit"+str(hnum), "gaus", boundary_left, boundary_right, 3)) #Creates a fit function instance of a gaussian with the proper boundary coordinates
  pros[-1].SetLineWidth(4) 
  pros[-1].SetLineColor(ROOT.kMagenta)
  gauss_pars = fits[-1].GetParameters()
  pros[-1].SetParameters(gauss_pars[0], gauss_pars[1], gauss_pars[2]) #Passes the gaussian parameters from the best fit to the gaussian fit

  bgs.append(ROOT.TF1("bgFit"+str(hnum), poly, boundary_left, boundary_right, degree + 1)) #Creates polynomial of the degree of the best fit fit function instance for each histogram
  bgs[-1].SetLineWidth(4) 
  bgs[-1].SetLineColor(ROOT.kGreen)
  background_pars = fits[-1].GetParameters()
  x = []
  for i in range(degree + 1):
    x.append(background_pars[i+3])
  #for i in range(len(x)):
  #  print(x[i])
  bgs[-1].SetParameters(*x)

  if hnum > 16: #This decides how big the legends should be depending on how many histograms are going to be displayed
    ls.append(ROOT.TLegend(.1,.6,.5,.9)) #If there are more than 16 histograms to display the legends with the bottom left corners at (x,y)=(.1,.6) and top right corners at (.4,.9)
  else:
    ls.append(ROOT.TLegend(.1,.6,.5,.9)) #(0,0) is the bottom left corner of the plot, and (1,1) is the top right 
  ls[-1].SetTextFont(70)
  ls[-1].SetTextSize(0.04)

  hists[-1].GetXaxis().SetTitle("W (GeV)") #This sets the x axis title  
  hists[-1].SetStats(0) #This removes the statistics from the histogram display (Things like the mean, median, etc. of the data will not be displayed)
  hists[-1].SetLineWidth(3)

  hists[-1].Draw() #This displays the histogram
  fits[-1].Draw("same") #The associated fits are displayed in these three lines
  pros[-1].Draw("same")
  bgs[-1].Draw("same")

  ls[-1].AddEntry(hists[-1],           "Data",           "l") #This adds a legend entry for the histograms
  ls[-1].AddEntry(fits[-1],            "Global Fit",     "l") #Adds a legend entry for the total fits
  ls[-1].AddEntry(bgs[-1],         "Background Fit", "l") 
  ls[-1].AddEntry(pros[-1],     "Proton Fit",     "l") 
  ls[-1].AddEntry(None,"\mu {:.5f}".format(gauss_pars[1])) #Adds legend entries to display the fit parameters of the gaussian
  ls[-1].AddEntry(None," \pm{:.5f} GeV".format(best_fit.ParError(1)))
  ls[-1].AddEntry(None,"\sigma {:.5f}".format(gauss_pars[2]))
  ls[-1].AddEntry(None," \pm{:.5f} GeV".format(best_fit.ParError(2)))
  ls[-1].AddEntry(None,"BG Poly Fit Degree =".format(degree))
  ls[-1].AddEntry(None,"Q^{2} range of fits: [" + str(boundary_left) + "," + str(boundary_right) + "]")
  ls[-1].Draw() #Draws the legend
  

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
  #c2p = ROOT.TCanvas("c2p","c2p",2200,1600)
  c2.Divide(5,2)
  #2p.Divide(5,2)
  for i in range(10):
    hists.append(ff.Get("hq2w_q2bin"+str(i)))
    c2.cd(i+1)
    c2.SetGrid()
    my_draw(hists, fits, pros, bgs) #This code block uses the proton data specifically from the data file
    
    #hists.append(ff.Get("hq2w_q2bin"+str(i)+"_proton"))
    #c2p.cd(i+1)
    #c2p.SetGrid()
    #my_draw(hists, fits, pros, bgs)
  c2.Print("out10h.pdf")
  #c2p.Print("hists/out10h_proton.pdf")

if 3 in target: #len(h1s) > 0:
  #c3 = ROOT.TCanvas("c3","c3",2200,1600)
  c3p = ROOT.TCanvas("c3p","c3p",2200,1600)
  #c3.Divide(3,2)
  c3p.Divide(3,2)
  for sec in range(6):
    #hists.append(ff.Get("hq2w_sec"+str(sec+1)))
    #c3.cd(sec+1)
    #c3.SetGrid()
    #my_draw(hists, fits, pros, bgs)
    
    print("sec="+str(sec))
    hists.append(ff.Get("hq2w_sec"+str(sec+1)+"_proton"))
    #print("hq2w_sec"+str(sec+1)+"_proton")
    c3p.cd(sec+1)
    c3p.SetGrid()
    my_draw(hists, fits, pros, bgs)
  #c3.Print("hists/out6s.pdf")
  c3p.Print("out6s_proton_2.pdf")

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
