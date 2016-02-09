#!/usr/bin/env python
import nibabel as nb
import numpy as np
import sys
import os
import glob
import matplotlib.pyplot as pl
import scipy.stats as sts
import subprocess as sp
import re




def main(WrkFile):
    
    
    base,subject=os.path.split(WrkFile)
    
    fileBase=re.search('(.*)(.nii.*)',subject).group(1)
    ext=re.search('(.*)(.nii.*)',subject).group(2)

    output=os.path.join(base,'{}_MC{}'.format(fileBase,ext))

        
    if not os.path.exists(output):
        cmd='cd {};mcflirt -in {} -out {}_MC'.format(base,fileBase,fileBase)
        print cmd
        mcSH=os.path.join(base,'MCsh.sh')
        fl=open(mcSH,'w')
        fl.write(cmd)
        fl.close()
        cmd='qsub -q big.q {}'.format(mcSH)   
        print cmd
        
        pr = sp.Popen(cmd,shell=True)
        pr.wait()
        
        cmd='rm {}'.format(mcSH)   
        print cmd        
        pr = sp.Popen(cmd,shell=True)
        pr.wait()
                
    
    return output



