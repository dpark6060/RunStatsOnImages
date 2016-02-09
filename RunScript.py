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

# Testing the Update
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




Subjects=glob.glob('/data/lxqSub_66_Sim*')
Motions=['HighMotion','MediumMotion','LowMotion']
TRs=['0.5','1.0','1.5','2.0','2.5','3.0']
Itls=[1,6]
OutputBase='/home/dparker/TRAnalysis/{TR}/{Motion}/{SubID}'
InputFileBase='SimulatedBoldSmooth_66_Noise{Noise}_{Motion}{MotNum}_Interleaved{Itl}_TR{TR}.nii.gz'
noise=5
for sub in Subjects:
    trash,subID=os.path.split(sub)

    for motion in Motions:
        SubMotions=glob.glob(os.path.join(sub,'Motion_{}*'.format(motion)))

        if not SubMotions:
            print 'No {} for {}'.format(motion,subID)
        else:
            submotion=SubMotions[-1]
            m=re.search('(Motion_.*Motion)(\d)',submotion)
            motnum=m.groups()[-1]
            for itl in Itls:
                for tr in TRs:
                    InputNii=os.path.join(submotion,InputFileBase.format(Noise=noise,Motion=motion,MotNum=motnum,Itl=itl,TR=tr))
                    if not os.path.exists(InputNii):
                        print 'No File {}'.format(InputNii)
                    else:
                        print InputNii
                        BoldTimeseries=os.path.join(sub,'OriginalRegionalBoldTimeSeries.txt')
                        WrkFile,Regressors=RunCoreOnFile(InputNii,OutputBase.format(TR=tr,Motion=motion,SubID=subID),1.0/float(tr), BoldTimeseries)
                        WrkDir,trash=os.path.split(WrkFile)
                        Pipe.main(WrkFile,'1006',itl,float(tr),Regressors)

