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



con='SuperiorFrontalL'
Methods=['FS','FSL','SPM']
#methPath=['FilterShift_Corrected.nii','FSL_Corrected.nii.gz','SPM_Corrected.nii']

Subs=['1','2','3','4','5']
tr=2
itl=6

Motions=['LowMotion','MediumMotion','HighMotion']




for sub in Subs:
    subject='/share/studies/David_FS/Simulated/DavidSub_{}'.format(sub)
    trash,subID=os.path.split(subject)

    for motion in Motions:
          
        for meth,path in zip(Methods,methPath):
            
            print subID
            WrkFile=os.path.join(subject,motion,'{}_Uncorrected.nii'.format(subID))
            
            if os.path.exists(WrkFile):
                
                trash='.exe'
                FileBase=WrkFile
                while trash:
                    FileBase,trash=os.path.splitext(FileBase)
                subID=FileBase
            
                target=os.path.join(subject,'{}_FS.nii.gz'.format(subID))
                print target
                if not os.path.exists(target):
                    Runfs.main(WrkFile,1./tr,itl)
                else:
                    print 'found FS for {}'.format(subID)
                    
                target=os.path.join(subject,'{}_SPM.nii.gz'.format(subID))
                if not os.path.exists(target):
                    Runspm.main(WrkFile,1./tr,itl)
                else:
                    print 'found SPM for {}'.format(subID)
                    
                target=os.path.join(subject,'{}_FSL.nii.gz'.format(subID))
                if not os.path.exists(target):
                    Runfsl.main(WrkFile,1./tr,itl)
                else:
                    print 'found FSL for {}'.format(subID)    
        
                InputNii=os.path.join(subject,'{}_{}.nii.gz'.format(subID,meth))
                InputNii=WrkFile
                Regressor=os.path.join(subject,'SuperiorFrontalL.txt')
        
                CheckOutput=os.path.join(subject,'tPython',meth,con,'Beta.nii.gz')
                if not os.path.exists(CheckOutput):
                    Runglm.main(InputNii,con,Regressor,meth)
                else:
            
                    print 'Ran for {} {}, skipping'.format(subject,meth)
                    
            else:
                print ('No Nii File For {}'.format(subID))
    else:
        print ('skipping {}'.format(subID))


#                 
# if __name__ == '__main__':
#     Subjects=glob.glob(sys.argv[1])
#     print sys.argv[1]
#     print len(Subjects)
#     for sub in Subjects:
#         RunStatsOnVols(sub)
            
            
            
            
            
            
            
            
            