#!/usr/bin/env python
import sys
sys.path.append('/share/dparker/dparker/Code/Python/GenericCode/RunStatsOnImg')
import RunFSLCompleteOnFile_SC as Runfsl
import RunSPMCompleteOnFile_SC as Runspm
import RunFsCompleteOnFile_SC as Runfs
import RunFilterCompleteOnFile_SC as RunFilt
import glob
import numpy as np
import os
import sys
import subprocess as sp
import nibabel as nb
import time




#itl=6
#tr=2



def main(WrkFile,tr,itl):


    Files=[]
    MethOrder=[]
    base,subID=os.path.split(WrkFile)
    print subID
    ext='.exe'
    while ext:
        subID,ext=os.path.splitext(subID)

    
    print 'subID: {}'.format(subID)
    
    
    ########################### FS #############################
    
    target=os.path.join(base,'{}_FS.nii.gz'.format(subID))
    print target
    if not os.path.exists(target):
        Runfs.main(WrkFile,1./tr,itl)
        Files.append(target)
        MethOrder.append('FS')
    else:
        print 'found FS for {}'.format(subID)
        Files.append(target)
        MethOrder.append('FS')
        
        
     ########################### SPM #############################
       
    target=os.path.join(base,'{}_SPM.nii.gz'.format(subID))
    if not os.path.exists(target):
        Runspm.main(WrkFile,1./tr,itl)
        Files.append(target)
        MethOrder.append('SPM')
    else:
        print 'found SPM for {}'.format(subID)
        Files.append(target)
        MethOrder.append('SPM')
        
        
    ########################### FSL #############################
        
    target=os.path.join(base,'{}_FSL.nii.gz'.format(subID))
    if not os.path.exists(target):
        Runfsl.main(WrkFile,1./tr,itl)
        Files.append(target)
        MethOrder.append('FSL')
    else:
        print 'found FSL for {}'.format(subID)
        Files.append(target)
        MethOrder.append('FSL')
        
        
    ########################### Filt #############################
        
    target=os.path.join(base,'{}_Filt.nii.gz'.format(subID))
    if not os.path.exists(target):
        RunFilt.main(WrkFile,1./tr,itl)
        Files.append(target)
        MethOrder.append('Filt')
    else:
        print 'found Filt for {}'.format(subID)
        Files.append(target)
        MethOrder.append('Filt')
        
        
    ########################### Uncorrected #############################
    
    target=os.path.join(base,'{}_Uncorrected.nii.gz'.format(subID))
    if not os.path.exists(target):
        cmd='cp {} {}/{}_Uncorrected.nii.gz'.format(WrkFile,base,subID)
        pr=sp.Popen(cmd,shell=True)
        pr.wait()
        
        Files.append(target)
        MethOrder.append('Uncorrected')
    else:
        print 'found UC for {}'.format(subID)
        Files.append(target)
        MethOrder.append('Uncorrected')    
        
    
    return Files,MethOrder
        


#                 
# if __name__ == '__main__':
#     Subjects=glob.glob(sys.argv[1])
#     print sys.argv[1]
#     print len(Subjects)
#     for sub in Subjects:
#         RunStatsOnVols(sub)
            
            
            
            
            
            
            
            
            
