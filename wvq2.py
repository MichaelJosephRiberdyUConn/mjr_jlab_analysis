import ROOT, sys, os, math

ROOT.gROOT.SetBatch()

ff =  ROOT.TFile('../paulsimmerl_analysis_code/q2w_hs.root') #Opens data file
#print(ff.Map())
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
  sum1 = par[0]*math.exp(-0.5*((x[0]-par[1])/par[2])**2
  l = len(par) 
  for i in range(3,l):
    sum1 += par[i]*x**(i-3)
  return sum1

def my_draw(hists, fits, pros, bgs): #A function to perform the fits and draw them
  hnum = len(hists) #Counts the number of histograms


  boundary_range = 0.1 #The x coordinates of the boundaries of the region over which the fitting will occur can differ from their initial values by, at a maximum, this value 
  boundary_step = 0.01 #Boundary x coordinates differ by this value between trials
  boundary_left_init = 0.7 #Initial x coordinate of left boundary 
  boundary_right_init = 1.1 #Initial x coordinate of right boundary
  boundary_steps = int(2 * boundary_range / boundary_step) #The number of different options for each of the two boundary locations
  dummy_hist = hists[-1] #Making a copy of the current histogram as to not associate hundreds of fit functions with the original histogram (hists[-1])
  best_fit = dummy_hist.Fit("gauss") #Creating an initial fit whose form is completely unimportant 
  best_fit_info = []
  for l in range(boundary_steps): #Looping through left boundary options
    for r in range(boundary_steps): #Looping through right boundary options
      for order in range(1,5): #Looping through polynomials of different degrees, where 5 is an arbitrary cap on the degree
        #global best_fit #Accessing the fit currently stored
        #global best_fit_info 
        boundary_left = boundary_left_init - boundary_range + l * boundary_step #x coordinate of trial left boundary
        boundary_right = boundary_right_init - boundary_range + r * boundary_step #x coordinate of trial right boundary
        gauss_polN = ROOT.TF1("gauss_polN",fitf,boundary_left,boundary_right,3+order+1)
        loop_fit = dummy_hist.Fit("gauss_polN","S","",boundary_left,boundary_right) #Trial fit
        if loop_fit.Chi2() < best_fit.Chi2(): #Comparing the chi^2 values of the two fits
          best_fit = loop_fit #Only change the stored fit to the trial fit if the chi^2 value of the trial fit is lower than the current fit's chi^2 value 
          best_fit_info.clear()
          best_fit_info.extend([boundary_left, boundary_right, order]) #The boundary information and the degree of the polynomial are stored

  fits.append(best_fit) #Adds the best fit to the list of fits
  fits[-1].SetLineWidth(4) #Establishes the line width of the fit functions for when they are drawn

  pros.append(ROOT.TF1("pFit"+str(hnum), "gauss", best_fit_info[0], best_fit_info[1], 3)) #Creates a fit function instance of a gaussian with the proper boundary coordinates
  pros[-1].SetLineWidth(4) 
  pros[-1].SetLineColor(ROOT.kMagenta)
  gauss_pars = fits[-1].GetParameters() 
  del gauss_pars[3:len(gauss_pars)]
  pros[-1].SetParameters(gauss_pars) #Passes the gaussian parameters from the best fit to the gaussian fit

  bgs.append(ROOT.TF1("bgFit"+str(hnum), "pol"+str(best_fit_info[2]), best_fit_info[0], best_fit_info[1], best_fit_info[2] + 1)) #Creates polynomial of the degree of the best fit fit function instance for each histogram
  bgs[-1].SetLineWidth(4) 
  bgs[-1].SetLineColor(ROOT.kGreen)
  background_pars = fits[-1].GetParameters()
  del background_pars[0:2]
  bgs[-1].SetParameters(background_pars)

  if hnum > 16: #This decides how big the legends should be depending on how many histograms are going to be displayed
    ls.append(ROOT.TLegend(.1,.6,.4,.9)) #If there are more than 16 histograms to display the legends with the bottom left corners at (x,y)=(.1,.6) and top right corners at (.4,.9)
  else:
    ls.append(ROOT.TLegend(.1,.6,.5,.9)) #(0,0) is the bottom left corner of the plot, and (1,1) is the top right 
  ls[-1].SetTextFont(72)
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
  ls[-1].AddEntry(None," \pm{:.5f} GeV".format(fits[-1].ParError[1]))
  ls[-1].AddEntry(None,"\sigma {:.5f}".format(gauss_pars[2]))
  ls[-1].AddEntry(None," \pm{:.5f} GeV".format(fits[-1].ParErrors[2]))
  ls[-1].AddEntry(None,"Background Fit Polynomial Degree".format(best_fit_info[2]))
  ls[-1].AddEntry(None,"Background Fit \chi^{2}".format(fits[-1].Chi2()))
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
  #c2p = ROOT.TCanvas("c2p","c2p",2200,1600)
  c2.Divide(5,2)
  #c2p.Divide(5,2)
  for i in range(10):
    hists.append(ff.Get("hq2w_q2bin"+str(i)))
    c2.cd(i+1)
    c2.SetGrid()
    my_draw(hists, fits, pros, bgs) #This code block uses the proton data specifically from the data file
    
    #hists.append(ff.Get("hq2w_q2bin"+str(i)+"_proton"))
    #c2p.cd(i+1)
    #c2p.SetGrid()
    #my_draw(hists, fits, pros, bgs)
  c2.Print("hists/out10h.pdf")
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
    
    hists.append(ff.Get("hq2w_sec"+str(sec+1)+"_proton"))
    c3p.cd(sec+1)
    c3p.SetGrid()
    my_draw(hists, fits, pros, bgs)
  #c3.Print("hists/out6s.pdf")
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
