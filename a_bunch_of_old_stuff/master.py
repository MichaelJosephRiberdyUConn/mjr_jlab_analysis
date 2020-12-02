import sys, os

data_list = ["4", "005038", "8", "005038", "4", "005032"]

sub_command_1 = " /cache/clas12/rg-a/production/recon/fall2018/torus-1/pass1/v0/dst/train/skim"
sub_command_2 = "/skim"
sub_command_3 = "_" 
sub_command_4 = ".hipo"

hipo_command = "run-groovy wvq2.groovy"
for i in range((len(data_list) / 2)):
  hipo_command += sub_command_1
  hipo_command += data_list[2 * i]
  hipo_command += sub_command_2
  hipo_command += data_list[2 * i]
  hipo_command += sub_command_3
  hipo_command += data_list[2 * i + 1]
  hipo_command += sub_command_4


os.chdir("/u/home/mjoer/paulsimmerl_analysis_code")
os.system("rm q2w_hs.root")
os.system(hipo_command)
os.chdir("/u/home/mjoer/example")
os.system("python2 my_run_wvq2.py")


