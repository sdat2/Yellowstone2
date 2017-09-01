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
import math

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
filt = 'jgf1'
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

step = 2; max_epi=90; min_epi=30;epi_steps=(max_epi-min_epi)/step+1;counter=np.zeros([epi_steps]) ###

for stadir in stadirs:
    stalist= glob.glob(stadir+'/'+subdirectory+'/*.PICKLE')
    for i in range(len(stalist)):
        print(stalist[i])
        try:
            seis = read(stalist[i],format ='PICKLE')
            epi_diff = - epi_ref + seis[0].stats['dist'] # see Jenny's thesis page 38
            RF = getattr(seis[0],filt)['iterativedeconvolution']
            epi_dist=seis[0].stats['dist']; epi_loc=(round((epi_dist-30)/step));counter[epi_loc]+=1 ###
            
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
fig = plt.figure(figsize=(12,4.5))
ax1 = fig.add_subplot(121) ###
contour_levels = np.arange(-0.05,0.05,.002)#Ptime*10+Min_Time*10) # (min,max,interval)(-.3,.301,.03)
cs = plt.contourf(time,s,stack,contour_levels, cmap=plt.cm.seismic, extend="both")


########################First Draft of Slowness Weighting factor calculator##################################
Target_Time = (Max_Time+Min_Time)/2###
import scipy
from scipy.interpolate import interp1d
data = np.genfromtxt(root + '/Travel_Times_Slowness/TTS_Pds_'+str(epi_ref)+'.dat', delimiter='\t')
x = data[:,1]; y = data[:,2] #curve
f = interp1d(x,y,kind='cubic')
L_C_Slowness = f(Target_Time)
Target_Index= round((Max_Time-Min_Time)/2*10)
Target_Slice= abs(-stack[:,Target_Index])
print("Target_Time", Target_Time, "Target_Index ", Target_Index, "Target_Slice", Target_Slice)
#S_Upper, from index -0.15*100 - S_Lower*100 to that +16, from that +16 to that +31
Lm=0;Lc=0; Lower_Slowness_Index = round(-(0.15+S_Lower)*100); L_Max =0
print(Lower_Slowness_Index)
for a in range(Lower_Slowness_Index,Lower_Slowness_Index+16):
    Lc += Target_Slice[a]; Lm+= Target_Slice[a+15]
for b in range(Lower_Slowness_Index,Lower_Slowness_Index+30):
    #print(b,L_Max)
    if Target_Slice[b] > L_Max:
        L_Max=Target_Slice[b]; L_Max_Index=b
L_Max_Slowness=(L_Max_Index-Lower_Slowness_Index)/100-0.15
print('L_Max_Index',L_Max_Index)
print('Lc \t',Lc ,'Lm \t', Lm)
Lmaxm = 0; 
for a in range(Target_Index-20, Target_Index+20):
    Lm_Temp = 0 
    for b in range(0,15,1):
        Lm_Temp +=abs(stack[16+Lower_Slowness_Index+b,a])
    if Lm_Temp > Lmaxm: Lmaxm=Lm_Temp; Lmaxm_Index = a; Lmaxm_Time=Min_Time+Lmaxm_Index/10
print('Lmaxm=\t', Lmaxm, 'Index of Lmaxm =\t', Lmaxm_Index, 'Time=', Lmaxm_Time)
w2 = math.exp(-Lmaxm/Lc)
print('w2=',w2)
Sigma_Slowness_Simple=0; Normaliser = 0
for i in range(len(Target_Slice)):
    Slowness_Temp = -0.15 + i*0.01
    Normaliser += Target_Slice[i]
    Sigma_Slowness_Simple += Target_Slice[i]*((Slowness_Temp-L_Max_Slowness)**2)
Sigma_Slowness_Simple=(Sigma_Slowness_Simple/Normaliser)**(0.5)
w1 = math.exp(-((L_C_Slowness-L_Max_Slowness)**2)/((2*Sigma_Slowness_Simple)**2))*math.exp(-Lm/Lc)
if w2 > 1:
    w2 = 1
print('w1=', w1)
SW_Factor=w1*w2
print('SW_Factor=',SW_Factor)
plt.plot([Target_Time-2,Target_Time-2],[S_Lower,S_Upper],color='yellow')
plt.plot([Target_Time+2,Target_Time+2],[S_Lower,S_Upper],color='yellow')
plt.plot([Target_Time,Target_Time],[0,0.15],color='red')
plt.plot([Target_Time,Target_Time],[-0.15,0],color='purple')
plt.plot([Lmaxm_Time,Lmaxm_Time],[0,0.15],color='orange')
plt.annotate('Lm,max',xy=(Lmaxm_Time-1.4,0.03), color='orange')
plt.plot([Min_Time,Max_Time],[0,0], color = 'white')
plt.plot([Target_Time],[L_Max_Slowness],marker='x', color='green',markersize=9,markeredgewidth=1.6)
plt.annotate('Po',xy=(Target_Time+0.4,L_Max_Slowness), color='green')
plt.plot([Target_Time],[L_C_Slowness],marker='x',color='blue',markersize=9,markeredgewidth=1.6)
plt.annotate('Pc',xy=(Target_Time+0.4,L_C_Slowness),color = 'blue')
plt.plot([Target_Time, Target_Time],[L_Max_Slowness-Sigma_Slowness_Simple,L_Max_Slowness+Sigma_Slowness_Simple],marker='_', color='green',markersize=9,markeredgewidth=1.6)
plt.annotate('w1 = '+"{:.2f}".format(w1),xy=(Target_Time+5,0.03), color='black')
plt.annotate('w2 = '+"{:.2f}".format(w2),xy=(Target_Time+5,0.00), color='black')
plt.annotate('SWF = '+"{:.2f}".format(SW_Factor),xy=(Target_Time+5,-0.03), color='black')
#######################################################################################

############Conversion Plotting##################
data = np.genfromtxt(root + '/Travel_Times_Slowness/TTS_Pds_'+str(epi_ref)+'.dat', delimiter='\t')
x = data[:,1]; y = data[:,2] #curve
plt.plot(x,y)
plt.annotate('Pds',xy=(20,-0.07))
x = data[3,1]; y = data[3,2]#410km
plt.plot(x,y, marker="x", color='black', markersize=8, markeredgewidth=1.6)
plt.annotate('P410s',xy=(x+0.1,y))
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

print('Failed at:\n', Failed_at_List)


ax2=fig.add_subplot(122)###
#Loop through the bins
for n in range(len(counter)):
    mindist=(n*step)+30
    maxdist=mindist+step

    #Plot rectangle of histogram ((startx,,starty),width, height))
    ax2.add_patch(patches.Rectangle((mindist, 0), step, counter[n],facecolor='#AF7AC5',edgecolor='0.3'))

#Axes labels
plt.ylabel('Number of RFs')
plt.xlabel('Epicentral Distance (degrees)')

#Axes limits
plt.gca().set_xlim([30,90])
plt.gca().set_ylim([0,np.nanmax(np.abs(counter[:]))])

#Subplot arrangement
#ax2.xaxis.tick_top()
#ax2.xaxis.set_label_position('top') 
plt.subplots_adjust(hspace=0)

plt.show()
