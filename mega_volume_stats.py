#mega_volume_stack.py
'''
A nice script that should allow you to compare the 440 to 660 correlations when using the 1-d and 3-d velocity models - has to be run off each volume that you want to compare, it will place it in a new directory 'CCP_Stack/MTZ_files/'+name+'_'+conversion+'_'+model+'_'+str(int(factor)).txt '''

root = '/raid3/sdat2/Parra/'
conversion = 'prem'; filter='jgf1';factor=2.;
file1= root+'CCP_Stack/MTZ_'+conversion+'_'+filter+'_'+str(int(factor))+'.txt'
conversion = 'SL2014';
file2 =root+'CCP_Stack/MTZ_'+conversion+'_'+filter+'_'+str(int(factor))+'.txt'
import sys
import numpy as np
import scipy
from scipy import interpolate
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import os
import os.path
import math
import msgpack
import shutil
from matplotlib.colors import LogNorm
import matplotlib.cm as cm
from scipy import stats
import pandas
from pandas.tools import plotting
import pickle
import seaborn as sns
import mpl_toolkits
from statsmodels.formula.api import ols

files =[file2,file1]

for i in [0,1]:#range(len(files)):
    file=files[i]
    data=np.loadtxt(file)
    #print(data)
    ## pandas!
    mtz=pandas.DataFrame({'d410':data[:,0],'d660':data[:,1]})
    #print(mtz.mean())
    #plotting.scatter_matrix(mtz,alpha=0.4,figsize=(6,6),diagonal='kde')
    #sns.pairplot(mtz, vars=['d410','d660'],kind='reg')
    #g = sns.JointGrid('d410','d660',data=mtz)
    #g.plot(sns.regplot, sns.distplot, stats.pearsonr);
    if i==0:
        g = sns.JointGrid(x=mtz.d410,y=mtz.d660,xlim=[370,440],ylim=[640,700], space=0,  ratio=2)
    if i==1:
        g.x=mtz.d410
        g.y=mtz.d660
    if i==0:
        g.plot_joint(sns.kdeplot, shade=True, cmap="PuBu", n_levels=10,alpha=1);
    if i==1:
        g.plot_joint(sns.kdeplot, shade=True, cmap="Greens", n_levels=10,alpha=0.5);
    #_ = g.ax_marg_x.hist(mtz["d410"], color="b", alpha=.6,bins=np.arange(370, 450, 10))
    #_ = g.ax_marg_y.hist(mtz["d660"], color="b", alpha=.6,orientation="horizontal",bins=np.arange(630, 710, 10))
    if i==0:
        g.plot_marginals(sns.kdeplot, shade=True,alpha=0.5)
    if i==1:
        g.plot_marginals(sns.kdeplot, shade=True,alpha=0.5)
    if i==0:
        g.annotate(stats.pearsonr, template="3D (Purple) {stat} = {val:.2f} (p = {p:.2g})",fontsize=12,loc='upper left');
    if i==1:
         g.annotate(stats.pearsonr, template="1D (Green) {stat} = {val:.2f} (p = {p:.2g})",fontsize=12, loc ='lower right');
        
    print('mtz mean =',mtz.mean())
    print('mtz mad =', mtz.mad())
    print('mtz mad =',mtz.median())

plt.savefig('dist_aftercorrection.pdf')
plt.show()# common conversion point stacking




