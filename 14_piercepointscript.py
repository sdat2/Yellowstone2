# This script computes predicted pierce points for user defined phases based on TauP

import sys,os 
import obspy
from obspy import read
from obspy.core import Stream
from obspy.core import trace
import matplotlib.pyplot as plt
import os.path
import time as timer
import glob
import shutil
import numpy as np
from obspy import UTCDateTime
import subprocess
import scipy
from scipy import interpolate
from obspy.taup.taup import getTravelTimes
from obspy.taup import TauPyModel
from geographiclib.geodesic import Geodesic as geo
from tempfile import NamedTemporaryFile

root = '/raid3/sdat2/Parra/'
subdirectory = 'tff3_auto_check_2'
#name of output file to save all pierce points to
output_file1 = root+'Piercepoint_Scripts/piercepointsP1000s_1000km.txt'
#open the file you are going to save into (w means you can write onto it)
out_put_write1=open(output_file1, 'w')

#define phases used
phase = ['P1000s']
# Find list of stations directories
stations = glob.glob(root+'DataRF/*')
# Loop through stations
for stadir in stations:
    stalist=glob.glob(stadir+'/'+subdirectory+'/*PICKLE')
    for s in range(len(stalist)):
        print(stalist[s])
        onestation = read(stalist[s],format='PICKLE')
        #note stats of stream as merge gets rid of them
        BAZ=onestation[0].stats['baz']
        EVLA=onestation[0].stats['evla']
        EVLO= onestation[0].stats['evlo']
        EVDP= onestation[0].stats['evdp']
        STLA= onestation[0].stats['stla']
        STLO= onestation[0].stats['stlo']
        DIST= onestation[0].stats['dist']
        AZ= onestation[0].stats['az']
        STATION= onestation[0].stats['station']
        NETWORK= onestation[0].stats['network']
        EVENT= onestation[0].stats['event']

        #start a pierce points dictionary
        if not hasattr(onestation[0].stats, 'piercepoints'):
            onestation[0].stats.piercepoints=dict()

        #------------looking for pierce points at 1000km------------------
        for ph in range(len(phase)):
            test = ['taup_pierce -mod prem1070.nd -h '+str(EVDP)+' -ph '+phase[ph]+' -pierce 1000 -nodiscon -sta '+str(STLA)+' ' ' '+str(STLO)+' -evt '+str(EVLA)+' ' ' '+str(EVLO)+'']
            #out runs test above in the terminal
            out=subprocess.check_output(test,shell=True,universal_newlines=True)
            t=out.split('\n')
            if t[1] == '': pass
            else:#if source is deeper than depth piercing, it only pierces once
                if EVDP < 1000:
                    u = t[2].split()
                else:
                    u = t[1].split()
            #make a separate dictionary within piercepoints for each phase
            onestation[0].stats.piercepoints[phase[ph]] = dict()
            onestation[0].stats.piercepoints[phase[ph]][str(u[1])] = [u[3],u[4]]
            #write pierce point data to original pickle file
            onestation.write(stalist[s], format = 'PICKLE')
            if phase[ph] == 'P1000s':
                out_put_write1.write("%f %f %f \n" % (float(u[1]),float(u[3]), float(u[4])))
out_put_write1.close()


