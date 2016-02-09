import nibabel as nb
import numpy as np
import sys
import os
import glob
import matplotlib.pyplot as pl
import scipy.stats as sts
import subprocess as sp
import ExtractBold as EXB
import re
import subprocess as sp
import RunGLMonFiles as GLM

def RunCoreOnFile(InputNii,Output,fs,Timeseries=''):
    print Output
    if not os.path.exists(Output):
        os.makedirs(Output)

    WrkFile=os.path.join(Output,'InputNii.nii.gz')
    if not os.path.exists(WrkFile):
        cmd='cp {} {}'.format(InputNii,WrkFile)
        pr=sp.Popen(cmd,shell=True)
        pr.wait()

    Regressors=os.path.join(Output,'Regressors_{}Hz.txt'.format(fs))
    if not os.path.exists(Regressors):
        EXB.main(Timeseries,1028,fs,Regressors,20.0)

    Reg100=os.path.join(Output,'Regressors_20Hz.txt')
    if not os.path.exists(Reg100):
        EXB.main(Timeseries,1028,20,Reg100,20.0)

    return(WrkFile,Regressors)



Methods=['Filt','FS','FSL','SPM','Uncorrected']
Subjects=glob.glob('/share/studies/David_FS/Simulated/Subjects/P0*')
Motions=['Low']
TRs=['2.0']
Itls=[2,6]
Blurs=[0,3.5,5,6.5,8]
OutputBase='/share/studies/David_FS/Simulated/Blur/{SubID}/Motion_{Motion}/Int_{Itl}/TR_{TR}/Blur_{Blur}'
InputFileBase='Motion_{Motion}/Int_{Itl}/TR_{TR}/Processed/MCInputNii_{Meth}.nii.gz'
NoMotInputFileBase='SimulatedBoldSmooth_66_Noise{Noise}_Interleaved{Itl}.nii.gz'
noise=5

for sub in Subjects:
    trash,subID=os.path.split(sub)
    
    for tr in TRs:
        
        for motion in Motions:
            
            for meth in Methods:
                
                for itl in Itls:
                    
                    for blur in Blurs:
                        InputFile=os.path.join(sub,InputFileBase.format(Motion=motion,Itl=itl,TR=tr,Meth=meth))                
                        InputBase,InputID=os.path.split(InputFile)
                        print InputFile
                       
                        if os.path.exists(InputFile):                            
                            
                            OutputDir=OutputBase.format(SubID=subID,Motion=motion,Itl=itl,TR=tr,Blur=blur)
                            
                            if not os.path.exists(OutputDir):
                                os.makedirs(OutputDir)
                            
                            CPdir,trash=os.path.split(OutputDir)
                            
                            if blur==0:
                                cmd='cp {} {}'.format(InputFile,os.path.join(OutputDir,'Smooth_{}'.format(InputID)))
                            else:
                                cmd='fslmaths {} -s {} {}'.format(InputFile,blur,os.path.join(OutputDir,'Smooth_{}'.format(InputID)))
                            
                            print cmd
                            pr=sp.Popen(cmd,shell=True)
                            pr.wait()
                            
                            WrkFile=os.path.join(OutputDir,'Smooth_{}'.format(InputID))
                            
                            RegPaths=[os.path.join(InputBase,'Regressors_0.5Hz.txt'),os.path.join(InputBase,'Regressors_20Hz.txt')]
                            
                            for r in RegPaths:
                                cmd='cp {} {}'.format(r,CPdir)
                                print cmd
                                pr=sp.Popen(cmd,shell=True)
                                pr.wait()

                            reg=os.path.join(CPdir,'Regressors_0.5Hz.txt')
                            WrkDir,trash=os.path.split(WrkFile)
                            #main(InputNii,meth,Regressor,con,tr,itl)
                            GLM.main(WrkFile,meth,reg,'1028',float(tr),itl)
























