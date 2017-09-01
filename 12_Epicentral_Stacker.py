'''
STACK_TIME_FULL.py
Stacks the RFs in bins of epicentral distance to show the most prominent features. 
Plots a graph of epicentral distance against time, with a red-blue colour map showing positive and negative amplitudes.
After calling up the script, put various arguments:

sys.argv[1] = step (width of epicentral distance bin) i.e. 2
sys.argv[2] = smoothing (adds adjacent bins to smooth the features) i.e. s
sys.argv[3] = data set (run script over whole data set or specific stations) i.e. full (for whole data set), YS (for this whole network) or YS.PL24 (for this station)
sys.argv[4] = histogram (plots epicentral distance histogram; how many RFs in each bin, pre-smoothing) i.e. h
sys.argv[5] = predicted travel time (plots the travel time curves for all phases written here) i.e. P1000s
sys.argv[6] = subdirectory e.g RF_auto_check1
Example: STACK_TIME_FULL.py 2 s YS.PL24 h P1000s RF_auto_checked 
(will plot a smoothed graph with bins of 2 degrees as well as a histogram of the RFs from station YS.PL24, and also P1000s travel time curve)
'''
root = '/raid3/sdat2/Parra/'


#----------------------------------------Import all the relevant modules---------------------------------------

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

#Set size of image
fig = plt.figure(figsize = (12,6))


#----------------------------------------Set up the arrays for the STACK and counter--------------------------------------- 

#Define min/max epi dist and no. steps
step=int(sys.argv[1])
epi_steps=(60/step)+1
min_epi=30
max_epi=90
epi_range=np.linspace(min_epi,max_epi,epi_steps) #linspace retuns evenly spaced numbers over a specified interval linspace(start value, end value, number of samples to generate

#Set up stack ( matrix [len of RF x no of bins ])
STACK=np.zeros([1751, epi_steps])                #returns an array of given shape and type, filled with zeros

#Set up counter to see how many RFs are added to each bin
counter=np.zeros([epi_steps])

Failed_at_List = []
#----------------------------------------Loop through the RF data for a specific station---------------------------------------


subdirectory = str(sys.argv[6]) # 'RF_auto_checked'
if str(sys.argv[3]) != 'all':
            direc = root+ 'DataRF/'+str(sys.argv[3])+'/'+ subdirectory
else:
            direc = root+'DataRF/*/'+subdirectory
filt = 'jgf1'
stalist=glob.glob(direc+'/*.PICKLE')
for i in range(len(stalist)):
            try:
                        seis=read(stalist[i],format='PICKLE')
                        print (stalist[i])

                        #Extract various bits of info
                        epi_dist=seis[0].stats['dist']
                        RF_amp=getattr(seis[0],filt)['iterativedeconvolution']

                        #Find out which bin this should go into in the stack
                        rounded_epi_dist=(round(epi_dist))

                        #Find the index i the stack matrix that this epicentral distance relates to
                        rounded_epi_dist_loc=(round((epi_dist-30)/step))

                        #Check it has found correct bin
                        print (epi_dist, "index",rounded_epi_dist_loc, epi_range[rounded_epi_dist_loc])

                        #Add every RF amplitude (vector) to the correct column (bin) in the STACK matrix
                        STACK[:,rounded_epi_dist_loc]=STACK[:,rounded_epi_dist_loc]+RF_amp

                        #Add 1 to the count of this bin to keep track of how many RFs it contains
                        counter[rounded_epi_dist_loc]=counter[rounded_epi_dist_loc] + 1
            except:
                        print('arrgh')
                        Failed_at_List.append(stalist[i])

                
#----------------------------------------Plot the stack---------------------------------------

#Get the time y axis (same in each RF) 
time=getattr(seis[0],filt)['time']

#Used to emphasise the smaller peaks (other than direct P)
NORMALIZATION=0.075

#Smoothing process

#Create new stack and counter
STACK_NEW=np.zeros([1751, epi_steps])
counter_new=np.zeros([epi_steps])

#Loop through the stack and counter, careful of the ends of the arrays
for p in range(len(counter)):
    if p == 0:
        STACK_NEW[:,p]=STACK[:,p]+STACK[:,p+1]
        counter_new[p]=counter[p]+counter[p+1]
    elif p == (len(counter)-1):
        STACK_NEW[:,p]=STACK[:,p]+STACK[:,p-1]
        counter_new[p]=counter[p]+counter[p-1]
    else:
        STACK_NEW[:,p]=STACK[:,p]+STACK[:,p-1]+STACK[:,p+1]
        counter_new[p]=counter[p]+counter[p-1]+counter[p+1]

#Normalization and average
#Divide stack by number of RF in each bin - recorded in counter
for m in range(len(counter)):
    if counter[m]>0:
        STACK_NEW[:,m]=STACK_NEW[:,m]/counter_new[m]

        #Check that direct P has amp of 1
        STACK_NEW[:,m]=STACK_NEW[:,m]/(np.nanmax(np.abs(STACK_NEW[:,m])))

#Normalize after direct P to bring out other features
STACK_NEW[:,:]=STACK_NEW[:,:]/NORMALIZATION  

#Plot STACK

#Set up first subplot
ax1=plt.subplot2grid((3,1),(1,1))

#Plotting command (x axis, y axis, matrix of values, colourmap, min and max values)
plt.pcolor(epi_range,time,STACK_NEW,cmap='seismic',vmin=-1,vmax=1)

#Axes labels
plt.ylabel('Time (seconds)')
plt.xlabel('Epicentral Distance (degrees)')

#Axes limits
plt.gca().set_xlim([30,90])
plt.gca().set_ylim([0,150])
plt.gca().invert_yaxis()


    
#----------------------------------------Plot Predicted Travel Times---------------------------------------

#Read in the predicted travel time differences from the appropriate file
data = np.genfromtxt(root +'/Travel_Times/TT_'+'P410s'+'.dat', delimiter='\t')

#Get the epicentral distance, set as x, and the travel time differences, set as y
x=data[:,0]
y=data[:,1]

#Plot the curves on the stack, annotating each with the name of the phase
plt.plot(x,y)
plt.annotate ('P410s', xy=(x[580], y[600]), xytext=(30,-5), textcoords='offset points')


#Read in the predicted travel time differences from the appropriate file
data = np.genfromtxt(root +'Travel_Times/TT_'+'P660s'+'.dat', delimiter='\t')

#Get the epicentral distance, set as x, and the travel time differences, set as y
x=data[:,0]
y=data[:,1]

#Plot the curves on the stack, annotating each with the name of the phase
plt.plot(x,y)
plt.annotate ('P660s', xy=(x[580], y[600]), xytext=(30,-5), textcoords='offset points')


#Read in the predicted travel time differences from the appropriate file
data = np.genfromtxt(root +'Travel_Times/TT_'+'P1000s'+'.dat', delimiter='\t')

#Get the epicentral distance, set as x, and the travel time differences, set as y
x=data[:,0]
y=data[:,1]

#Plot the curves on the stack, annotating each with the name of the phase
plt.plot(x,y)
plt.annotate ('1000s', xy=(x[580], y[600]), xytext=(30,-5), textcoords='offset points')

#Read in the predicted travel time differences from the appropriate file
data = np.genfromtxt(root +'Travel_Times/TT_'+'PcP'+'.dat', delimiter='\t')

#Get the epicentral distance, set as x, and the travel time differences, set as y
x=data[:,0]
y=data[:,1]

#Plot the curves on the stack, annotating each with the name of the phase
plt.plot(x,y)
plt.annotate ('PcP', xy=(x[580], y[600]), xytext=(30,-5), textcoords='offset points')

#Read in the predicted travel time differences from the appropriate file
data = np.genfromtxt(root +'Travel_Times/TT_'+'PP'+'.dat', delimiter='\t')

#Get the epicentral distance, set as x, and the travel time differences, set as y
x=data[:,0]
y=data[:,1]

#Plot the curves on the stack, annotating each with the name of the phase
plt.plot(x,y)
plt.annotate ('PP', xy=(x[150], y[160]), xytext=(30,-5), textcoords='offset points')


#Read in the predicted travel time differences from the appropriate file
data = np.genfromtxt(root +'Travel_Times/TT_'+'PPv410s'+'.dat', delimiter='\t')

#Get the epicentral distance, set as x, and the travel time differences, set as y
x=data[:,0]
y=data[:,1]

#Plot the curves on the stack, annotating each with the name of the phase
plt.plot(x,y)
plt.annotate ('PPv410s', xy=(x[580], y[600]), xytext=(30,-5), textcoords='offset points')

    
#----------------------------------------Plot epicentral distance histogram---------------------------------------

#Plot histogram

 
#Add second subplot
ax2=plt.subplot2grid((3,1), (0, 0))

#Loop through the bins
for n in range(len(counter)):
    mindist=(n*step)+30
    maxdist=mindist+step

    #Plot rectangle of histogram ((startx,,starty),width, height))
    ax2.add_patch(patches.Rectangle((mindist, 0), step, counter[n],facecolor='#AF7AC5',edgecolor='0.3'))

#Axes labels
plt.ylabel('Number of RFs')


#Axes limits
plt.gca().set_xlim([30,90])
plt.gca().set_ylim([0,np.nanmax(np.abs(counter[:]))])

#Subplot arrangement
ax2.xaxis.tick_top()
ax2.xaxis.set_label_position('top') 
plt.subplots_adjust(hspace=0)



#----------------------------------------Final plotting---------------------------------------

plt.suptitle('Epicentral Distance Stack - Bin Size='+str(sys.argv[1])+' - Directory='+ direc)
plt.show()





