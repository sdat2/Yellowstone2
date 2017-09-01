import obspy
from obspy import read
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.pyplot as plt
from matplotlib import gridspec
#import plotly.plotly as py
#import plotly.plotly as py
#import plotly.tools as tls
import glob
import time
import sys
import pickle
import numpy as np
import scipy
import math
from scipy.interpolate import interp1d
root = '/raid3/sdat2/Parra/'; ###CHANGE TO YOUR ACCOUNT
epi_ref = 55 # degrees

def Vespagram_Creator(subdirectory='RF_auto_check_2', station='TA.D15A', S_Lower=-0.15, S_Upper=0.15, Min_Time=0, Max_Time=120):
    '''Creates a stack from the pickles'''
    direc = root +'DataRF' ; Failed_at_List =[] #To keep count
    Ptime=25; Stacktime = Max_Time-Min_Time #(RF has been cut so that it is 25 seconds into RF
    Vertical = int((S_Upper-S_Lower)*100+1); Horizontal=Stacktime*10 #The length of a list
    stack = np.zeros([Vertical,Horizontal]) #The main stack itself
    s = [x/100 for x in range(int(100*S_Lower),int(100*S_Upper+1),1)] #(increment 0.01 s/deg)
    time = [x/10 for x in range(Min_Time*10,Max_Time*10,1)] #(sampling rate 10 Hz)
    RF_Stack_Number=0 #counter for normalisation
    stadirs = glob.glob(direc+'/'+station)
    filt = 'jgf1' ### CHANGE TO YOUR FILTER
    for stadir in stadirs:
        stalist= glob.glob(stadir+'/'+subdirectory+'/*.PICKLE')
        for i in range(len(stalist)):
            print(stalist[i])
            try:
                seis = read(stalist[i],format ='PICKLE')
                epi_diff = - epi_ref + seis[0].stats['dist'] #        see Jenny's thesis page 38
                RF = getattr(seis[0],filt)['iterativedeconvolution']
                for j in range(len(s)):
                    timeshift = s[j]*epi_diff
                    indexshift = int(timeshift*10)
                for k in range(0,Horizontal,1):
                    if k in range(0,Horizontal) and (k+indexshift+Ptime*10+Min_Time*10) in range(0,len(RF)):
                        stack[j,k] += RF[k+indexshift+Ptime*10+Min_Time*10] #Actual stacking here
                    RF_Stack_Number+=1
            except: print(sys.exc_info); Failed_at_List.append(stalist[i])
    print('Failed at:\n', Failed_at_List)
    return stack/RF_Stack_Number ##normalises stack

def Window_Grabber(stack, Time, Min_Time):
    ''' Simply cuts the main vespagram to the Section around the target time '''
    Index = (Time-Min_Time)*10 # sampling rate 10 Hz
    window =stack[:,int(Index-20):int(Index+21)] # should produce an object 31 horizontal by 41 vertical
    return window # a small version of the stack

def SWF(window,pc):
    '''
This function should take in a 41 by 31 window of a vespagram, 
and predicted conversion slowness value for the central time, 
and output a dictionary of results related to the method outlined in Guan and Niu (2017)
'''
    SWfactor={'main':0,'w1':0,'w2':0,'p0':0}; Lm=0;Lc=0;Target_Slice= abs(window[:,20]);
    Lmaxm=0;Lm_Temp=0; Sigma_Slowness_Simple=0;Normaliser=0; L_Max=0; L_Max_Index = 0
    
    for a in range(41):#The supposed horizontal width of a window
        Lm_Temp = 0
        for b in range(0,15):
            Lm_Temp+=abs(window[16+b,a])
        if Lm_Temp > Lmaxm: Lmaxm = Lm_Temp;Lmaxm_Index=a; Lmaxm # searches window
        
    for b in range(0,15): Lc += Target_Slice[b]; Lm+=Target_Slice[b+16] # computes target slice
    
    for b in range(0,31): 
        if Target_Slice[b] > L_Max:
            L_Max=Target_Slice[b]; L_Max_Index=b
            
    L_Max_Slowness=(L_Max_Index)/100-0.15
    for i in range(len(Target_Slice)): # A hacky way of getting stdev
        Slowness_Temp = -0.15 + i*0.01
        Normaliser += Target_Slice[i]
        Sigma_Slowness_Simple += Target_Slice[i]*((Slowness_Temp-L_Max_Slowness)**2)
    Sigma_Slowness_Simple=(Sigma_Slowness_Simple/Normaliser)**(0.5)
    w1 = math.exp(-((pc-L_Max_Slowness)**2)/((2*Sigma_Slowness_Simple)**2))*math.exp(-Lm/Lc)
    w2 = math.exp(-Lmaxm/Lc)
    if w2 > 1: w2 = 1  ## see if statement in Guan and Niu
    SWfactor['main']= w1*w2; SWfactor['w1']=w1; SWfactor['w2']=w2;SWfactor['p0']=L_Max_Slowness
    return SWfactor

def Plot(stack,SW_Dict,Min_Time,Max_Time):
    '''Plots a) Main vespagram.  b) SWfactor,w1 & w2. c) Central RF with and without SWfactor'''











    t = np.arange(0.01, 5.0, 0.01)
    s1 = np.sin(2*np.pi*t)
    s2 = np.exp(-t)
    s3 = np.sin(4*np.pi*t)
    ax1 = plt.subplot(311)
    plt.plot(t, s1)
    plt.setp(ax1.get_xticklabels(), fontsize=6)
    ax2 = plt.subplot(312, sharex=ax1)    # share x only
    plt.plot(t, s2)
    plt.setp(ax2.get_xticklabels(), visible=False)     # make these tick labels invisible
    ax3 = plt.subplot(313, sharex=ax1, sharey=ax1)    # share x and y
    plt.plot(t, s3)
    plt.xlim(0.01, 5.0)
    fig = plt.gcf()
    plotly_fig = tls.mpl_to_plotly(fig)
    return

    ###main###
data = np.genfromtxt(root + '/Travel_Times_Slowness/TTS_Pds_'+str(epi_ref)+'.dat', delimiter='\t')
x = data[:,1]; y = data[:,2]; f = interp1d(x,y,kind='cubic') #creates a fair prediction of slowness
stack = Vespagram_Creator(subdirectory='RF_auto_check_2', station='TA.D15A', S_Lower=-0.15, S_Upper=0.15, Min_Time=0, Max_Time=120)
print(stack.shape)
SW_Dict = {}
print(Window_Grabber(stack,20,0).shape)
print(Window_Grabber(stack,20,0))
Min_Time = 0; Max_Time=120
for Time_ds in range(25,27): #range(int((Min_Time+2)*10),(Max_Time-2)*10):
    Time = Time_ds/10
    #L_C_Slowness = f(Time) 
    window = Window_Grabber(stack,Time,Min_Time)
    SW_Dict[Time]= SWF(window,f(Time))
    print(SWF(window,f(Time)))
#Plot(stack,SW_Dict,Min_Time,Max_Time)

