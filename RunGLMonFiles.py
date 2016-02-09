#!/usr/bin/env python
import nibabel as nb
import numpy as np
import sys
import os
import glob
import matplotlib.pyplot as pl
import scipy.stats as sts
import subprocess as sp
sys.path.append('/share/users/dparker/Code/Python/GenericCode/RunStatsOnImg')

import RunLinRegCompleteOnFile as Runglm
import RunLinRegCompleteOnFile_UCSR as RunglmSR

   
   
def main(InputNii,meth,Regressor,con,tr,itl):
        base,subID=os.path.split(InputNii)
    
        #print Regressor
        
        CheckOutput=os.path.join(base,'tPython',meth,con,'Beta.nii.gz')
        #print CheckOutput
        
        if not os.path.exists(CheckOutput):
            
            if meth=='Filt':
                Regressor,trash=os.path.split(Regressor)
                Regressor=os.path.join(Regressor,'Regressors_20Hz.txt')
                RunglmSR.main(InputNii,con,Regressor,meth,tr,itl,20)
                
            else:
                Runglm.main(InputNii,con,Regressor,meth)
        else:
        
            print 'Ran GLM for {} {}, skipping'.format(InputNii,meth)    