#!/usr/bin/env python

import os

def main(InputSlice,Reg,Ref,shPath,ClusterError,ClusterOutput):

    
    if os.path.isfile(shPath):
        os.remove(shPath)

    shFile=open(shPath,'w')

    ###################################################
    ###### Create .sh file to submit to cluster #######
    ###################################################
    
    shFile.write('#!/bin/bash\n')
    shFile.write('############################\n')
    shFile.write('# Job Options & Parameters #\n')
    shFile.write('############################\n')
    shFile.write('# (2) Resource Requirements:\n')
    shFile.write('#$ -l mem_free=3G\n')
    shFile.write('#$ -l h_vmem=4G\n')
    shFile.write('# (3) Environment Setup:\n')
    shFile.write('#$ -cwd\n')
    shFile.write('#$ -j y\n')
    shFile.write('#$ -S /bin/bash\n')
    shFile.write('# (4) Job:\n')
    shFile.write('#$ -o {}\n'.format(ClusterOutput))
    shFile.write('#$ -e {}\n'.format(ClusterError))
    shFile.write('source ~/.bashrc\n')
    shFile.write('source /usr/local/UniversalPathSetup.sh\n')
    shFile.write(' \n')
    shFile.write('unset SGE_ROOT\n')
    shFile.write("python /share/users/dparker/Code/Python/GenericCode/RunStatsOnImg/SliceGLM.py"+' {} {} {}'.format(Reg,InputSlice,Ref))
    shFile.close()
    return()
