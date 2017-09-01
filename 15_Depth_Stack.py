'''
Depth_Stack.py
Stacks all the RFs within the bounds for the depth stated producing one trace.
Normalised at various points to emphasise the smaller phases.
Requires the pierce point script to be run first to generate the data.

'''

#Import all the relevant modules

import obspy
from obspy import read
from obspy.core import Stream
from obspy.core import trace
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import os.path
import time
import glob
import shutil
import numpy as np
from obspy import UTCDateTime
import subprocess
from obspy.taup.taup import getTravelTimes
from obspy.taup import TauPyModel
import pickle
import sys
import math
import random

#Define constraints

#depth of the Pds converted phase and the depth of the pierce points calculated
dp = 660

#lat lon bounds, if not constraining using the grid
latmin = 43
latmax = 46
lonmin = -111
lonmax = -108


#Set some values
root = '/raid3/sdat2/Parra/'
direc = root +'DataRF'
subdirectory = 'RF_auto_check_2'
filt = 'jgf1'
NORM1 = 0.2
NORM2 = 0.05
stalist = glob.glob(direc + '/*/'+subdirectory+'/*.PICKLE')


#Define matrix of receiver functions with P1000s piercepoints within the region

matrix = []


#Loop through events
for s in range(len(stalist)):
    #print (stalist[s])

    #Read in the file
    seis = read(stalist[s],format='PICKLE')

    #Define part RF part of event
    out=getattr(seis[0],filt)

    if hasattr(seis[0].stats['piercepoints'],'P'+str(dp)+'s'):


        #Extract the pierce points
        trace_pierce = seis[0].stats['piercepoints']['P'+str(dp)+'s'][str(float(dp))]
        #print (trace_pierce)

        #Define lat and lon of event pierce points
        latpp = float(trace_pierce[0])
        lonpp = float(trace_pierce[1])


        #Check whether event pierce points located within bounds of regions

        if (latmin <= latpp <= latmax) and (lonmin <= lonpp <= lonmax):
            

            #Form matrix of all events which fit the lat and lon criteria

            matrix.append(stalist[s])

        else:
            pass      
    else:
        pass

# -------- need to pick a random sample of receiver functions ---------

matrix2 = set(matrix)

#need to select a random 90% of receiver functions that fit the regional criteria
sample_no = int(len(matrix)*0.9)
#randomly selects 90% correct receiver functions and puts them into a matrix 

bootleg_matrix = random.sample(matrix2, sample_no)



#Set figure dimensions (larger vertical than horizontal)
fig = plt.figure(figsize=(4, 12))


#Create depth stack
STACK=np.zeros([1400])


#Set up checking counts and event lists
count_yes = 0
count_no = 0
List_yes = []
List_no = []




#Loop through events
for s in range(len(bootleg_matrix)):

    #Read in the file
    seis= read(bootleg_matrix[s],format='PICKLE')

    #Define part RF part of event
    out=getattr(seis[0],filt)


    #Add to list and count
    List_yes.append(bootleg_matrix[s])
    count_yes = count_yes + 1
    #print (count_yes)


    #Extract amplitude vector with regular depth intervals from event
    amp = out['amp_reg']

    #Add this amplitude to the stack
    STACK[:] = STACK[:] + amp




#Extract the regular depth intervals from the event
depth = out['depth_reg']

#Find average amplitudes
amp_rel = STACK[:]/count_yes

#Normalise max value (direct P) to 1
amp_rel[:]=amp_rel[:]/(np.nanmax(np.abs(amp_rel[:])))

#Re-normalise later sections to emphasise the small phases
amp_rel[150:900]=amp_rel[150:900]/NORM1
amp_rel[900:1400]=amp_rel[900:1400]/NORM2

#Print checks
#print (List_yes)
#print (List_no)
#print (count_yes)
#print (count_no)

#Plot the relative amplitudes against the depth points
plt.plot(amp_rel, depth, 'k')

#Fill the postive values with red, negative with blue
plt.fill_betweenx(depth, 0, amp_rel, where=amp_rel >= 0, facecolor=[1, 0.4, 0.4])
plt.fill_betweenx(depth, 0, amp_rel, where=amp_rel <= 0, facecolor=[0.4, 0.4, 1])

#Make label for y axis (none for x)
plt.ylabel('Depth (km)')
plt.xticks([])

#Create dotted lines to show where there are new normalisations
x=[-0.5,1]
y1=[150,150]
y2=[900,900]
plt.plot(x,y1, 'k--')
plt.plot(x,y2, 'k--')

#Set axis limits and invert y axis
plt.gca().set_xlim([-0.5,1])
plt.gca().set_ylim([0,1400])
plt.gca().invert_yaxis()

#Make title of plot
plt.suptitle('Depth Stack - '+str(dp)+'km - No. of RFs: '+str(count_yes)+'\n Lat/Lon Bounds '+str(latmin)+'/'+str(latmax)+'/'+str(lonmin)+'/'+str(lonmax))

#save the plot
filename = 'RegionY21.png'

#plt.savefig('/raid3/kg382/Depth_Stack/Regions/'+filename)

#show the plot
plt.show()

plt.close()
