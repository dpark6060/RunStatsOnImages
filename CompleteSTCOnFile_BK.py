#!/usr/bin/env python
import sys
sys.path.append('/share/users/dparker/Code/Python/GenericCode/RunStatsOnImg')
import RunFSLCompleteOnFile as Runfsl
import RunSPMCompleteOnFile as Runspm
import RunFsCompleteOnFile as Runfs
import RunLinRegCompleteOnFile as Runglm
import glob
import numpy as np
import os
import sys
import subprocess as sp
import nibabel as nb
import time


con='Sub18'

Methods=['FS','SPM','FSL','Uncorrected']
#methPath=['FilterShift_Corrected.nii','FSL_Corrected.nii.gz','SPM_Corrected.nii']

tr=2
itl=6





def RunStatsOnVols(subject,Regressor):
    mainDir,subID=os.path.split(subject)

        
    for meth in Methods:
          
        WrkFile=subject
          
        if os.path.exists(WrkFile):
              
            trash='.exe'
            FileBase=subID
            while trash:
                FileBase,trash=os.path.splitext(FileBase)
            subID=FileBase
          
            if meth=='Uncorrected':
                target=subject
            else:
                
                target=os.path.join(mainDir,'{}_{}.nii.gz'.format(subID,meth))
                print target
                if not os.path.exists(target):
                    if meth=='FS':
                        Runfs.main(WrkFile,1./tr,itl)
                    elif meth=='FSL':
                        Runfsl.main(WrkFile,1./tr,itl)
                    elif meth=='SPM':
                        Runspm.main(WrkFile,1./tr,itl)
                    time.sleep(20)
                else:
                    print 'found {} for {}'.format(meth,subID)

            CheckOutput=os.path.join(mainDir,'tPython',meth,con,'Beta.nii.gz')
            print CheckOutput
            if not os.path.exists(CheckOutput):
                Runglm.main(target,con,Regressor,meth)
            else:
          
                print 'Ran for {} {}, skipping'.format(subject,meth)
                  
        else:
            print ('No Nii File For {}'.format(subID))



                
if __name__ == '__main__':
    
    sub=sys.argv[1]
    reg=sys.argv[2]
    RunStatsOnVols(sub,reg)
            
            
            
            
            
            
            
            
            