#!/usr/bin/env python


import glob
import os
import sys
import numpy as np
import time
import MakeFslSliceTimingSh as FSLsh
import nibabel as nb
import SCcallSH as SH
from multiprocessing import Pool
import subprocess as sp

def MaketFile(Nii,itl,tr):
    nSlices=nb.load(Nii).get_shape()[2]
    sliceOrder=[]
    
    for n in range(itl):
        sliceOrder.extend(range(n,nSlices,int(itl)))
        
    PerSlice=float(tr)/nSlices
    refSlice=0
    
    TimeList=range(len(sliceOrder))
    trash,TimeList=zip(*sorted(zip(sliceOrder,TimeList)))
    
    TimeList=np.array(TimeList)
    TimeList=(TimeList-TimeList[refSlice])*PerSlice/tr
    
    for n in range(len(TimeList)):
        if n!=refSlice:
            TimeList[n]=TimeList[refSlice]-(TimeList[n]-TimeList[refSlice])
            
    return TimeList
    
    
    
def usage():
    print'USAGE: ./RunFSLCompleteOnFile.py <InputFile> '

def main(InputNii,Fs,itl):
    tr=1./Fs
    RootDir,FileName=os.path.split(InputNii)
    trash='.exe'
    FileBase=FileName
    while trash:
        FileBase,trash=os.path.splitext(FileBase)

       
    OutputFile=os.path.join(RootDir,'{}_FSL.nii.gz'.format(FileBase))
    
    n=1
    
    while os.path.exists(OutputFile):
        OutputFile=os.path.join(RootDir,'{}_FSL{}.nii.gz'.format(FileBase,n))
        n=n+1
    
    WrkDir=os.path.join(RootDir,'{}_Work'.format(FileBase))
    FSLFiles=os.path.join(WrkDir,'WorkFiles','FSL')
    ClusterJobDir=os.path.join(WrkDir,'ShFiles','FSL')
    ErrorOutput=os.path.join(WrkDir,'ClusterError','FSL')
    ClusterOutput=os.path.join(WrkDir,'ClusterOutput','FSL')
    
    BaseDir,fname=os.path.split(InputNii)
    
    while not fname.find('.')==-1:
        fname,trash=os.path.splitext(fname)
        
    
    if not os.path.exists(WrkDir):
        os.makedirs(WrkDir)

    if not os.path.exists(ClusterJobDir):
        os.makedirs(ClusterJobDir)
    
    if not os.path.exists(FSLFiles):
        os.makedirs(FSLFiles)
        
    if not os.path.exists(ErrorOutput):
        os.makedirs(ErrorOutput)
    
    if not os.path.exists(ClusterOutput):
        os.makedirs(ClusterOutput)
        
    
    JobName=os.path.join(ClusterJobDir,'{}_FSL.sh'.format(FileBase))
    
    
    SliceTiming=MaketFile(InputNii,itl,tr)
    STfile=os.path.join(FSLFiles,'SliceTiming.txt')
    np.savetxt(STfile,SliceTiming)
    
    
    FSLsh.main(InputNii,OutputFile,JobName,ErrorOutput,ClusterOutput,STfile)
    

    SubmitFiles=glob.glob(ClusterJobDir+'/*.sh')
    for fl in SubmitFiles:
        base,sh=os.path.split(fl)
        cmd='cd {};./{}'.format(base,sh)
        pr=sp.Popen(cmd,shell=True)
        pr.wait()
    
    #print SubmitCmd
    #os.system(SubmitCmd)
    
    Min=0
    
    while (not os.path.exists(OutputFile)) and Min<60*10:
        time.sleep(60)
        Min=Min+1
        
    if (not os.path.exists(OutputFile)) and Min==60:
        print ('Timeout Error For {}'.format(OutputFile))
        
    time.sleep(30)
    

    
    

if __name__ == '__main__':
    
    if not len(sys.argv)==2:
        usage()
    else:
        main(sys.argv[1])


