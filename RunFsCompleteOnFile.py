#!/usr/bin/env python

import ClusterCreateJobsFromTxt as CreateTxtSh
import CompileResultsInFolder as Compile
import glob
import os
import sys
import numpy as np
import time
import subprocess as sp
import nibabel as nb
import multiprocessing


def usage():
    print'USAGE: ./RunFsCompleteOnFile.py <InputFile> <Fs> <Int> '
    print '\t where <Fs> is the sampling frequency (Hz)'
    print '\t and <Int> Is the interleave Parameter'


def main(InputNii,Fs,Int,WrkDir=''):
    time1=time.time()
    RootDir,FileName=os.path.split(InputNii)

    trash='.exe'
    FileBase=FileName
    while trash:
        FileBase,trash=os.path.splitext(FileBase)

       
    OutputFile=os.path.join(RootDir,'{}_FS.nii.gz'.format(FileBase))
    
    n=1
    
    while os.path.exists(OutputFile):
        OutputFile=os.path.join(RootDir,'{}_FS{}.nii.gz'.format(FileBase,n))
        n=n+1
    
    if not WrkDir:
        WrkDir=os.path.join(RootDir,'{}_Work'.format(FileBase))
        
    TxtOutput=os.path.join(WrkDir,'WorkFiles','FS')
    ClusterJobDir=os.path.join(WrkDir,'ShFiles','FS')
    ErrorOutput=os.path.join(WrkDir,'ClusterError','FS')
    ClusterOutput=os.path.join(WrkDir,'ClusterOutput','FS')
    
    
    if not os.path.exists(WrkDir):
        os.makedirs(WrkDir)
    
    if not os.path.exists(TxtOutput):
        os.makedirs(TxtOutput)
    
    if not os.path.exists(ClusterJobDir):
        os.makedirs(ClusterJobDir)
        
    if not os.path.exists(ErrorOutput):
        os.makedirs(ErrorOutput)
    
    if not os.path.exists(ClusterOutput):
        os.makedirs(ClusterOutput)
        
    x,y,z,t=nb.load(InputNii).get_shape()
    Fnew=np.ceil(z*Fs)
    print Fnew
    
    CreateTxtSh.RunOnFile(InputNii,WrkDir,TxtOutput,Fs,Int,Fnew)
    
    NtxtFiles=len(glob.glob(os.path.join(TxtOutput,'Image*.txt')))
    ProcessedFiles=len(glob.glob(os.path.join(TxtOutput,'FS_Image*.txt')))
    if not ProcessedFiles==NtxtFiles:
        SubmitCmd='for Dir in `/bin/ls '+ClusterJobDir+'/*.sh`; do echo "Running FiltShift on ${Dir}.";qsub -cwd -q big.q $Dir;sleep 2; done'
        print SubmitCmd
        os.system(SubmitCmd)
    else:
        print 'Completed for {}'.format(FileBase)
    
    ProcessedFiles=len(glob.glob(os.path.join(TxtOutput,'FS_{}*.txt'.format('Image'))))
    
    while ProcessedFiles<NtxtFiles:
        print('{}: Waiting for Files to Finish'.format(time.ctime()))
        ProcessedFiles=len(glob.glob(os.path.join(TxtOutput,'FS_{}*.txt'.format('Image'))))
        time.sleep(60)
        
    Compile.CompileNii(InputNii)
    
    cmd='mv -f {}/{}_FilterShift_Corrected.nii {}/{}_FS.nii'.format(RootDir,FileBase,RootDir,FileBase)
    pr=sp.Popen(cmd,shell=True)
    pr.wait()
    cmd='gzip -f {}/{}_FS.nii'.format(RootDir,FileBase)
    pr=sp.Popen(cmd,shell=True)
    pr.wait()
    time2=time.time()
    dur=time2-time1
    cmd='cd {};echo {} >> time.txt'.format(RootDir,dur)
    os.system(cmd)
    
    
    
    
    

if __name__ == '__main__':
    
    if not len(sys.argv)>=3:
        usage()
    else:
        main(sys.argv[1],float(sys.argv[2]),float(sys.argv[3]))


