# common conversion point stacking
import numpy as np
import mega_volume_2017 as mega_volume
import glob
import sys

root = '/raid3/sdat2/Parra/'
subdirectory = 'tff3_auto_check_2'
if len(sys.argv)>=2:
    subdirectory = str(sys.argv[1])
name = subdirectory#'fulldataset_check_2'
rffilter='tff3'
conversion='SL2014'
factor=2. # doubling the fresnel zone width, smoothing factor

#select the lat, lon and depth boundaries
extension = 2.
lonmin=-118. - extension -2
lonmax=-103. + extension
lonrez=(lonmax-lonmin)*2.+1. # every 0.5 degrees
latmin=40. - extension -2
latmax=48. + extension
latrez=(latmax-latmin)*2.+1. # every 0.5 degrees
depmin=60
depmax=1200
deprez=(depmax-depmin)/2. # every 2 km


CCP=mega_volume.ccp_volume()#

# First time start volume, otherwise comment out
CCP.start_empty_volume(name= name,filter=rffilter, conversion=conversion, factor=factor, lonmin=lonmin,lonmax=lonmax,lonrez=lonrez,latmin=latmin, latmax=latmax, latrez=latrez, depmin = depmin, depmax=depmax, deprez=deprez)
# Uncomment after first time
#CCP.load_latest(name=name,filter=rffilter, conversion=conversion, factor=factor)


#make list of stations
direc = root+'DataRF' 
#make list of all events
stalist = glob.glob(direc+'/*/'+subdirectory+'/*.PICKLE')

#make empty array to add RFs to
rflist=stalist

#loop through events
#for j in range(len(stalist)):
#	print (stalist[j])
#	rflist.extend([line.strip() for line in open(stalist[j], 'r')])
CCP.addlist(rflist,name= name,filter=rffilter, conversion=conversion, factor=factor)
	



'''

# Stations that are finished


done = [] # none are done yet


# Here I have selected stations, but you can also loop through all stations.
sta=[] ####Need to add my good stations her
todo=[]



for i in range(len(sta)):#range(64):
    rflist=[]
    stalist=glob.glob('../Data/*'+sta[i]+'/good_RFs_jgf1.dat')
    if len(stalist)==0: 
            stalist=glob.glob('../DataOrfeus/*'+sta[i]+'/good_RFs_jgf1.dat') # if nothing in Data try in DataOrfeus
    if len(stalist)>0:
    # Currently I'm adding the receiver list for each station to the stack.
    # This means the stack gets written out more often, and if a station fails, not all previous work is lost.
    # However, it does take up a lot of space. So it is best to just save the final stack in the end and remove the others. 
       for j in range(len(stalist)):
            print(stalist[j])
            rflist.extend([line.strip() for line in open(stalist[j],'r')]   )  # the RF list is added to
       CCP.addlist(rflist,name= name,filter=rffilter, conversion=conversion, factor=factor) #the CCP object is called and added to

'''
