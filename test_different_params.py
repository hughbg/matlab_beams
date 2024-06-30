import sys
import tempfile, os
import numpy as np

assert len(sys.argv), sys.argv[0]+": expecting path to params file"

matlab_commands = """
h2 = horn(FlareWidth={FlareWidth}, Width={Width}, FeedWidth={FeedWidth}, FlareHeight={FlareHeight}, Height={Height}, FeedHeight={FeedHeight}, FlareLength={FlareLength}, Length={Length}, FeedOffset=[{FeedOffset0} {FeedOffset1}], Tilt=90, TiltAxis=[0, 1 0]);
%mesh(h2,'MaxEdgeLength',0.1);
%[pat, az, el] = pattern(h2, 350E6, 0:1:360, -90:1:90);
%writematrix(pat, "matlab_horn.dat");
%writematrix(el, "matlab_horn_el.dat");
%writematrix(az, "matlab_horn_az.dat");
exit;
"""

""" Ordering is defined in the genetic algorithm code - horn_antenna.py
        self.ordering = [ "FlareWidth", "Width", "FeedWidth", "FlareHeight", "Height", "FeedHeight", "FlareLength", "Length",                            "FeedOffset0", "FeedOffset1" ]
"""

vals = np.loadtxt(sys.argv[1])

for i, params in enumerate(vals):
    print("params", i)
    f = open("test_params.m", "w")
    
    f.write(matlab_commands.format(FlareWidth=params[0], Width=params[1], FeedWidth=params[2], FlareHeight=params[3], Height=params[4], FeedHeight=params[5], FlareLength=params[6], Length=params[7], FeedOffset0=params[8], FeedOffset1=params[9]))
    f.close()
    
    os.system("/ssd3/MATLAB/R2023b/bin/matlab -batch test_params")
    

    
    