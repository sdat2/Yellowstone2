#Begin 4_plot_data_preRF_perstation.py, a python program by Sanne Cottaar (sc845@cam.ac.uk)

#####RAW SEISMOGRAM PLOTTING SCRIPT FOR RF ANALYSIS#################
# This script plots ZRT seismogram components with predicted arrival times after initial processing and before RF creation
# Because of the large size of the Yellowstone dataset (268000 original PICKLE files inside my box) I will not use this much
##################################################################

import obspy
from obspy import read
from obspy.core import Stream
from obspy.core import trace
import matplotlib.pyplot as plt
import os.path
import time
import glob
import shutil
import numpy as np
from obspy import UTCDateTime
import subprocess
from obspy.taup.taup import getTravelTimes
from obspy.taup import TauPyModel

direc = '/raid3/sdat2/Parra/DataRF' #go into the data folder

stadirs = glob.glob(direc+'/*') #create a large object from all the directories
print('there are',len(stadirs),' stations in ', direc)
for stadir in stadirs: #loop through all of them
    # loop through events
    print('looking in ', stadir+'/Travel_time_added/*.PICKLE')
    stalist=glob.glob(stadir+'/Travel_time_added/*.PICKLE') #create a list from all the pickles						#in that directory
    # Loop through pickles
    print('I have made a list of ',len(stalist),' Pickles for this station') 
    if(len(stalist)>0):
        for i in range(len(stalist)): #range(cat.count()):

                seis=read(stalist[i],format='PICKLE') #put each pickle into a seis local variable

                #extract epi dist of event/station from header info
                distdg=seis[0].stats['dist']
			#further local variable distdg created

                #----------------PLOT VERTICAL--------------------------------
                #1 of 3 subplots (grid 1 row 3 columns)
                plt.subplot(1,3,1)
                vertical = seis.select(channel='BHZ')[0] #extract V from stream 
		#chop pickle into vertical part, filter pickle
                vertical.filter('bandpass', freqmin=0.01,freqmax=.1, corners=2, zerophase=True)
                
		#plot vertical part of pickle
                plt.plot(vertical.times(), vertical.data/np.max(vertical.data)+np.round(distdg),'k')	
		#plot normalised data as black line

                #Plot predicted travel times as coloured points (add more phases as wanted)
                plt.plot(seis[0].stats.traveltimes['P'],np.round(distdg),'.b')
		# P waves are blue
                plt.plot(seis[0].stats.traveltimes['S'],np.round(distdg),'.g')
		# S waves are green
               
                #label plot
                plt.title('Vertial')   
                plt.ylabel('Epi dist (degrees)') 
                plt.xlabel('Time from Origin (sec)') 

                #----------------PLOT RADIAL--------------------------------
                #2 of 3 subplots
                plt.subplot(1,3,2)
		#again we need to chop and filter pickle for radial part
                radial = seis.select(channel='BHR')[0]

                radial.filter('bandpass', freqmin=0.01,freqmax=.1, corners=2, zerophase=True)
 
                plt.plot(radial.times(), radial.data/np.max(radial.data)+np.round(distdg),'k')

                #More theoretical curves for travel times      
                plt.plot(seis[0].stats.traveltimes['P'],np.round(distdg),'.b')
        # Write out seismogram againt(seis[0].stats.traveltimes['P'],np.round(distdg),'.b')
                plt.plot(seis[0].stats.traveltimes['P410s'],np.round(distdg),'.b')
                plt.plot(seis[0].stats.traveltimes['P660s'],np.round(distdg),'.b')
                plt.plot(seis[0].stats.traveltimes['S'],np.round(distdg),'.g')
                
                plt.title('Radial')    
                plt.xlabel('Time from Origin (sec)') 

                #----------------PLOT TRANSVERSE--------------------------------
                #3 of 3 subplots                
                plt.subplot(1,3,3) #3rd argument increments by 1 each thime
                transverse = seis.select(channel='BHT')[0]
                transverse.filter('bandpass', freqmin=0.01,freqmax=.1, corners=2, zerophase=True)
  		
		#More theoretical curves for travel times
                plt.plot(transverse.times(), transverse.data/np.max(transverse.data)+np.round(distdg),'k')  
                plt.plot(seis[0].stats.traveltimes['P'],np.round(distdg),'.b')
                plt.plot(seis[0].stats.traveltimes['S'],np.round(distdg),'.g') 

		#again no y axis label, but I suppose using same as first plot as long as scaling consistent
                plt.title('Transverse') 
                plt.xlabel('Time from Origin (sec)')     
      
        plt.show() #once all the data has been added we output the plot
