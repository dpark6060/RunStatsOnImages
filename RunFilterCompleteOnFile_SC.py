#!/usr/bin/env python

import ClusterCreateFilterJobsFromTxt as CreateTxtSh
import CompileFilterResultsInFolder as Compile
import glob
import os
import sys
import numpy as np
import time
import subprocess as sp
import nibabel as nb
import SCcallSH as SH
from multiprocessing import Pool
import subprocess as sp

def usage():
    print'USAGE: ./RunFsCompleteOnFile.py <InputFile> <Fs> <Int> '
    print '\t where <Fs> is the sampling frequency (Hz)'
    print '\t and <Int> Is the interleave Parameter'


def main(InputNii,Fs,Int,Save='',WrkDir=''):
    
    RootDir,FileName=os.path.split(InputNii)

    trash='.exe'
    FileBase=FileName
    while trash:
        FileBase,trash=os.path.splitext(FileBase)

       
    OutputFile=os.path.join(RootDir,'{}_Filt.nii.gz'.format(FileBase))
    
    n=1
    
    while os.path.exists(OutputFile):
        OutputFile=os.path.join(RootDir,'{}_Filt{}.nii.gz'.format(FileBase,n))
        n=n+1
    
    if not WrkDir:
        WrkDir=os.path.join(RootDir,'{}_Work'.format(FileBase))
        
    TxtOutput=os.path.join(WrkDir,'WorkFiles','Filt')
    ClusterJobDir=os.path.join(WrkDir,'ShFiles','Filt')
    ErrorOutput=os.path.join(WrkDir,'ClusterError','Filt')
    ClusterOutput=os.path.join(WrkDir,'ClusterOutput','Filt')
    
    
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
    ProcessedFiles=len(glob.glob(os.path.join(TxtOutput,'Filt_Image*.txt')))
    if not ProcessedFiles==NtxtFiles:
        SubmitFiles=glob.glob(ClusterJobDir+'/*.sh')
        p=Pool(20)
        p.map(SH.main,SubmitFiles)
        p.close()
        p.join()
    else:
        print 'Completed for {}'.format(FileBase)
    
    ProcessedFiles=len(glob.glob(os.path.join(TxtOutput,'Filt_{}*.txt'.format('Image'))))
    
    while ProcessedFiles<NtxtFiles:
        print('{}: Waiting for Files to Finish'.format(time.ctime()))
        ProcessedFiles=len(glob.glob(os.path.join(TxtOutput,'Filt_{}*.txt'.format('Image'))))
        time.sleep(60)
    
    if Save=='':
        Save=OutputFile
        
    Compile.CompileNii(InputNii,Save)
    
    cmd='mv -f {}/{}_FilterShift_Corrected.nii {}/{}_Filt.nii'.format(RootDir,FileBase,RootDir,FileBase)
    pr=sp.Popen(cmd,shell=True)
    pr.wait()
    cmd='gzip -f {}/{}_Filt.nii'.format(RootDir,FileBase)
    pr=sp.Popen(cmd,shell=True)
    pr.wait()
    
    
    
    
    

if __name__ == '__main__':
    
    if not len(sys.argv)==4:
        usage()
    else:
        main(sys.argv[1],float(sys.argv[2]),float(sys.argv[3]))


