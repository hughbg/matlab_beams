import numpy as np
from collections import OrderedDict
import os, sys


rhino_params = OrderedDict()

rhino_params["FlareWidth"] = 2.3
rhino_params["Width"] = 0.5
rhino_params["FeedWidth"] = 0.04
rhino_params["FlareHeight"] = 2.3
rhino_params["Height"] = 0.5 
rhino_params["FeedHeight"] = 0.25 
rhino_params["FlareLength"] = 2.9
rhino_params["Length"] = 0.4
rhino_params["FeedOffset0"] = -0.05
rhino_params["FeedOffset1"] = 0 

os.system("rm examine_param_*.zip")

# For each param
for i, p in enumerate(rhino_params.values()):
    
    if i < 8:    # Vary by percentage
        vals = np.linspace(p-p*0.8, p+p*0.8, num=11)
    else:
        vals = np.linspace(-0.25, 0.25, num=11)


    # Generate a range of vals for this param, and dump the sets in a file
    f = open("examine_params_effect.dat", "w")
    for val in vals:
        
        new_params = list(rhino_params.values())
        new_params[i] = "{:.2f}".format(round(val, 2))
        
        for j, new_val in enumerate(new_params): f.write(str(new_val)+("" if j==len(rhino_params)-1 else ","))
        f.write("\n")
        

    f.close()
    
    # Run the sets of params and save results
    os.system("rm params*png")
    os.system("python parallel_beam_runs.py examine_params_effect.dat")

    # Generate html
    names = list(rhino_params)
    params = np.loadtxt("examine_params_effect.dat", delimiter=",")[:, i]
    f = open("beams.html", "w")
    # Hardwired assumes there are 11
    f.write("Fiducial values "+str(rhino_params)+"<p><p>")
    f.write("<table>\n")
    f.write("<tr><th align=center>"+names[i]+" = "+str(params[0])+"</th><th align=center>"+names[i]+" = "+str(params[1])+"</th><th align=center>"+names[i]+" = "+str(params[2])+"</th></tr>\n")
    f.write("<tr><td align=center><img alt=Failed src=horn_0.png></td><td align=center><img alt=Failed src=horn_1.png></td><td align=center><img alt=Failed src=horn_2.png></td></tr>\n")
    f.write("<tr><td align=center><img alt=Failed src=params_0.png></td><td align=center><img alt=Failed src=params_1.png></td><td align=center><img alt=Failed src=params_2.png></td></tr>\n")
    f.write("<tr><th align=center>"+names[i]+" = "+str(params[3])+"</th><th align=center>"+names[i]+" = "+str(params[4])+"</th><th align=center>"+names[i]+" = "+str(params[5])+"</th></tr>\n")
    f.write("<tr><td align=center><img alt=Failed src=horn_3.png></td><td align=center><img alt=Failed src=horn_4.png></td><td align=center><img alt=Failed src=horn_5.png></td></tr>\n")
    f.write("<tr><td align=center><img alt=Failed src=params_3.png></td><td align=center><img alt=Failed src=params_4.png></td><td align=center><img alt=Failed src=params_5.png></td></tr>\n")
    f.write("<tr><th align=center>"+names[i]+" = "+str(params[6])+"</th><th align=center>"+names[i]+" = "+str(params[7])+"</th><th align=center>"+names[i]+" = "+str(params[8])+"</th></tr>\n")
    f.write("<tr><td align=center><img alt=Failed src=horn_6.png></td><td align=center><img alt=Failed src=horn_7.png></td><td align=center><img alt=Failed src=horn_8.png></td></tr>\n")
    f.write("<tr><td align=center><img alt=Failed src=params_6.png></td><td align=center><img alt=Failed src=params_7.png></td><td align=center><img alt=Failed src=params_8.png></td></tr>\n")
    f.write("<tr><th align=center>"+names[i]+" = "+str(params[9])+"</th><th align=center>"+names[i]+" = "+str(params[10])+"</th></th></tr>\n")
    f.write("<tr><td align=center><img alt=Failed src=horn_9.png></td><td align=center><img alt=Failed src=horn_10.png></td><td align=center></td></tr>\n")
    f.write("<tr><td align=center><img alt=Failed src=params_9.png></td><td align=center><img alt=Failed src=params_10.png></td><td align=center></td></tr>\n")
    f.write("</table>\n")
    f.close()

    os.system("zip examine_param_"+str(i)+" beams.html examine_params_effect.dat params_*.png")

    sys.stdout.flush()
