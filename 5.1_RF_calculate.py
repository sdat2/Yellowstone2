##### RF CREATION SCRIPT FOR RF ANALYSIS#################
# This script deconvolves RT seismogram components to produce RF based on user inputs 
# requires module receiver_function.py in same folder program is run in. Adds computed RF to pre-existing PICKLE event file
##################################################################


import obspy
from obspy import read
from obspy.core import Stream
from obspy.core import trace
from obspy.core import event
from obspy.taup.taup import getTravelTimes
import os.path
import glob
import shutil
import numpy as np
from obspy import UTCDateTime
import time
import receiver_function as rf
import datetime
import time
import obspy.signal
import obspy.signal.rotate
import scipy
import sys

direc = '/raid3/sdat2/Parra/DataRF'
flag = 'SV' #rdial (SV) or tranverse (ST) RF to compute
filt = 'tff3' #define frequency range

#could do this more elegantly with a dictionary set up
filterconst_dict = {'jgf1':0.4,'jgf2':1.0,'jgf3':0.2,'tff1':1.4,'tff2':1.2,'tff3':1.0,'tff4':0.8,'tff5':0.6}
fmin_dict = {'jgf1':0.01,'jgf2':0.02,'jgf3':0.02,'tff1':0.01,'tff2':0.01,'tff3':0.01,'tff4':0.01,'tff5':0.01}
fmax_dict = {'jgf1':0.2,'jgf2':0.5,'jgf3':0.1,'tff1':0.7,'tff2':0.6,'tff3':0.5,'tff4':0.4,'tff5':0.3}

if filt in ['jgf1','jgf2','jgf3','tff1','tff2','tff2','tff3','tff4','tff5']:
    filterconst = filterconst_dict[filt]
    filttype = 'gauss' # was gauss for all filts
    fmin = fmin_dict[filt]
    fmax = fmax_dict[filt]

count = 0
stations = glob.glob(direc+'/*')
print('about to iterate through ',len(stations),' stations that have directories') 
for stadir in stations:
    print("Station:", stadir)
    stalist=glob.glob(stadir+'/Fresh_copies/*.PICKLE')
    print('This station has ',len(stalist), ' pickle files in its /Fresh_copies')
    newdirec = stadir + '/'+filt+'_added'
    otherdirec = stadir+'/Fresh_copies_2'

    if not os.path.exists(newdirec):
        os.makedirs(newdirec)
    if not os.path.exists(otherdirec):
        os.makedirs(otherdirec)

    for sta in stalist:#iterate through all the PICKLEs in station
        print(sta)
        try:
            seis = read(sta,format='PICKLE')
            Ptime = seis[0].stats.traveltimes['P']
            distdg=seis[0].stats['dist']
            if hasattr(seis[0],filt):
                print ('already done with', sta)
            else:
                Ptime = seis[0].stats['starttime'] + Ptime
                vertical = seis.select(channel='BHZ')[0]
                Pref = vertical.slice(Ptime-25.,Ptime+150.)
                Pref.time=Pref.times()-25.
                if flag =='SV': #using this type of RF ATM
                    radial=seis.select(channel='BHR')[0]
                    SVref = radial.slice(Ptime-25.,Ptime+150.)
                if flag =='SH': #different possible RF
                    transverse=seis.select(channel='BHT')
                    SVref = transverse.slice(Ptime-25.,Ptime+150.)
                    #named SVref for convenience not truth
                SVref.resample(10.)
                SVref.time=SVref.times()-25.

                Pref.filter('bandpass', freqmin=fmin,freqmax=fmax,corners=2,zerophase=True)
                SVref.filter('bandpass', freqmin=fmin,freqmax=fmax,corners=2,zerophase=True)
                seis[0].stats['minfreq']=fmin
                seis[0].stats['maxfreq']=fmax
                Pref.taper(max_percentage=0.05, type='cosine')
                SVref.taper(max_percentage=0.05,type='cosine')
                RF=trace.Trace()

                if 1==1:

                        if flag=='SV':
                            if filt=='jgf1': 
                                seis[0].jgf1=dict()
                                out=seis[0].jgf1 
                            elif filt=='jgf2':
                                seis[0].jgf2=dict()
                                out=seis[0].jgf2
                            elif filt=='jgf3':
                                seis[0].jgf3=dict()
                                out=seis[0].jgf3
                            elif filt=='tff1':
                                    seis[0].tff1=dict()
                                    out=seis[0].tff1
                            elif filt=='tff2':
                                    seis[0].tff2=dict()
                                    out=seis[0].tff2
                            elif filt=='tff3':
                                    seis[0].tff3=dict()
                                    out=seis[0].tff3
                            elif filt=='tff4':
                                    seis[0].tff4=dict()
                                    out=seis[0].tff4
                            elif filt=='tff5':
                                    seis[0].tff5=dict()
                                    out=seis[0].tff5                 
                            else:
                                print('Define a new dictionary to store results in')

                        if flag=='SH':
                            if filt=='rff1':
                                seis[0].rfshf1=dict()
                                out=seis[0].rfshf1
                            elif filt=='rff2':
                                seis[0].rfshf2=dict()
                                out=seis[0].rfshf2
                            elif filt=='rff3':
                                seis[0].rfshf3=dict()
                                out=seis[0].rfshf3                  

                        out['filter']=filttype
                        out['filterconst']=filterconst
                        out['timeshift']=25.

                        if len(SVref.data)==0 or len(Pref.data)==0:
                            continue #('no try except currently present)
                        # Run iterative deconvolution
                        # this is were the actual work happens
                        RF.data, fitid =rf.iterative_deconvolution(SVref.data,Pref.data,maxbumps= 200,dt = Pref.stats['delta'],filt = filttype,fmax= filterconst,timeshift = 25.)
                        # Normalize and switch polarity if needed
                        indm=np.argmax(np.abs(RF.data[200:300]))
                        RF.data=RF.data/RF.data[200+indm]

        # what does this actually achieve? where does out go? When is out fed back in to the PICKLE?
                        out['iterativedeconvolution']=RF.data
                        out['iterativedeconvolution_fit']=fitid
                        out['time']=SVref.time

                        print('finished for',sta)

                        BAZ=seis[0].stats['baz']
                        DIST=seis[0].stats['dist']
                        print(BAZ,DIST)
                        baz_str=format(BAZ,'.3f').zfill(7)
                        dist_str=format(DIST,'.3f').zfill(7)
                        ev_str=str(seis[0].stats.starttime)
                        filename=newdirec +'/'+baz_str+'_'+dist_str+'_'+ev_str+'.PICKLE'

                        seis.write(filename,'PICKLE')
                        count += 1
                        print('Wrote to File', filename, 'number', count)
                        shutil.copy(sta, otherdirec)
                        print('Copied to:', otherdirec)
                        os.remove(sta)
                        print('Now deleting ', sta)
        except:
            print('failed (possibly at read)')
                
