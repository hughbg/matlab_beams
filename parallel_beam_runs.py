import sys
import subprocess, os
import numpy as np
import tempfile
from plot_horn import plot_horn
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm

MAX_PROCESSES = 15



def plot_beam(data_file, az_file, za_file, name, save_to=None):
    """
    Plot a beam. The plot is the beam projected flat onto the ground when looking from above.
    Colors indicate the beam values.

    Parameters
    ----------
    data_file : matlab beam output za by az
        The beam to plot.
    az_file : matlab az file
    za_file: matlab za file
    save_to: str
        A file name to save the plot to.

    """
    
    
    
    az = np.deg2rad(np.loadtxt(az_file, delimiter=","))
    za = np.deg2rad(np.loadtxt(za_file, delimiter=",")+90)  # Trickey going on here, setup by the Tilt
    data = np.loadtxt(data_file, delimiter=",")
    data = 10**(data/10)    # dB to power
    
    assert data.shape[0] == za.size and data.shape[1] == az.size
    
    za_coord = np.repeat(za, az.size)
    az_coord = np.tile(az, za.size)
    data = data.ravel()
    
    r = np.sin(za_coord)
    x = r*np.sin(az_coord)
    y = r*np.cos(az_coord)  

    grid_dim = 64

    # convert the x/y points to a grid location. x/y can be -1 to 1
    gi = np.round(np.interp(x, [-1, 1], [0, grid_dim-1])).astype(int)
    gj = np.round(np.interp(y, [-1, 1], [0, grid_dim-1])).astype(int)

    # Insert beam values into grid and weight
    grid = np.zeros((grid_dim, grid_dim), dtype=complex)
    np.add.at(grid, (gi, gj), data)
    weights = np.zeros((grid_dim, grid_dim))
    np.add.at(weights, (gi, gj), 1)

    grid /= weights

    #ax = plt.axes()
    #ax.remove()           # Causes problem in subplots

    plt.clf()
    im=plt.imshow(np.abs(grid), interpolation="quadric", norm=LogNorm(), cmap="rainbow")
    plt.xticks([])
    plt.yticks([])


    if False:
        points = np.arange(0, 2*np.pi, 0.01)
        for deg in [ 30, 45, 60, 75 ]:
            r = np.cos(deg*np.pi/180)
            x = r*np.cos(points)
            y = r*np.sin(points)
            plt.text(r/np.sqrt(2), -r/np.sqrt(2), "    $"+str(deg)+"^\circ$", c="w")
            plt.scatter(x, y, s=0.01, c='w', marker='o')
    

    plt.colorbar(im,fraction=0.04, pad=0.04)
    plt.title(name)

    for pos in ['right', 'top', 'bottom', 'left']: 
        plt.gca().spines[pos].set_visible(False) 
    # shape.custom3d()
    #show()
    # or just show(h2) replace with image dump

    if save_to is not None:
        plt.savefig(save_to)
        
       
def finish_up_processes(plist):
    # plist is is list of tuples. Each tuple is (process handle, params index, tmpfile)
    
    status = [ p_info[0].wait() for p_info in plist ]

    # Plot all the beams from processes we waited for. Some may have failed, which means
    # there are no output files. Check for that. Also delete the tmp file.
    for p_info in plist:

        j = str(p_info[1])
        if os.path.exists("matlab_horn_"+j+".dat"):
            print("Params index", j, "ok")
            plot_beam("matlab_horn_"+j+".dat", "matlab_horn_az_"+j+".dat", "matlab_horn_el_"+j+".dat",
                  "params number "+j, save_to="params_"+j)
        else:
            print("Params index", j, "failed")

            if os.path.exists("params_"+j+".png"): os.remove("params_"+j+".png")

        if os.path.exists(p_info[2]): os.remove(p_info[2])
                

        


assert len(sys.argv), sys.argv[0]+": expecting path to generations file"

matlab_commands = """
h2 = horn(FlareWidth={FlareWidth}, Width={Width}, FeedWidth={FeedWidth}, FlareHeight={FlareHeight}, Height={Height}, FeedHeight={FeedHeight}, FlareLength={FlareLength}, Length={Length}, FeedOffset=[{FeedOffset0} {FeedOffset1}], Tilt=90, TiltAxis=[0, 1 0]);
[pat, az, el] = pattern(h2, 350E6, 0:1:360, -90:1:90);
writematrix(pat, "matlab_horn_{index}.dat");
writematrix(el, "matlab_horn_el_{index}.dat");
writematrix(az, "matlab_horn_az_{index}.dat");
exit;
"""

""" 
    Ordering is defined in the genetic algorithm code - horn_antenna.py
        self.ordering = [ "FlareWidth", "Width", "FeedWidth", "FlareHeight", "Height", "FeedHeight", "FlareLength", "Length",                            "FeedOffset0", "FeedOffset1" ]
"""

individuals = np.loadtxt(sys.argv[1], delimiter=",")
individuals = np.atleast_2d(individuals)

process_list = []     # Contains tuple, tuple[0] is pid, tuple[1] is which params, line 0, 1, etc, tuple[3] temp file

for i, params in enumerate(individuals):
    
    # Plot the horn, we always want that
    p = { 'FlareWidth': params[0],
         'Width': params[1],
         'FeedWidth': params[2],
         'FlareHeight': params[3],
         'Height': params[4],
         'FeedHeight': params[5],
         'FlareLength': params[6],
         'Length': params[7],
         'FeedOffset0': params[8],
         'FeedOffset1': params[9]
         }
    
    plot_horn(p, save_to="horn_"+str(i))
    
    # Create matlab script in tmp file

    tmpfile = tempfile.mkstemp(suffix=".m", dir=".")

    os.write(tmpfile[0], str.encode(matlab_commands.format(FlareWidth=params[0], Width=params[1], FeedWidth=params[2], 
                                     FlareHeight=params[3], Height=params[4], FeedHeight=params[5], FlareLength=params[6],
                                     Length=params[7], FeedOffset0=params[8], FeedOffset1=params[9], index=i)))
    
    os.close(tmpfile[0])
    
    # Start process    
    command = ["/ssd3/MATLAB/R2023b/bin/matlab", "-batch", os.path.basename(tmpfile[1][:-2])]
    print(command)
    
    # Remove any old output files
    for f in [ "matlab_horn_"+str(i)+".dat", "matlab_horn_az_"+str(i)+".dat", "matlab_horn_el_"+str(i)+".dat" ]:
        if os.path.exists(f): os.remove(f)
        
    # Run matlab to generate a beam
    p = subprocess.Popen(command)
    process_list.append((p, i, tmpfile[1]))
    
    # If num of processes reaches limit then wait for current ones
    if len(process_list) == MAX_PROCESSES:
        
        print("Waiting for", MAX_PROCESSES, "processes to finish")
        
        finish_up_processes(process_list)
        process_list = []

    
    
if len(process_list) > 0:
    finish_up_processes(process_list)
