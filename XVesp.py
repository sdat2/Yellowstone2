'''
Vespagram.py. An attempt at making the most efficient program for slowness stacking possible.
'''
import obspy
from obspy import read
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import glob
import time
import sys
import pickle
import numpy as np

root = '/raid3/sdat2/Parra/'
if len(sys.argv) >6:
    subdirectory = str(sys.argv[6])
else:
    subdirectory = 'RF_auto_check_2'
if len(sys.argv) >1:
    if str(sys.argv[1]) == 'all': station = '*'
    else: station = str(sys.argv[1])
if len(sys.argv) >2:
    Min_Time=int(sys.argv[2])
else:
    Min_Time=0
if len(sys.argv) >3:    
    Max_Time= int(sys.argv[3])
else:
    Max_Time=60
if len(sys.argv) >4:    
    S_Lower= float(sys.argv[4])
else:#bug means that only -0.15,-0.25,-0.35 etc. work
    S_Lower=-0.15
if len(sys.argv) >5:    
    S_Upper= float(sys.argv[5])
else:
    S_Upper=0.15  
    

direc = root +'DataRF'
Ptime=25
Stacktime = Max_Time-Min_Time
Vertical = int((S_Upper-S_Lower)*100+1); Horizontal=Stacktime*10 #The length of a list
stack = np.zeros([Vertical,Horizontal]) #The main stack itself
s = [x/100 for x in range(int(100*S_Lower),int(100*S_Upper+1),1)] # a slowness list (seconds/degree)
time = [x/10 for x in range(Min_Time*10,Max_Time*10,1)] # a time list (seconds) given that Ptime at 25 seconds
Failed_at_List = []
epi_ref = 55 # degrees
RF_Stack_Number=0
stadirs = glob.glob(direc+'/'+station)

for stadir in stadirs:
    stalist= glob.glob(stadir+'/'+subdirectory+'/*.PICKLE')
    for i in range(len(stalist)):
        print(stalist[i])
        try:
            seis = read(stalist[i],format ='PICKLE')
            epi_diff = - epi_ref + seis[0].stats['dist'] # see Jenny's thesis page 38
            RF = getattr(seis[0],filt)['iterativedeconvolution']
            for j in range(len(s)):
                timeshift = s[j]*epi_diff
                indexshift = int(timeshift*10)
                for k in range(0,Horizontal,1):
                    if k in range(0,Horizontal) and (k+indexshift+Ptime*10+Min_Time*10) in range(0,len(RF)):
                        stack[j,k] += RF[k+indexshift+Ptime*10+Min_Time*10] #Event is at 20seconds into RF
            RF_Stack_Number+=1
            #print(getattr(seis[0],filt)['time'][0])
        except: print(sys.exc_info); Failed_at_List.append(stalist[i])
        
#####Main Plotting#########
stack = stack / RF_Stack_Number
fig = plt.figure(figsize=((Max_Time-Min_Time)/10,4.5))
contour_levels = np.arange(-0.05,0.05,.002)#Ptime*10+Min_Time*10) # (min,max,interval)(-.3,.301,.03)
cs = plt.contourf(time,s,stack,contour_levels, cmap=plt.cm.seismic, extend="both")


############Conversion Plotting##################
data = np.genfromtxt(root + '/Travel_Times_Slowness/TTS_Pds_'+str(epi_ref)+'.dat', delimiter='\t')
x = data[:,1]; y = data[:,2] #curve
plt.plot(x,y)
plt.annotate('Pds',xy=(20,-0.07))
x = data[3,1]; y = data[3,2]#410km
plt.plot(x,y, marker="x", color='black', markersize=8, markeredgewidth=1.6)
plt.annotate('P410s',xy=(45.2,-0.04))
x = data[5,1]; y = data[5,2] #660km
plt.plot(x,y, marker="x", color='black', markersize=8, markeredgewidth=1.6)
plt.annotate('P660s',xy=(69.4,-0.13))
x = data[8,1];y = data[8,2] #1000km
plt.plot(x,y, marker="x", color='black', markersize=8, markeredgewidth=1.6)
plt.annotate('P1000s',xy=(103,-0.33))


###PPVdp####
data = np.genfromtxt(root +'Travel_Times_Slowness/TTS_PPvdp_'+str(epi_ref)+'.dat', delimiter='\t')
x = data[:,1]; y = data[:,2] #curve
plt.plot(x,y)
plt.annotate('PPvdp',xy=(23,0.1)) 


##PPvds###
data = np.genfromtxt(root + 'Travel_Times_Slowness/TTS_PPvds_'+str(epi_ref)+'.dat', delimiter='\t')
x = data[:,1]; y = data[:,2] #curve
plt.plot(x,y)
plt.annotate('PPvds',xy=(33.5,0.07))


#########Main Plotting######
plt.ylabel('Slowness (s/deg)')
plt.ylim(S_Lower,S_Upper)
plt.xlim(Min_Time,Max_Time)
plt.xlabel('Time (s)')
plt.suptitle('Slowness Stack at subdirectory = '+subdirectory + '  limited to station: '+station)
plt.show()

print('Failed at:\n', Failed_at_List)
