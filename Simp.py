import glob
import os
import obspy
import pickle
from obspy import read

def foldercheck(folder):
    PickleList = glob.glob('/raid3/sdat2/Parra/DataRF/*'+folder+'/*.PICKLE')
    print('In ', folder, ' there are ', len(PickleList), 'pickles')
    if len(PickleList) != 0:
        print('The first pickle is called', PickleList[0])
        try:
            a = read(PickleList[0],format='PICKLE')
            print('This Folder is clean')
        except:
            print('wrong python for this folder')

#foldercheck('/Originals')
#foldercheck('/Processed_originals')
foldercheck('')
foldercheck('/Fresh_copies_2')
foldercheck('/tff3_added')
foldercheck('/tff3_auto_check_2')
foldercheck('/tff3auto_removed')
foldercheck('/RF_added')
foldercheck('/Fresh_copies')
foldercheck('/Travel_time_added')
foldercheck('/RF_auto_checked')
foldercheck('/RF_auto_check_2')

#foldercheck('/RF_auto_check_3')
#foldercheck('/RF_auto_check_4')
foldercheck('/RF_auto_removed')
