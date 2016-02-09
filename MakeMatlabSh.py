#!/usr/bin/env python

import os
import numpy as np

def main(File,ShDir,ErOut,ClustOut,path):
    
    
    trash,subID=os.path.split(File)
    while trash:
        subID,trash=os.path.splitext(subID)
    shPath=os.path.join(ShDir,'{}.sh'.format(subID))
    if os.path.isfile(shPath):
        os.remove(shPath)
    
    base,trash=os.path.split(File)
    shFile=open(shPath,'w')

    ###################################################
    ###### Create .sh file to submit to cluster #######
    ###################################################
    
    shFile.write('#!/bin/bash\n')
    shFile.write('############################\n')
    shFile.write('# Job Options & Parameters #\n')
    shFile.write('############################\n')
    shFile.write('# (2) Resource Requirements:\n')
    shFile.write('#$ -l mem_free=5G\n')
    shFile.write('#$ -l h_vmem=6G\n')
    shFile.write('#PBS -N Matlab\n')
    shFile.write('#PBS -m be\n')
    shFile.write('#PBS -j oe\n')           
    shFile.write('# (3) Environment Setup:\n')
    shFile.write('#$ -cwd\n')
    shFile.write('#$ -j y\n')
    shFile.write('#$ -S /bin/bash\n')
    shFile.write('#$ -o {}\n'.format(ClustOut))
    shFile.write('#$ -e {}\n'.format(ErOut))
    shFile.write('# (4) Job:\n')
    shFile.write('cd {}\n'.format(base))
    shFile.write('/usr/local/MATLAB/R2013b/bin/matlab -nodisplay << EOF\n')
    shFile.write('addpath /usr/local/SPM/v8/spm8\n')
    shFile.write('addpath {}\n'.format(path))
    shFile.write('addpath /share/users/dparker/Code/Matlab/OpenNii\n')
    shFile.write("spm_get_defaults('cmdline',1);\n")
    shFile.write("spm_jobman('initcfg');\n")
    shFile.write("SliceTiming('{}','{}')\n".format(File,subID))
    shFile.write("pause(10)\n")
    shFile.write('exit\n')
    shFile.write('EOF\n')
    shFile.write('echo "Sleeping"\n')
    shFile.write('sleep 10\n')
    shFile.write('mv {}/a{}.nii {}/{}_SPM.nii'.format(base,subID,base,subID))
    shFile.close()
    return()

