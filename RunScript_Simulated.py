import nibabel as nb
import numpy as np
import sys
import os
import glob
import matplotlib.pyplot as pl
import scipy.stats as sts
import subprocess as sp
import ExtractBold as EXB
import RunFullPipelineOnFile as Pipe
import re


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
        EXB.main(Timeseries,1006,fs,Regressors)

    Reg100=os.path.join(Output,'Regressors_100Hz.txt')
    if not os.path.exists(Reg100):
        EXB.main(Timeseries,1006,100,Reg100)

    return(WrkFile,Regressors)




Subjects=glob.glob('/share/studies/Simulated/Subjects/P0*')
Motions=['Low']
TRs=['2.5','3.5','4.5']
Itls=[0,1,2]

OutputBase='/share/studies/Simulated/Subjects/{SubID}/Motion_{Motion}/Int_{Itl}/TR_{TR}/Processed'
InputFileBase='SimulatedBoldSmooth_66_Noise{Noise}_{Motion}Motion{MotNum}_Interleaved{Itl}_TR{TR}.nii.gz'
noise=5
for sub in Subjects:
    trash,subID=os.path.split(sub)
    
    for tr in TRs:
        
        for motion in Motions:
            SubDir=os.path.join(sub,'Motion_{}'.format(motion))
    
            if not os.path.exists(SubDir):
                print 'No {} for {}'.format(motion,subID)
            else:                
                for itl in Itls:
                    
                    SubDir=os.path.join(SubDir,'Int_{}'.format(itl),'TR_{}'.format(tr))
                    
                    SubNii=glob.glob(os.path.join(SubDir,'*.nii.gz'))
                    submotion=SubNii[-1]
                    m=re.search('({}Motion)(\d)'.format(motion),submotion)
                    motnum=m.groups()[-1]
                    
                    InputNii=os.path.join(SubDir,InputFileBase.format(Noise=noise,Motion=motion,MotNum=motnum,Itl=itl,TR=tr))
                    
                    if not os.path.exists(InputNii):
                        print 'No File {}'.format(InputNii)
                    else:
                        print InputNii
                        BoldTimeseries=os.path.join(sub,'OriginalRegionalBoldTimeSeries.txt')
                        WrkFile,Regressors=RunCoreOnFile(InputNii,OutputBase.format(TR=tr,Motion=motion,SubID=subID,Itl=itl),1.0/float(tr), BoldTimeseries)
                        WrkDir,trash=os.path.split(WrkFile)
                        Pipe.main(WrkFile,'1006',itl,float(tr),Regressors)

