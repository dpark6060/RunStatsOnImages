#!/usr/bin/env python
import nibabel as nb
import numpy as np
import sys
import os
import glob
import matplotlib.pyplot as pl
import scipy.stats as sts
import subprocess as sp


import RunSTConFile_SC as STC
import RunMConFile as RMC
import RunGLMonFiles_SC as GLM


def main(InputFile,ContrastName,Interleave,TR,Regressor):
    print 'RunFillPipelineOnFile_SC.py'

    STCFiles,Methods=STC.main(InputFile,TR,Interleave)
    RMC.main(InputFile)
    for stcfile,meth in zip(STCFiles,Methods):

        GLM.main(stcfile,meth,Regressor,ContrastName)