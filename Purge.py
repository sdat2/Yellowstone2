#example usage: python3 Purge.py RF_auto_check_4 RF_auto_check_4
import os
import os.path
import glob
import sys
import shutil

root = '/raid3/sdat2/Parra/'

if sys.argv[1] == sys.argv[2]:
    pickles = glob.glob(root+'DataRF/*/'+str(sys.argv[1])+'/*.PICKLE')
    print('there are', len(pickles) ,' to remove')
    for pickle in pickles:
        print('about to remove', pickle)
        os.remove(pickle)
    print('removed' , len(pickles), ' pickles')
