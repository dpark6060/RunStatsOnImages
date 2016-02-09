#!/usr/bin/env python


import glob
import os
import sys
import numpy as np
import time
import MakeMatlabSh as SPMsh
import subprocess as sp
import nibabel as nb

def MakeSliceTimingJobs(Nii,Fs,itl,OutDir):
    shape=nb.load(Nii).get_shape()
    nSlice=shape[2]
    SliceOrder=[]
    SOtxt="["
    tr=1./Fs
    print itl
    for n in range(int(itl)):
        SliceOrder.extend(range(n,nSlice,int(itl)))
    
    
    for n in SliceOrder[:-1]:         
        SOtxt=SOtxt+'{:1.0f} '.format(n+1)
        
    SOtxt=SOtxt+'{}]'.format(int(SliceOrder[-1]+1))
    
    TA=tr-(float(tr)/nSlice)
    
    jobTemplate='/share/studies/David_FS/Simulated/Code/Matlab/SliceTimingTemplate_job.m'
    File=open(jobTemplate)
    Template=File.read()
    File.close
    
    Template=Template.replace('^NSLICES^',str(nSlice))
    Template=Template.replace('^TR^',str(float(tr)))
    Template=Template.replace('^TA^','{:.14f}'.format(TA))
    Template=Template.replace('^SLICEORDER^',SOtxt)
    
    SaveDir=os.path.join(OutDir,'SliceTiming_job.m')
    File=open(SaveDir,'w')
    File.write(Template)
    File.close()
    
    Template='/share/studies/David_FS/Simulated/Code/Matlab/SliceTimingTemplate.m'
    File=open(Template)
    Template=File.read()
    File.close
    
    Template=Template.replace('^JOBFILE^',SaveDir)
    SaveDir=os.path.join(OutDir,'SliceTiming.m')
    
    File=open(SaveDir,'w')
    File.write(Template)
    File.close()


def usage():
    print'USAGE: ./RunSPMCompleteOnFile.py <InputFile> '

def main(InputNii,Fs,itl):
    tr=1./Fs
    RootDir,FileName=os.path.split(InputNii)
    trash='.exe'
    FileBase=FileName
    while trash:
        FileBase,trash=os.path.splitext(FileBase)
        
    cmd='cp {0} {1}/SPM{2}.nii.gz;gunzip -f {1}/SPM{2}.nii.gz;mv {1}/SPM{2}.nii {1}/{2}.nii;'.format(InputNii,RootDir,FileBase)
    print cmd
    pr=sp.Popen(cmd,shell=True)
    pr.wait()
    
    
    trash='.exe'
    FileBase=FileName
    while trash:
        FileBase,trash=os.path.splitext(FileBase)

       
    OutputFile=os.path.join(RootDir,'{}_SPM.nii.gz'.format(FileBase))
    
    n=1
    
    while os.path.exists(OutputFile):
        OutputFile=os.path.join(RootDir,'{}_SPM{}.nii.gz'.format(FileBase,n))
        n=n+1
    
    WrkDir=os.path.join(RootDir,'{}_Work'.format(FileBase))
    SPMFiles=os.path.join(WrkDir,'WorkFiles','SPM')
    ClusterJobDir=os.path.join(WrkDir,'ShFiles','SPM')
    ErrorOutput=os.path.join(WrkDir,'ClusterError','SPM')
    ClusterOutput=os.path.join(WrkDir,'ClusterOutput','SPM')
    
    BaseDir,fname=os.path.split(InputNii)
    
    while not fname.find('.')==-1:
        fname,trash=os.path.splitext(fname)
        
    targetNii=os.path.join(BaseDir,'{}.nii'.format(fname))
    
    if not os.path.exists(WrkDir):
        os.makedirs(WrkDir)

    if not os.path.exists(ClusterJobDir):
        os.makedirs(ClusterJobDir)
    
    if not os.path.exists(SPMFiles):
        os.makedirs(SPMFiles)
        
    if not os.path.exists(ErrorOutput):
        os.makedirs(ErrorOutput)
    
    if not os.path.exists(ClusterOutput):
        os.makedirs(ClusterOutput)
        
        
    JobName='{}_SPM'.format(FileBase)
    
    
    MakeSliceTimingJobs(os.path.join(RootDir,'{}.nii'.format(FileBase)),Fs,itl,SPMFiles)
    #(Nii,Fs,itl,OutDir)
    SPMsh.main(targetNii,ClusterJobDir,ErrorOutput,ClusterOutput,SPMFiles)
    

    
    SubmitCmd='for Dir in `/bin/ls '+ClusterJobDir+'/*.sh`; do echo "Running SPM Slice Timing on ${Dir}.";qsub -cwd $Dir;sleep 2; done'
    print SubmitCmd
    pr=sp.Popen(SubmitCmd,shell=True)
    pr.wait()
    
    
    
    CheckPath=os.path.join(RootDir,'{}_SPM.nii'.format(FileBase))
    print CheckPath
    Min=0
    
    while (not os.path.exists(CheckPath)) and Min<60*10:
        time.sleep(60)
        Min=Min+1
        print 'Waiting'
    time.sleep(20)
    
    if Min==60 and not os.path.exists(CheckPath):
        print ('File {} TImeout'.format(FileBase))    
    
    CheckPath=os.path.join(RootDir,'a{}.mat'.format(FileBase))
    if os.path.exists(CheckPath):
        cmd='mv {} {}/a{}.mat'.format(CheckPath,SPMFiles,FileBase)
        #print cmd
        pr=sp.Popen(cmd,shell=True)
        pr.wait()
    
    CheckPath=os.path.join(RootDir,'{}_SPM.nii'.format(FileBase))
    print CheckPath
    if os.path.exists(CheckPath):
        cmd='gzip -f {}'.format(CheckPath)
        #print cmd
        pr=sp.Popen(cmd,shell=True)
        pr.wait()
        
        cmd='rm {}/{}.nii'.format(RootDir,FileBase)
        pr=sp.Popen(cmd,shell=True)
        pr.wait()
        time.sleep(60)
        
 
if __name__ == '__main__':
    
    if not len(sys.argv)==2:
        usage()
    else:
        main(sys.argv[1])


