# common conversion point stacking

#import mega_volume_plottingroutines_2017 as mega_volume
import My_Plotting_Routines as mega_volume
import glob
import matplotlib
#matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import sys
import os

root = '/raid3/sdat2/Parra/'
homedirec = '/home/sdat2/'

#EXAMPLE USAGE:
# python3 11_plot_volume.py [rffilter] [subdirectory] [conversion] [factor]
# python3 11_plot_volume.py jgf1 RF_auto_check_2 prem 2
# python3 11_plot_volume.py jgf1 RF_auto_check_2 prem 2
# python3 11_plot_volume.py tff3 tff3_auto_check_2 SL2014 2
# python3 11_plot_volume.py tff3 tff3_auto_check_2 prem 2
# python3 11_plot_volume.py tff3 tff3_auto_check_2 SL2014 2

if len(sys.argv)>=2:
    subdirectory = str(sys.argv[2])
else:
    subdirectory = 'RF_auto_check_2'
if len(sys.argv) >1:
    rffilter = str(sys.argv[1])
if len(sys.argv) >3:
    conversion=str(sys.argv[3])
else:
    conversion = 'prem'
if len(sys.argv) >4:    
   factor = float(sys.argv[4])
else:
    factor=2.

outputdirec = homedirec+'CCP_Results'+'_' + conversion +'_'+ rffilter + '_' + str(factor) +'/'
if not os.path.exists(outputdirec):
    os.makedirs(outputdirec)
'''
#Previous default settings:
name = 'fulldataset_check_2'; rffilter = 'jgf1'; conversion = 'prem'; factor = 2.
Lets go for all with spectral type colour scheme for all figures
PseudoX3 [-116,42] [-104,47] (10)
PsuedoW2 [-120,45] [-103,45] (12)
PseudoY3 [-110,39] [-110,49] (10)
PseudoCC [-115,47] [-105,42] (8.5)
DataCoverage410_check2
DataCoverage660_check2 
#may need to change the figures for all of these
Topography_410 380 450, reversed colours
Topography_660 650 700, straight colours
MTZ_width 230 290
lets go for:
Name = old_name + '_' + conversion +'_'+ rffilter + '_' + str(factor)
'''
name = subdirectory

CCP = mega_volume.ccp_volume()
CCP.load_latest(
    name=name,
     filter=rffilter,
     conversion=conversion,
     factor=factor)

print('done loading')

if True: #change to false if you would rather not replot this
    Data_Coverage={}
    Data_Coverage['DataCoverage410_check2']={'depth':410}
    Data_Coverage['DataCoverage660_check2']={'depth':660}
    for Entry in Data_Coverage:
        CCP.plot_datacoverage(Data_Coverage[Entry]['depth'],name=name,filter=rffilter, conversion=conversion, factor=factor)
        plt.savefig(outputdirec+Entry+'_'+ conversion +'_'+ rffilter + '_' + str(int(factor)) +'.png')
        #plt.show()
        plt.clf()

if False:
    CCP.plot_crosssection('EW',45.,amplify=1.,name=name,filter=rffilter, conversion=conversion, factor=factor,zoom=False, mincoverage=20.)
    plt.show()

if False:
    CS = {}
    Cross_Section['JennyX3']= {'lon1':-116.,'lon2':-104.,'lat1':42.,'lat2':47.,'deglim':10}
    Cross_Section['PseudoCC']= {'lon1':-115.,'lon2':-105.,'lat1':47.,'lat2':42.,'deglim':10}
    



#Reproduce the zoomed in cross sections found in the Schmandt et al. and Fee & Deuker papers
if True:
    Cross_Section={}
    Cross_Section['PseudoX3']= {'lon1':-116.,'lon2':-104.,'lat1':42.,'lat2':47.,'deglim':10}
    Cross_Section['PseudoW2']= {'lon1':-120.,'lon2':-103.,'lat1':45.,'lat2':45.,'deglim':12}
    Cross_Section['PseudoY3']= {'lon1':-110.,'lon2':-110.,'lat1':39.,'lat2':49.,'deglim':10}
    Cross_Section['PseudoCC']= {'lon1':-115.,'lon2':-105.,'lat1':47.,'lat2':42.,'deglim':10}
    for Entry in Cross_Section:
        for zoom in [False, True]:
            CCP.plot_crosssection_any(lon1=Cross_Section[Entry]['lon1'],lon2=Cross_Section[Entry]['lon2'],lat1=Cross_Section[Entry]['lat1'],lat2=Cross_Section[Entry]['lat2'],numpoints=40,amplify=0.5,mincoverage=20.,zoom=zoom,color_scheme='rainbow', reverse=False,degree_limit = Cross_Section[Entry]['deglim'])
            plt.savefig(outputdirec+Entry+'_'+ conversion +'_'+ rffilter + '_' + str(int(factor))+'_'+str(zoom)+'.png')
            #plt.show();
            plt.clf()

if True:
    Topography = {}
    Topography['Topography660']={'min':650,'max':700,'reverse':True}
    Topography['Topography410']={'min':380,'max':440,'reverse':False}
    if conversion == 'SL2014': Topography['Topography660']={'min':640,'max':690,'reverse':True} # to deal with pull up from 3d
    for Entry in Topography:
        CCP.plot_topography(Topography[Entry]['min'],Topography[Entry]['max'],name=name,filter=rffilter,conversion=conversion,factor=factor,mincoverage=100., amplitude = False,color_scheme='rainbow', reverse=Topography[Entry]['reverse'])
        plt.savefig(outputdirec + Entry + '_' + conversion +'_'+ rffilter + '_' + str(int(factor)) +'.png')
        #plt.show();
        plt.clf()

if True:
    Entry = 'MTZ_width'
    CCP.plot_mtzwidth(filter=rffilter, conversion=conversion, factor=factor, Max_Thickness = 290, Min_Thickness=230)
    plt.savefig(outputdirec+Entry+'_'+ conversion +'_'+ rffilter + '_' + str(int(factor)) +'.png')
    #plt.show()
    plt.clf()

if False:
    CCP.plot_moveout(d660=True,filter=rffilter, conversion=conversion, factor=factor)
