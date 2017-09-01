'''
convert_to_depth_v2.py

Converts the receiver function from time to location
	location is depth, lon, lat

Script loops through RFs and computes locations and time at several depths
Depths are "discontinuities" found in modified prem model - here 'prem_added_discon_taup.nd' is used

Run on multiple terminals, with inputs defining upper and lower bounds of RFs

eg. python3 convert_to_depth_v2.py 1000 2000 &

'''
subdirectory = '/tff3_auto_check_2'
#----------------------------------------------------------
#
import sys,os 
#sys.path.append('/raid2/sc845/Python/geographiclib-1.34/')
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

#obspy.taup.taup_create.build_taup_model('./prem_added_discon_taup.nd',output_folder = './')
taupmodel = TauPyModel(model='/raid3/sdat2/Parra/prem_added_discon_taup.npz')

#make list of stations
direc = '/raid3/sdat2/Parra/DataRF'
filter = 'tff3'

#make list of all events
stalist = glob.glob(direc+'/*'+subdirectory+'/*.PICKLE')

#define range of RFs in list of all events to loop through
indmin = int(sys.argv[1]) #lower bound, sys.argv[1]
indmax = int(sys.argv[2]) #upper bound, sys.argv[2]
count = indmin
count = 0

#------------------Loop through data-------------------


#loop through events between constraints

c=0
# Loop through list
for i in range(indmin, indmax): 
	
	#how many events have been processed	
	count = count + 1
	print (count, len(stalist))
	print(i, stalist[i])
	seis=read(stalist[i],format='PICKLE') # read in receiver function
	RFtrace = getattr(seis[0],filter)
	
	#check whether event has already got a depth conversion
	done=False
	if hasattr(seis[0],'conversions'):
		if 'prem' in seis[0].conversions:
			print('done')
			done = True
	
	if done is False:
		if seis[0].stats['dist']> 30.  and seis[0].stats['dist'] <90.:
			print('converting for ', stalist[i])
			dt=seis[0].stats['delta']                            # set sampling read
			dist=seis[0].stats['dist']                     # set distance
			depth= seis[0].stats['event']['origins'][0]['depth']/1.e3 # set depth
			slat=float(seis[0].stats['stla'])
			slon=float(seis[0].stats['stlo'])
			elat= seis[0].stats['event'].origins[0]['latitude']
			elon= seis[0].stats['event'].origins[0]['longitude']




			# buggy line time=RFtrace['time']                            # set time axis
			RF=trace.Trace()
			RF.data= RFtrace['iterativedeconvolution']      # define iterative deconvolution as a trace


			# initialize
			refdepths=[]
			reftimes=[]
			reftakeoff=[]
			refincident=[]
			refslow=[]

			# get slownesses and incident angles based on PREM using Taup in Obspy
			phases =  ['P','Pms','P220s','P310s','P400s','P550s','P670s','P971s','P1171s']
			phdepths = [0,24.4,220,310,400,550,670,971,1171]
			for p,ph in enumerate(phases):
				arr = taupmodel.get_travel_times(depth,dist,[ph])
				if p ==0:
					Preftime=arr[0].time
					Prefslow=arr[0].ray_param
					Preftakeoff= arr[0].takeoff_angle
					Prefincident = arr[0].incident_angle
				refdepths.append(phdepths[p])
				reftimes.append(arr[0].time-Preftime)
				reftakeoff.append(arr[0].takeoff_angle-Preftakeoff)
				refincident.append(arr[0].incident_angle-Prefincident)
				refslow.append((arr[0].ray_param-Prefslow)*np.pi/180.)
			depthspace=np.linspace(-100,1200,1300)
			# fit polynomials
			takeoff_poly=np.polyfit(refdepths[1:],reftakeoff[1:],3)
			takeoff=np.poly1d(takeoff_poly)
			slow_poly=np.polyfit(refdepths,refslow,4)
			slowness=np.poly1d(slow_poly)
			time_poly=np.polyfit(refdepths,reftimes,4)
			time=np.poly1d(time_poly)

			# save solutions to dictionary
			if not hasattr(seis[0],'conversions'):
				seis[0].conversions=dict()
			seis[0].conversions['prem']=dict()
			seis[0].conversions['prem']['depths']=depthspace
			seis[0].conversions['prem']['takeoff']=takeoff(depthspace)
			seis[0].conversions['prem']['slowness']=slowness(depthspace)
			seis[0].conversions['prem']['time']=time(depthspace)




			# interpolate latitude and longitudes  at the discontinuities
			# Unfortunately obpsy taup cannot do this...yet. So this will be slow
			discon=['P','P220s','P400s','P550s','P670s','P971s', 'P1171s']
			x=[0,220.,400.,550.,670.,971., 1171.]

			xtime=[0]
			xlat=[slat]
			xlon=[slon]
			for d in range(1,len(discon)):

				taup_660=['taup_pierce -mod /raid3/sdat2/Parra/prem_added_discon_taup.nd -h '+ str(depth) + ' -sta '+ str(slat)+' ' +str(slon)+ ' -evt '+ str(elat) + ' ' + str(elon) +' -ph '+discon[d] + ' -Pierce ' + str(x[d])+',0 -nodiscon']
				out=subprocess.check_output(taup_660,shell=True)
				t=out.split()
				xtime.append(float(t[-3])-float(t[-8]))
				xlat.append(float(t[-7]))
				xlon.append(float(t[-6]))

			traveltime_poly=np.polyfit(x,xtime,4)
			traveltime=np.poly1d(traveltime_poly)
			lats_poly=np.polyfit(x,xlat,4)
			lats=np.poly1d(lats_poly)
			lons_poly=np.polyfit(x,xlon,4)
			lons=np.poly1d(lons_poly)


			# convert this trace to depths and save
			depths=np.interp(RFtrace['time'],seis[0].conversions['prem']['time'],seis[0].conversions['prem']['depths'])
			latitudes=lats(depthspace)
			longitudes=lons(depthspace)

			seis[0].conversions['prem']['depthsfortime']=depths
			seis[0].conversions['prem']['latitudes']=latitudes
			seis[0].conversions['prem']['longitudes']=longitudes
			seis[0].conversions['prem']['latfortime']=np.interp(RFtrace['time'],seis[0].conversions['prem']['time'], latitudes)
			seis[0].conversions['prem']['lonfortime']=np.interp(RFtrace['time'] ,seis[0].conversions['prem']['time'],longitudes)

			seis.write(stalist[i],format='PICKLE')
			print ('completed RF')
		else:
                        print('problematic degrees')
			#os.remove(stalist[i])               
		#except:
		#  print 'I am a failure'


