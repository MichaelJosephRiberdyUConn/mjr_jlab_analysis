import ROOT, sys, os, math

ROOT.gROOT.SetBatch()

ff =  ROOT.TFile('mon_EKKapKam_mon_skim4_005032.hipooct.6.20.root') #Opens data file
#ff =  ROOT.TFile('mon_EPPipPim_mon_skim4_005038.hipo1.root') #Opens data file
#ff =  ROOT.TFile('mon_EKKapKam_mon_skim4_005032.hipo1k.root') #Opens data file
#ff.ls()
#exit()
target = [8,9,"base stats"] #Action choice

legend = ROOT.TLegend(0.1,0.6,0.5,0.9) #Creates an object of TLegend class to use for histograms
legend.SetTextFont(72)
legend.SetTextSize(0.04)

hists = [] #A list for the generated histograms
fits_results = []
ls = [] #A list of legends associated with the histograms
background = []
peak = []

def write_list(file_object, L):
  for i in range(len(L)):
    file_object.write(str(L[i]) + "\n")
  

def fitf(x, par):
  sum1 = par[0]*math.exp(-0.5*((x[0]-par[1])/par[2])**2)
  l = len(par) 
  for i in range(3,l):
    sum1 += par[i]*x[0]**(i-3)
  return sum1

def gaussian(x, par):
  return par[0]*math.exp(-0.5*((x[0]-par[1])/par[2])**2)

def polynomial(x,par):
  sum = 0
  l = len(par)
  for i in range(l):
    sum += par[i]*x[0]**i
  return sum

def polynomial(x, par):
  sum1 = 0
  l = len(par)
  for i in range(l):
    sum1 += par[i]*x[0]**(i)
  return sum1

def generalized_gaussian(x, par):
  return par[0]*math.exp(-0.5*((math.fabs(x[0]-par[1])/par[2])**par[3])) * math.erf(par[4] * x[0])


def my_draw(hists, fits_results, background, peak, boundaries, remove_square_from_x_axis_label = 0): #A function to perform the fits and draw them
  hnum = len(hists)
  communication_number = 0  

  gaus_pol2 = ROOT.TF1("gaus_pol2", fitf, boundaries[0], boundaries[1], 5)
  if(remove_square_from_x_axis_label == 0):
    gaus_pol2.SetParameters(2600, 0, 0.1, 10, 10)
  else:
    gaus_pol2.SetParameters(2600, 0.95, 0.1, 10, 10)
  gaus_pol2.SetParLimits(4, 0, 1000)
  try:
    fits_results.append(hists[-1].Fit("gaus_pol2","S,Q", "", boundaries[0], boundaries[1]))
  except AttributeError:
    pass
  else:
    peak.append(ROOT.TF1("gaussian_part", gaussian, boundaries[0], boundaries[1], 3))
    try:
      peak[-1].SetParameters(fits_results[-1].Parameter(0), fits_results[-1].Parameter(1), fits_results[-1].Parameter(2))
    except ReferenceError:
      pass
    else:
      peak[-1].SetLineWidth(4)
      peak[-1].SetLineColor(ROOT.kGreen)
      background.append(ROOT.TF1("polynomial_part", polynomial, boundaries[0], boundaries[1], 2))
      background[-1].SetParameters(fits_results[-1].Parameter(3), fits_results[-1].Parameter(4))
      background[-1].SetLineWidth(4)
      background[-1].SetLineColor(ROOT.kMagenta)
      communication_number = 1

  axis_label = "MM2 (GeV^2)" if (remove_square_from_x_axis_label == 0) else "MM (GeV)"
  hists[-1].GetXaxis().SetTitle(axis_label) #This sets the x axis title  
  hists[-1].SetStats(0) #This removes the statistics from the histogram display (Things like the mean, median, etc. of the data will not be displayed)
  hists[-1].SetLineWidth(3)
  hists[-1].SetMinimum(0)
  hists[-1].Draw() #This displays the histogram

  peak[-1].Draw("same")
  background[-1].Draw("same")
  ls.append(ROOT.TLegend(.6,.6,.9,.9)) 
  ls[-1].SetTextFont(70)
  ls[-1].SetTextSize(0.03)
  ls[-1].AddEntry(hists[-1],           "Data",           "l") #This adds a legend entry for the histograms
  ls[-1].AddEntry(None,"#mu {:.5f}".format(fits_results[-1].Parameter(1))) #Adds legend entries to display the fit parameters of the gaussian
  ls[-1].AddEntry(None," #pm{:.5f} MeV".format(fits_results[-1].ParError(1)))
  ls[-1].AddEntry(None,"#sigma {:.5f}".format(fits_results[-1].Parameter(2)))
  ls[-1].AddEntry(None," #pm{:.5f} MeV".format(fits_results[-1].ParError(2)))
  ls[-1].Draw("same")
  print("mu:")
  print(fits_results[-1].Parameter(1))
  print("sigma:")
  print(fits_results[-1].Parameter(2))

if 2 in target:
  bounds = [[-0.1, 0.1], [-0.1, 0.1], [0.75, 1.05]]
  bounds += [[-0.1, 0.1], [-0.1, 0.1], [0.9, 1.05]]
  name_ls = ["mm2pip_FD", "mm2pim_FD", "mm2pro_FD"]
  name_ls += ["mm2pip_CD", "mm2pim_CD", "mm2pro_CD"]
  c2 = ROOT.TCanvas("all","all",2200,1600)
  c2.Divide(3,2)
  for hist_type in range(6):
    c2.cd(hist_type + 1)
    c2.SetGrid()
    hists.append(ff.Get(name_ls[hist_type]))
    if(str(type(hists[-1])) != "<class 'ROOT.TObject'>"):
      my_draw(hists, fits_results, background, peak, bounds[hist_type]) #option_number = 0 \equiv mm2, option_number = 1 \equiv invariant mass
  c2.Print("all_pi_events.pdf")
  
if 3 in target: #
  bounds = [[-0.1, 0.1], [-0.1, 0.1], [0.8, 1], [-0.1, 0.1], [-0.1, 0.1], [0.8, 1]]
  name_ls = ["mm2pip_FD", "mm2pim_FD", "mm2pro_FD", "mm2_pip_CD", "mm2pim_CD", "mm2pro_CD"]
  bounds += [[-0.1, 0.1], [-0.1, 0.1], [0.8, 1], [-0.1, 0.1], [-0.1, 0.1], [0.8, 1]]
  name_ls += ["mm2pip:in_FD", "mm2pim:in_FD", "mm2pro:in_FD", "mm2pip:in_CD", "mm2pim:in_CD", "mm2pro:in_CD"]
  cut_ls = ["", "in:"]
  c3 = ROOT.TCanvas("c3","c3",2200,1600)
  c3.Divide(3,2)
  for ele_status in range(2): #0=good,1=bad
    e_status = "_ele_good" if ele_status == 0 else "_ele_bad"
    for pip_status in range(2): #^
      p_status = "_pip_good" if pip_status == 0 else "_pip_bad"
      for f in range(4): #f = number of particles scattered forward
        f_str = "_f=" + str(f)
        name_string = f_str + e_status + p_status
        existence_count = 0
        for cut in range(2):
          for hist_type in range(6):
            hists.append(ff.Get(name_ls[cut * 6 + hist_type] + name_string))
            c3.cd(hist_type + 1)
            c3.SetGrid() 
            if(str(type(hists[-1])) != "<class 'ROOT.TObject'>"):
              existence_count += 1
              my_draw(hists, fits_results, background, peak, bounds[hist_type]) #option_number = 0 \equiv mm2, option_number = 1 \equiv invariant mass
          if(existence_count != 0):
            c3.Print("./cuthists_pi/by_number/" + cut_ls[cut] + name_string + ".pdf")

if 4 in target:
  bounds = [[-0.1, 0.1], [-0.1, 0.1], [0.8, 1]]
  name_ls = ["mm2pip", "mm2pim", "mm2pro"]
  bounds += [[-0.1, 0.1], [-0.1, 0.1], [0.8, 1]]
  name_ls += ["mm2pip:in", "mm2pim:in", "mm2pro:in"]
  c4 = ROOT.TCanvas("c4","c4",2200,1600)
  c4.Divide(3,2)
  for ele_status in range(2): #0=good,1=bad
    e_status = "_ele_good" if ele_status == 0 else "_ele_bad"
    for pip_status in range(2): #^
      p_status = "_pip_good" if pip_status == 0 else "_pip_bad"
      for pro in range(2):
        pro_label = "FD" if pro == 0 else "CD"
        for pip in range(2):
          pip_label = "FD" if pip == 0 else "CD"
          for pim in range(2):
            pim_label = "FD" if pim == 0 else "CD"
            name_string = "_pro:" + pro_label + "_pip:" + pip_label + "_pim:" + pim_label + e_status + p_status
            existence_count = 0
            for hist_type in range(6):
              c4.cd(hist_type+1) 
              c4.SetGrid()
              hists.append(ff.Get(name_ls[hist_type] + name_string))
              #option_number = 0 if (hist_type != 3) else 1
              if(str(type(hists[-1])) != "<class 'ROOT.TObject'>"):
                my_draw(hists, fits_results, background, peak, bounds[hist_type], remove_square_label_x_axis)
                existence_count += 1
            if(existence_count != 0):
              c4.Print("./cuthists_pi/by_particle/" + name_string + ".pdf")

if 5 in target: #
  name_ls = ["mm2pip_FD", "mm2pim_FD", "mm2pro_FD", "mm2_pip_CD", "mm2pim_CD", "mm2pro_CD"]
  name_ls += ["mm2pip:in_FD", "mm2pim:in_FD", "mm2pro:in_FD", "mm2pip:in_CD", "mm2pim:in_CD", "mm2pro:in_CD"]
  cut_ls = ["", "in:"]
  c3 = ROOT.TCanvas("c3","c3",2200,1600)
  c3.Divide(3,2)
  for ele_status in range(2): #0=good,1=bad
    e_status = "_ele_good" if ele_status == 0 else "_ele_bad"
    for pip_status in range(2): #^
      p_status = "_pip_good" if pip_status == 0 else "_pip_bad"
      for f in range(4): #f = number of particles scattered forward
        f_str = "_f=" + str(f)
        name_string = f_str + e_status + p_status
        existence_count = 0
        for cut in range(2):
          for hist_type in range(6):
            hists.append(ff.Get(name_ls[cut * 6 + hist_type] + name_string))
            c3.cd(hist_type + 1)
            c3.SetGrid() 
            if(str(type(hists[-1])) != "<class 'ROOT.TObject'>"):
              existence_count += 1
              hists[-1].SetStats(0)
              hists[-1].GetXaxis().SetTitle("MM2 (MeV)") #This sets the x axis title  
              hists[-1].SetLineWidth(3)
              hists[-1].Draw() #option_number = 0 \equiv mm2, option_number = 1 \equiv invariant mass
          if(existence_count != 0):
            c3.Print("./cuthists_pi/by_number/" + cut_ls[cut] + name_string + ".pdf")

if 6 in target:
  name_ls = ["mm2pip", "mm2pim", "mm2pro"]
  name_ls += ["mm2pip:in", "mm2pim:in", "mm2pro:in"]
  c4 = ROOT.TCanvas("c4","c4",2200,1600)
  c4.Divide(3,2)
  for ele_status in range(2): #0=good,1=bad
    e_status = "_ele_good" if ele_status == 0 else "_ele_bad"
    for pip_status in range(2): #^
      p_status = "_pip_good" if pip_status == 0 else "_pip_bad"
      for pro in range(2):
        pro_label = "FD" if pro == 0 else "CD"
        for pip in range(2):
          pip_label = "FD" if pip == 0 else "CD"
          for pim in range(2):
            pim_label = "FD" if pim == 0 else "CD"
            name_string = "_pro:" + pro_label + "_pip:" + pip_label + "_pim:" + pim_label + e_status + p_status
            existence_count = 0
            for hist_type in range(6):
              c4.cd(hist_type+1) 
              c4.SetGrid()
              hists.append(ff.Get(name_ls[hist_type] + name_string))
              #option_number = 0 if (hist_type != 3) else 1
              if(str(type(hists[-1])) != "<class 'ROOT.TObject'>"):
                hists[-1].SetStats(0)
                hists[-1].SetLineWidth(3)
                hists[-1].GetXaxis().SetTitle("MM2 (MeV)") #This sets the x axis title  
                hists[-1].Draw() #option_number = 0 \equiv mm2, option_number = 1 \equiv invariant mass
                existence_count += 1
            if(existence_count != 0):
              c4.Print("./cuthists_pi/by_particle/" + name_string + ".pdf")

if 7 in target:
  bounds = [[0.2, 0.4], [0.2, 0.4], [0.9, 1.05]]
  name_ls = ["mm2kap_FD", "mm2kam_FD", "mm2pro_FD"]
  c7 = ROOT.TCanvas("all","all",2200,1600)
  c7.Divide(3)
  for hist_type in range(3):
    print(name_ls[hist_type])
    c7.cd(hist_type + 1)
    c7.SetGrid()
    hists.append(ff.Get(name_ls[hist_type]))
    sq_op_num = 1 if (hist_type == 2) else 0
    #option_number = 0 if (hist_type != 3) else 1
    #my_draw(hists, fits_results, bounds[hist_type], option_number)
    if(str(type(hists[-1])) != "<class 'ROOT.TObject'>"):
      my_draw(hists, fits_results, background, peak, bounds[hist_type], sq_op_num)
      #hists[-1].SetStats(0)
      #hists[-1].SetLineWidth(3)
      #hists[-1].Draw()
      #print(name_ls[hist_type])
  c7.Print("kaon_primary.pdf")


if 8 in target: #
  name_ls = ["mm2kap_FD", "mm2kam_FD", "mm2pro_FD"]
  name_ls += ["mm2kap:in_FD", "mm2kam:in_FD", "mm2pro:in_FD"]
  cut_ls = ["", "in:"]
  c8 = ROOT.TCanvas("c8","c8",2200,1600)
  c8.Divide(3,2)
  for ele_status in range(2): #0=good,1=bad
    e_status = "_ele_good" if ele_status == 0 else "_ele_bad"
    for f in range(4): #f = number of particles scattered forward
      f_str = "_f=" + str(f)
      name_string = f_str + e_status
      existence_count = 0
      for cut in range(2):
        for hist_type in range(3):
          hists.append(ff.Get(name_ls[cut * 3 + hist_type] + name_string))
          c8.cd(hist_type + 1 + 3 * ele_status)
          c8.SetGrid() 
          if(str(type(hists[-1])) != "<class 'ROOT.TObject'>"):
            existence_count += 1
            hists[-1].SetStats(0)
            if(hist_type != 2):
              hists[-1].GetXaxis().SetTitle("MM2 (GeV^2)") #This sets the x axis title
            else:
              hists[-1].GetXaxis().SetTitle("MM (GeV)") #This sets the x axis title
            hists[-1].SetLineWidth(3)
            hists[-1].Draw() #option_number = 0 \equiv mm2, option_number = 1 \equiv invariant mass
        if(existence_count != 0):
          c8.Print("./cuthists_ka/by_number/" + cut_ls[cut] + name_string + ".pdf")

if 9 in target:
  name_ls = ["mm2kap", "mm2kam", "mm2pro"]
  name_ls += ["mm2kap:in", "mm2kam:in", "mm2pro:in"]
  c9 = ROOT.TCanvas("c9","c9",2200,1600)
  c9.Divide(3,2)
  for ele_status in range(2): #0=good,1=bad
    e_status = "_ele_good" if ele_status == 0 else "_ele_bad"
    for pro in range(2):
      pro_label = "FD" if pro == 0 else "CD"
      for kap in range(2):
        kap_label = "FD" if kap == 0 else "CD"
        for kam in range(2):
          kam_label = "FD" if kam == 0 else "CD"
          name_string = "_pro:" + pro_label + "_kap:" + kap_label + "_kam:" + kam_label + e_status
          existence_count = 0
          for hist_type in range(6):
            c9.cd(hist_type+1) 
            c9.SetGrid()
            hists.append(ff.Get(name_ls[hist_type] + name_string))
            #option_number = 0 if (hist_type != 3) else 1
            if(str(type(hists[-1])) != "<class 'ROOT.TObject'>"):
              hists[-1].SetStats(0)
              hists[-1].SetLineWidth(3)
              if(hist_type != 2):
                hists[-1].GetXaxis().SetTitle("MM2 (GeV^2)") #This sets the x axis title
              else:
                hists[-1].GetXaxis().SetTitle("MM (GeV)") #This sets the x axis title
              hists[-1].Draw() #option_number = 0 \equiv mm2, option_number = 1 \equiv invariant mass
              existence_count += 1
          if(existence_count != 0):
            c9.Print("./cuthists_ka/by_particle/" + name_string + ".pdf")

if "base stats" in target:
  stat_list = [0] * 6
  name_ls = ["mm2kap", "mm2kam", "mm2pro"]
  name_ls += ["mm2kap:in", "mm2kam:in", "mm2pro:in"]
  for ele_status in range(2): #0=good,1=bad
    e_status = "_ele_good" if ele_status == 0 else "_ele_bad"
    for pro in range(2):
      pro_label = "FD" if pro == 0 else "CD"
      for kap in range(2):
        kap_label = "FD" if kap == 0 else "CD"
        for kam in range(2):
          kam_label = "FD" if kam == 0 else "CD"
          name_string = "_pro:" + pro_label + "_kap:" + kap_label + "_kam:" + kam_label + e_status
          existence_count = 0
          for hist_type in range(6):
            c9.cd(hist_type+1) 
            c9.SetGrid()
            hists.append(ff.Get(name_ls[hist_type] + name_string))
            if(str(type(hists[-1])) != "<class 'ROOT.TObject'>"):
              stat_list[hist_type] += hists[-1].GetEntries()
  stat_file = open("kaon_event_information.txt","w+")
  stat_file.write("Number of protons passing the three sigma cut: " + str(stat_list[5]) + "\n")
  stat_file.write("Number of +kaons passing the three sigma cut: " + str(stat_list[3]) + "\n")
  stat_file.write("Number of -kaons passing the three sigma cut: " + str(stat_list[4]) + "\n")
  stat_file.write("Percentage of protons passing the three sigma cut: " + str(stat_list[5]/stat_list[2] * 100 if (stat_list[2] != 0) else + 0) + "\n")
  stat_file.write("Percentage of +kaons passing the three sigma cut: " + str(stat_list[3]/stat_list[0] * 100 if (stat_list[0] != 0) else + 0) + "\n")
  stat_file.write("Percentage of -kaons passing the three sigma cut: " + str(stat_list[4]/stat_list[1] * 100 if (stat_list[1] != 0) else + 0) + "\n")
  stat_file.close()
  
