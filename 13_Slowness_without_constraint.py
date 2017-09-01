'''
Slowness_Stack.py
Used to distinguish which signals in the time or depth against epicentral angle stack are converted phases and which signals are multiples.
Multiples come from shallower angles, therefore the velocity is lower and the slowness is +ve wrt the direct P wave.
Converted phases come from steeper angles, therefore the velocity is higher and the slowness is -ve wrt the direct P wave.

This script forms a plot of slowness against time, looking at a specfic epicentral angle (60deg).

'''
#example: python3 13_Slowness_without_constraint.py RF_auto_check_2 all 0
#example: python3 13_Slowness_without_constraint.py RF_auto_check_2 TA.D15A 0
#[subdirectory] [station] [option]
root = '/raid3/sdat2/Parra/'
Failed_at_List = []
epi_ref = 55
slowness_max = 0.8
slowness_min =-1
upper_limit = 101 #* 2
lower_limit = -100 #* 2
np_vertical = upper_limit-lower_limit
np_horizontal  = 1751
option = 0
###slowness is s/deg 
#-------------------------------Import required modules-------------------------------------


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

if len(sys.argv) >1:
    subdirectory = str(sys.argv[1])
else:
    subdirectory = 'RF_auto_check_2'
if len(sys.argv) >2:
    if str(sys.argv[2]) == 'all':
        station = '*'
    else:
        station = str(sys.argv[2])
if len(sys.argv) >3:
    option = int(sys.argv[3])



#Set size of image
fig = plt.figure(figsize=(13,4.5))


#--------------------------Set up array for the STACK-----------------

#array of zeros, slowness stack high and 2*length of RF wide

STACK = np.zeros([np_vertical,np_horizontal]) #initially 201,1751


#-------------------------------Loop through stations---------------------------------------   

direc = root +'DataRF'
filt = 'jgf1'
stadirs = glob.glob(direc+'/'+station )######*')


#loop through stations
for stadir in stadirs:
    print (stadir)
    stalist = glob.glob(stadir+'/'+subdirectory+'/*.PICKLE')

    #loop through events
    for i in range(len(stalist)):
        try:
            seis = read(stalist[i], format = 'PICKLE') #read all the seimsograms
            print (stalist[i])


    #-------------------------------Make an array of slowness----------------------------------       

            #List values between -1.0 and +1.0 in steps of 0.1 - slowness in s/deg
            a = range(lower_limit,upper_limit,1) #initially -100
            b = [x / 100. for x in a]   #

            for j in a: # j is a list index

                s = b[j] #(s for slowness)

                #need to extract the epicentral distance

                
                epi_RF = seis[0].stats['dist']
                epi_dist = epi_RF - epi_ref

                #need to calculate delta t (timeshift)

                timeshift = s * epi_dist # timeshift generated from slowness

                #print ('slowness (s): %r' %s)

                #print ('epi_dist: %r' %epi_dist)

                #print ('timeshift: %r' %timeshift)


    #--------convert the RF into the right format--------------


                #get the amplitude of the RF 
                RF_amp = getattr(seis[0],filt)['iterativedeconvolution']

                #shows plot of RF_amp
                #plt.plot(RF_amp)
                #plt.show()

                #create line of zeros length of which is 40s of 0s either side of the RF
                #RF = getattr(seis[0],filt)['iterativedeconvolution']
                #40s either side is  80/float(seis[0].stats['delta'] (80/sampling time (0.1s))
                RFtemp = np.zeros(len(getattr(seis[0],filt)['iterativedeconvolution'])+80/float(seis[0].stats['delta'])) # Delta is time steps # Make it as long as the RF + some ammount

                #shows plot of RFtemp (line at 0, 2551 long at this stage)
                #plt.plot(RFtemp)
                #plt.show()            

                #Take the middle section of 0s of RFtemp and make it equal to RF_amp
                RFtemp[40/float(seis[0].stats['delta']):40/float(seis[0].stats['delta'])+len(getattr(seis[0],filt)['iterativedeconvolution'])] = RF_amp                

                #shows plot of RFtemp (now 2551 long, with RF_amp present in the middle of 0s)
                #plt.plot(RFtemp)
                #plt.show()


    #------------set up timeshift of sample----------------------

                timeshift_sample = int(timeshift/float(seis[0].stats['delta'])) #timeshift generated from slowness now into sample timeshift


    #--------set up slowness stack-------------------------            

                #add to previous stack RF signal which has been timeshifted
######### ACTUAL STACKING HERE #############################

                lower_time_limit = int(40/float(seis[0].stats['delta']) + timeshift_sample)
                upper_time_limit = int(40/float(seis[0].stats['delta']) + timeshift_sample + len(getattr(seis[0],filt)['iterativedeconvolution']))
                if upper_time_limit > len(RFtemp):
                    upper_time_limit=len(RFtemp)
                '''
                if len(RFtemp) != np_horizontal:
                    print('length problem',len(RFtemp))
                    '''
                if option==0:
                    STACK[j,0:len(RFtemp)] +=  RFtemp[lower_time_limit : upper_time_limit]
                elif option==1:
                    for index in range(len(RFtemp)):
                        if lower_time_limit+index>=0 and lower_time_limit+index<np_horizontal:
                            STACK[j,index]+=RFtemp[lower_time_limit+index]
                elif option==2:
                    for index in range(400 + timeshift_sample,400 + timeshift_sample + len(getattr(seis[0],filt)['iterativedeconvolution'])):
                        if index>=400 and index<=np_horizontal:
                            Stack[j,index-400]+=RFtemp[index]
                            
                #STACK[j,:] +=  RFtemp[40/float(seis[0].stats['delta']) + timeshift_sample :]
                #STACK[j,:] +=  RFtemp[ : 40/float(seis[0].stats['delta']) + timeshift_sample + len(getattr(seis[0],filt)['iterativedeconvolution'])]
                #STACK[j,:] += RFtemp[40/float(seis[0].stats['delta']) + timeshift_sample : 40/float(seis[0].stats['delta']) + timeshift_sample + len(getattr(seis[0],filt)['iterativedeconvolution'])]

########################################################
        except:
            Failed_at_List.append(stalist[i])
            print('Failed')

                

#-------------need to normalise trace-------------------------

NORMALIZATION = 0.075 #0.075
STACK = STACK / np.max(np.abs(STACK))
STACK = STACK/NORMALIZATION

#---------------------Plot Predicted Travel Times and Slowness of converted phases-----------------

#Read in the predicted travel time and slowness differences from the appropriate file
data = np.genfromtxt(root +'/Travel_Times_Slowness/TTS_Pds_'+str(epi_ref)+'.dat', delimiter='\t')

#Get the travel time difference, set as x, and the slowness difference, set as y
x = data[:,1]
y = data[:,2]

#Plot the curves on the stack
plt.plot(x,y)
plt.annotate('Pds',xy=(136,-0.57))


#---------------------Plot Predicted Travel Times and Slowness of PPvdp-----------------

#Read in the predicted travel time and slowness differences from the appropriate file
data = np.genfromtxt(root +'Travel_Times_Slowness/TTS_PPvdp_'+str(epi_ref)+'.dat', delimiter='\t')

#Get the travel time difference, set as x, and the slowness difference, set as y
x = data[:,1]
y = data[:,2]

#Plot the curves on the stack
plt.plot(x,y)
plt.annotate('PPvdp',xy=(110,0.63)) 


#---------------------Plot Predicted Travel Times and Slowness of PPvds-----------------

#Read in the predicted travel time and slowness differences from the appropriate file
data = np.genfromtxt(root + 'Travel_Times_Slowness/TTS_PPvds_'+str(epi_ref)+'.dat', delimiter='\t')

#Get the travel time difference, set as x, and the slowness difference, set as y
x = data[:,1]
y = data[:,2]

#Plot the curves on the stack
plt.plot(x,y)
plt.annotate('PPvds',xy=(137,0.17))


#---------------------Plot Predicted points for discontinuities-----------------

#Read in the predicted travel time and slowness differences from the appropriate file
data = np.genfromtxt(root + '/Travel_Times_Slowness/TTS_Pds_'+str(epi_ref)+'.dat', delimiter='\t')

#410km

#Get the travel time difference, set as x, and the slowness difference, set as y
x = data[3,1]
y = data[3,2]

#Plot the curves on the stack
plt.plot(x,y, marker="x", color='black', markersize=8, markeredgewidth=1.6)
plt.annotate('P410s',xy=(45.2,-0.04))

#660km

#Get the travel time difference, set as x, and the slowness difference, set as y
x = data[5,1]
y = data[5,2]

#Plot the curves on the stack
plt.plot(x,y, marker="x", color='black', markersize=8, markeredgewidth=1.6)
plt.annotate('P660s',xy=(69.4,-0.13))

#1000km

#Get the travel time difference, set as x, and the slowness difference, set as y
x = data[8,1]
y = data[8,2]

#Plot the curves on the stack
plt.plot(x,y, marker="x", color='black', markersize=8, markeredgewidth=1.6)
plt.annotate('P1000s',xy=(97.5,-0.29))


#-----------------plot up stack----------------------------

#Plotting command 1 ( values, colourmap, min and max values)

#plt.pcolor(STACK , cmap ='seismic', vmin=-NORMALIZATION, vmax=NORMALIZATION)

#Plotting using contourf (time_axis (RF time) , slowness_range, slowness_matrix, contour_levels , colourmap , extend (extend grid if data lies outside range)

contour_levels = np.arange(-.3,.301,.03)  #(-1.,1.01,.1) (min,max,interval)
#########Actual Plotting here############################
cs = plt.contourf(getattr(seis[0],filt)['time'],b,STACK[:len(getattr(seis[0],filt)['time'])],contour_levels, cmap=plt.cm.seismic, extend="both")
#########################################################
#Set axes limits
plt.ylim(slowness_min,slowness_max)
plt.xlim(0,150)

#Axes labels
plt.ylabel ('Slowness (s/deg)')
plt.xlabel ('Time (s)')

#Graph title and details
plt.suptitle('Slowness Stack at subdirectory = '+subdirectory + '  limited to station: '+station)

plt.show()

print('Failed at:\n', Failed_at_List)
