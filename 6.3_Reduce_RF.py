#Begin 6_auto_select_receiver_functions.py a program written by Sanne Cottaar (sc845@cam.ac.uk)
file_name = '6_auto_select_receiver_functions.py'

##### AUTOMATED QUALITY CONTROL SCRIPT FOR RF ANALYSIS#################
# Given large quantity of data in box, this must be used instead of manual quality control.
# This script looks at computed RF and removes low quality ones based on set criteria:
 
# -if maximum value of the Receiver function is actually between 24 and 26 seconds from the P wave arrival (ie P wave is largest arrival)
# -if 60% of SV is recovered (when RF in reconvolved with Z)
# -if there are no strong peaks before and no huge peaks after the main P arrival

# poor RF are moved to a sub folder and a list of automatically slected RF is produced:selected_RFs_jgf1.dat
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
import receiver_function as rf
import subprocess
import scipy
from scipy import interpolate
import pickle


#negative length of file name in characters +1
#****
file_char_len=-51
#****
direc = '/raid3/sdat2/Parra/DataRF'
flag = 'SV' # current options
filt= 'jgf1'
Fail_Count= {'Range':0,'fitid':0,'tooshort':0,'Noise_before':0,'Noise_after':0,'Minamp':0}

fitmin = 80 # Minimum 60 percent of radial compoment should be fit (after reconvolving the RF with the vertical component
noisebefore = 0.3 # There should be no peaks before the main P wave which are more than 30% of the amplitude of the Pwave
noiseafter = 0.3# There should be no peaks after the main P wave which are more than 70% of the amplitude of the Pwave
minamp = 0.04 # There should be signals after the P wave which are at least 4% of the main P wave. Otherwise something has gone wrong...
#It may be possible to strengthen some of these requirements

stadirs= glob.glob(direc+'/*')
print('Looked in',direc+'/*',' and found ',len(stadirs), ' directories' ) 
for stadir in stadirs:
    # This is where selected data will be listed.
    stalist=glob.glob(stadir+'/RF_auto_checked/*.PICKLE')
    #Make directories for rubbish data if it doesn't already exist

    new_direc= stadir+'/RF_auto_check_3'
    if not os.path.exists(new_direc):
        os.makedirs(new_direc)
    #c=0 #I think this variable is unused
    # Loop through receiver functions
    for i in range(len(stalist)):
        print('checking quality', i+1,"/",len(stalist), stalist[i])
        if os.path.isfile(stalist[i]):
            seis=read(stalist[i],format='PICKLE')
            dist=seis[0].stats['dist']
            if dist>30 and dist <90: # If fails download faulty
                RF=trace.Trace()
                findRF = getattr(seis[0],filt)
                RF.data= np.real(findRF['iterativedeconvolution'])
                RF.data=RF.data/np.max(np.abs(RF.data))
                fitid=findRF['iterativedeconvolution_fit']
                print(fitid)
                # Test if maximum value of the Receiver function is actually between 24 and 26 seconds from the P wave arrival
                indm=np.argmax(np.abs(RF.data))
                print(indm)
                withinrange= True if (indm>230 and indm <270) else False #check between 23-27s
                if withinrange:
                    # If 60% of SV is recovered, and RF passes the peak test, save the
                    if fitid>fitmin:
                        # test if there are no strong peaks before and no huge peaks after the main arrival
                        try:
                            if np.max(np.abs(RF.data[0:indm-40]))<noisebefore:
                                if np.max(np.abs(RF.data[indm+200:indm+1200]))<noiseafter:
                                    if np.max(np.abs(RF.data[indm+20:-1]))>minamp:
                                        print('good station')
                                        shutil.copy(stalist[i],new_direc)
                                    else:
                                        Fail_Count['Minamp']+=1
                                else:
                                    Fail_Count['Noise_after']+=1
                            else:
                                Fail_Count['Noise_before']+=1
                        except:
                            Fail_Count['tooshort']+=1
                    else:
                        Fail_Count['fitid']+=1
                else:
                    Fail_Count['Range']+=1



print('Finished Sorting')
print('failed at Minamp:', Fail_Count['Minamp'])
print('failed at noise before:', Fail_Count['Noise_before'])
print('failed at noise after:', Fail_Count['Noise_after'])
print('failed due (probably) to length being to short: ', Fail_Count['tooshort'])
print('failed at fitid:', Fail_Count['fitid'])
print('failed at withinrange:', Fail_Count['Range'])
