'''
Station_map.py a initially written by Kiaran (kg382) and adapted by Simon (sdat2) produced to make a nice GMT map
Creates a file containing three columns: The name of the station, station lat, station lon'
Runs through the first signal in each station and takes the lat, lon of the station.
-------------------------------------
'''
file_name = 'Station_map.py'

import obspy
from obspy import read
from obspy.core import Stream
from obspy.core import trace
import os.path
import time
import glob
import shutil
import numpy as np
from obspy import UTCDateTime
import subprocess
import pickle
import sys

PickleCounter = 0 #This is a global variable to count the pickles
Empty_Stations = [] #If I can remove these from the download this could save time without compromising data download
Useful_Stations = []
U_Dict = {}

direc = '/raid3/sdat2/DataRF' #My data directory
filt = 'jgf1' #Not sure actually used
stadirs = glob.glob('DataRF/*')
#stadirs = glob.glob(direc+'/*') #Look through the right directory and collect the directories

#------------------------------output file stuff----------------------------------

#name of output file to save stations to
output_file = 'Output_Files/' + 'Station_Map.txt'
output_file1 = 'Output_Files/' + 'Lat_Long_Stations.txt'
g = 'Output_Files/' + 'Name_Lat_Long_number.txt'

print('Station_map.py program running, planning to print data to:')
print(output_file)
print('We should be getting data from:')
print(direc)
print('There seem to be', len(stadirs), 'standard directories (stadirs)')


#open the file you are going to save into (w means you can write onto it)
output_file_write = open(output_file, 'w')
output_file_write1 = open(output_file1, 'w')
outdy = open(g,'w')

#-------------------------------Loop through stations---------------------------------------   

#loop through stations
for stadir in stadirs:
        try:
                #we expect each station to produce 4 lines of terminal output
                print("STATION:", stadir)
                stalist = glob.glob(stadir+'/*/*.PICKLE')
                #This line is directly copied from 2_rotate_data_NE_RT, so hopeful
                #should work
                print('We made a stalist with', len(stalist), 'Pickles')
                if (len(stalist) == 0):
                        Empty_Stations.append(stadir)
                        print('station empty')
                else:
                        seis = read(stalist[0], format = 'PICKLE')
                        station = seis[0].stats['network']+'.'+seis[0].stats['station']
                        print(station)
                        #we take the data from the first pickle
                        Useful_Stations.append(station)
                        U_Dict[station] = {'station':seis[0].stats['station'],'network':seis[0].stats['network']\
						,'seismograms':len(stalist),'latitude':seis[0].stats['stla']\
						,'longitude':seis[0].stats['stlo']}
                        PickleCounter = PickleCounter + len(stalist)
                        #increment to count successes
                        #look at first event in each station
                        #only need to search first pickle
                        lat = seis[0].stats['stla']
                        lon = seis[0].stats['stlo']
                        #then we take out the latitude and longitude
                        print(lat, lon) #print latitude and longitude
                        #create the actual output file to be graphed
                        output_file_write.write(str(station)+'\t')
                        output_file_write.write(str(lon)+'\t')
                        output_file_write.write(str(lat)+'\n')
                        output_file_write1.write(str(lon)+'\t')
                        output_file_write1.write(str(lat)+'\n')
                        outdy.write(str(station)+'\t')
                        outdy.write(str(lon)+'\t')
                        outdy.write(str(lat)+'\t')
                        outdy.write(str(len(stalist))+'\n')
                print('Whole loop completed')
        except:
                print('The loop broke before completion')
                print(sys.exc_info())

#Close the file of data
output_file_write.close()
output_file_write1.close()
outdy.close()

print('The file was written and', PickleCounter, 'Pickles were found')

print('I think that there are',len(Empty_Stations),' empty stations:', Empty_Stations)
f =  open('Output_Files/Empty_Stations.txt', 'w')
for item in Empty_Stations:
        f.write(item + '\n')

f.close()
        
# print U_Dict to pickle file

pickle.dump( U_Dict, open("Output_Files/U_Dict.p","wb"))



print('I think that there are',len(Useful_Stations),' useful stations:', Useful_Stations)

h = open('Output_Files/Non_Empty_Stations.txt', 'w')
for item in Useful_Stations:
        h.write(item + '\n')

h.close()

print('My useful dictionary has', len(U_Dict), 'entries')
Useful_Networks = {}

for Entry in U_Dict:
        net = U_Dict[Entry]['network']
        if net  not in Useful_Networks:
                Useful_Networks[net] = {'stations':0,'seismograms':0}
        Useful_Networks[net]['stations'] += 1
        Useful_Networks[net]['seismograms'] += U_Dict[Entry]['seismograms']

#Produce a sorted list of seismometers by number of seismograms contained.
Station_Sorted = [] # an empty list to fill with the names of the stations sorted

# a list full of unsorted names
Initial = []
for Entry in U_Dict:
        Initial.append(Entry)

#Manually linearly sorting them
a = len(Initial) #should lose one member per iteration
for i in range(a):
        Max_Value = 0 # reset to 0 with each loop
        for j in range(len(Initial)): # equivalent to a - i
                PICKLEs = U_Dict[Initial[j]]['seismograms']
                if PICKLEs > Max_Value:
                        Max_Value = PICKLEs
                        Current_Highest = Initial[j]

        Station_Sorted.append(Current_Highest) # add the next highest to the sorted list
        Initial.remove(Current_Highest) # remove next highest form the unsorted list

        #Write out a sorted list of pickles now using U_Dict
out_file = '/raid3/sdat2/Parra/Output_Files/Sorted_Useful_Seismometers.txt'
splat = open(out_file, 'w')
for i in range(len(Station_Sorted)):
        f = Station_Sorted[i]
        dat = str(i)+'\t'+U_Dict[f]['network'] +'\t'+U_Dict[f]['station']+'\t'+str(U_Dict[f]['longitude'])+'\t'+str(U_Dict[f]['latitude'])+'\t'+str(U_Dict[f]['seismograms'])
        splat.write(dat + '\n')
splat.close()


#write a small file containing a summary of the Networks as they stand
out_file = '/raid3/sdat2/Parra/Output_Files/Useful_Networks.txt'
blah = open(out_file, 'w')
blah.write('The Networks that were downloaded (unsorted):')

for Net in Useful_Networks:
        dat = Net +'\t'+ str(Useful_Networks[Net]['stations']) +'\t' + str(Useful_Networks[Net]['seismograms'])
        print(dat)
        blah.write(dat + '\n')

blah.close()


for Net in Useful_Networks:
        output_file='/raid3/sdat2/Parra/Output_Files/Network_'+Net+'.txt'
        blot = open(output_file, 'w')
        blot.write('For the Network '+ Net + ' there are ' + str(Useful_Networks[Net]['stations']) +' stations\n') 
        for station_no in range(len(Station_Sorted)):
                f = Station_Sorted[station_no]
                if U_Dict[f]['network'] == Net:
                        dat = str(station_no) +'\t'+U_Dict[f]['station']+'\t'+str(U_Dict[f]['longitude'])+'\t'+str(U_Dict[f]['latitude'])+'\t'+str(U_Dict[f]['seismograms'])
                        blot.write(dat+'\n')
        blot.close()
