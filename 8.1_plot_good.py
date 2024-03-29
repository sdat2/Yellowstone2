# Program 8_plot_data_perstation.py written by Sanne Cottaar (sc845@cam.ac.uk)
file_name= '8_plot_data_perstation.py'
# Uses receiver functions computed to produce a nice graph for every directory in DATARF

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
import receiver_function as rf


direc = 'DataRF'
flag = 'SV'
filt = 'jgf1'

stadirs = glob.glob(direc+'/*')

for stadir in stadirs:
    print(stadir)

    # loop through events
    stalist=glob.glob(stadir+'/RF_auto_checked/*.PICKLE')
    print(stalist)
    c=0
    # Loop through data
    if(len(stalist)>0):
        for i in range(len(stalist)): #range(cat.count()):
                print(stalist[i])
                seis=read(stalist[i],format='PICKLE')
                distdg=seis[0].stats['dist']
                print('YAY',seis[0].stats['event'].magnitudes[0].mag)
                tshift=UTCDateTime(seis[0].stats['starttime'])-seis[0].stats['event'].origins[0].time
  
                #Ptime=Ptime
                plt.subplot(1,3,1)
                vertical = seis.select(channel='BHZ')[0]
                vertical.filter('bandpass', freqmin=0.01,freqmax=.1, corners=2, zerophase=True)
                windowed=vertical[np.where(vertical.times()>seis[0].stats.traveltimes['P']-100) and np.where(vertical.times()<seis[0].stats.traveltimes['P']+100)]
                norm=np.max(np.abs(windowed))
                plt.plot(vertical.times()-seis[0].stats.traveltimes['P'], vertical.data/norm+np.round(distdg),'k')
                plt.xlim([-25,150])
                plt.ylim([30,92])
                plt.subplot(1,3,2)
                radial = seis.select(channel='BHR')[0]

                radial.filter('bandpass', freqmin=0.01,freqmax=.1, corners=2, zerophase=True)
                windowed=vertical[np.where(radial.times()>seis[0].stats.traveltimes['P']-100) and np.where(radial.times()<seis[0].stats.traveltimes['P']+100)]
                norm=np.max(np.abs(windowed))
                plt.plot(radial.times()-seis[0].stats.traveltimes['P'], radial.data/norm+np.round(distdg),'k')
                plt.xlim([-25,150])                  
                plt.plot(seis[0].stats.traveltimes['P'],np.round(distdg),'.b')
                plt.plot(seis[0].stats.traveltimes['S'],np.round(distdg),'.g')
                plt.ylim([30,92])
            
                plt.subplot(1,3,3)
                RF=getattr(seis[0],filt)['iterativedeconvolution']
                time=getattr(seis[0],filt)['time']

                plt.plot(time, RF/np.max(np.abs(RF))+np.round(distdg),'k')
                     
                
                    
        plt.subplot(1,3,1)
        plt.title('vertical')
        plt.ylabel('distance')
        plt.xlabel('time')
        plt.subplot(1,3,2)
        plt.title('radial')
        plt.ylabel('distance')
        plt.xlabel('time')
        plt.subplot(1,3,3)
        plt.title('receiver functions')
        plt.ylabel('distance')
        plt.xlabel('time')
        #plt.xlim([-150,1000])        
        plt.show()
