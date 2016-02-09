#!/usr/bin/env python
import nibabel as nb
import numpy as np
import sys
import os
import glob
import matplotlib.pyplot as pl
import scipy.stats as sts
import subprocess as sp


import RunSTConFile as STC
import RunGLMonFiles as GLM
import RunMConFile as RMC


def main(InputFile,ContrastName,Interleave,TR,Regressor,RunMC=''):
    print 'RunFillPipelineOnFile_SC.py'
    
    print 'RunMC:\t{}'.format(RunMC)
    print 'RunMC=="first":\t{}'.format(RunMC=='first')
    print 'RunMC=="last":\t{}'.format(RunMC=='last')
    print 'RunMC=="none":\t{}'.format(RunMC=='none')

    
    
    if RunMC=='first':
        print 'Running MC first'
        InputFile=RMC.main(InputFile)
        
    print InputFile
    
    STCFiles,Methods=STC.main(InputFile,TR,Interleave)
    
    for stcfile,meth in zip(STCFiles,Methods):
        
        if RunMC=='last':            
            MCstcfile=RMC.main(stcfile)
        else:
            MCstcfile=stcfile
            
        print MCstcfile
        GLM.main(MCstcfile,meth,Regressor,ContrastName,TR,Interleave)
        
if __name__ == '__main__':
    main(sys.argv[1],sys.argv[2],int(sys.argv[3]),float(sys.argv[4]),sys.argv[5])