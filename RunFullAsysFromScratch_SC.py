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
import ExtractBold as EXB
#import MotionAnalysis_David as ma

# 
# ethods='/share/studies/David_FS/Simulated/TextFiles/3Methods.txt'
# Noises='/share/studies/David_FS/Simulated/TextFiles/Noise20.txt'
# Names='/share/studies/David_FS/Simulated/TextFiles/RegNames.txt'
# Colors='/share/studies/David_FS/Simulated/TextFiles/Colors.txt'
# Regions='/share/studies/David_FS/Simulated/TextFiles/RegNumbers.txt'
# Motions='/share/studies/David_FS/Simulated/TextFiles/Motion.txt'
# 
# Methods=open(Methods,'r').read().split('\n')[:-1]
# Noises=[int(n) for n in open(Noises,'r').read().split('\n')[:-1]]
# Regions=open(Regions,'r').read().split('\n')[:-1]
# Names=open(Names,'r').read().split('\n')[:-1]
# colors=open(Colors,'r').read().split('\n')[:-1]
# Motions=open(Motions,'r').read().split('\n')[:-1]
# us='_'
# cor='_Corrected'



ln='================================================='








con='Visual'
#methPath=['FilterShift_Corrected.nii','FSL_Corrected.nii.gz','SPM_Corrected.nii']

tr=2
itl=6

Motions=['LowMotion','MediumMotion','HighMotion']

MCs=['ST','STMC','MCST']

MoveBase='/share/studies/ECFf/Subjects/{sub}/S0001/HRF/HRF_{sub}_S0001.nii'

subbase='/share/studies/David_FS/Real/Subjects'

SubMotion={'LowMotion':['P00001614','P00001628','P00001639','P00001637','P00001632'],'MediumMotion':['P00001624','P00001633','P00001638','P00001644','P00001636'],'HighMotion':['P00001645','P00001621','P00001655','P00001620','P00001668']}
low=['P00001614','P00001628','P00001639','P00001637','P00001632','P00001626','P00001654','P00001647','P00001659','P00001658']
med=['P00001624','P00001633','P00001638','P00001644','P00001636','P00001620','P00001623','P00001643','P00001646','P00001651']
high=['P00001645','P00001621','P00001655','P00001620','P00001668','P00001667','P00001648','P00001619','P00001627','P00001652']

skip=1
for motion in Motions:
 #   subject='/share/studies/David_FS/Simulated/DavidSub_[1-5]'.format(sub)
    Subs=SubMotion[motion]
    print Subs
    for subID in Subs:
        subject=os.path.join(subbase,subID)
        
        for MC in MCs:
            
                
            moveFile=MoveBase.format(sub=subID)
            toFile='/share/studies/David_FS/Real/MotionCorrection/{}/{}/{}/HRF.nii'.format(motion,subID,MC)
            target='/share/studies/David_FS/Real/MotionCorrection/{}/{}/{}/HRF.nii.gz'.format(motion,subID,MC)
            if not os.path.exists(target):

                cmd='cp {} {};gzip {}'.format(moveFile,toFile,toFile)
                pr=sp.Popen(cmd,shell=True)
                pr.wait()
                
                if MC=='ST':
    
                    
                    Files,MethOrder=STC.main(target)
                    print 'STC Files:\n{}'.format(Files)
                    
                    
                    print 'Method:\t{MC}\n{ln}'.format(MC=MC,ln=ln)
    
                    for InputNii,meth in zip(Files,MethOrder):
                        
                        if meth=='Filt':
                            Regressor='/share/studies/David_FS/Real/MotionCorrection/{}/{}/{}/20_Visual.txt'.format(motion,subID,MC)
                        else:
                            Regressor='/share/studies/David_FS/Real/MotionCorrection/{}/{}/{}/Visual.txt'.format(motion,subID,MC)
                        
                        GLM.main(InputNii,meth,Regressor,con)
                        print 'Reg:\t{Regressor}\nFile:\t{InputNii}\nMeth:\t{meth}'.format(Regressor=Regressor,InputNii=InputNii,meth=meth)
                        
                        
                        
                elif MC=='STMC':
                    
                    
                    print 'Method:\t{MC}\n{ln}'.format(MC=MC,ln=ln)
                    
    
                    
                    Files,MethOrder=STC.main(target)
                    print 'STC Files:\n{}'.format(Files)
    
                    for InputNii,meth in zip(Files,MethOrder):
                        
                        if meth=='Filt':
                            Regressor='/share/studies/David_FS/Real/MotionCorrection/{}/{}/{}/20_Visual.txt'.format(motion,subID,MC)
                        else:
                            Regressor='/share/studies/David_FS/Real/MotionCorrection/{}/{}/{}/Visual.txt'.format(motion,subID,MC)
                        
                        MCInputNii=RMC.main(InputNii)
                        
                        GLM.main(MCInputNii,meth,Regressor,con)         
                        print 'Reg:\t{Regressor}\nFile:\t{InputNii}\nMeth:\t{meth}'.format(Regressor=Regressor,InputNii=MCInputNii,meth=meth)
              
              
              
                elif MC=='MCST':
                    
                    print 'Method:\t{MC}\n{ln}'.format(MC=MC,ln=ln)
    
                    
                    MCinputNii=RMC.main(target)
                    
                    Files,MethOrder=STC.main(MCinputNii)
                    print 'STC Files:\n{}'.format(Files)
    
                    for InputNii,meth in zip(Files,MethOrder):
                        
                        if meth=='Filt':
                            Regressor='/share/studies/David_FS/Real/MotionCorrection/{}/{}/{}/20_Visual.txt'.format(motion,subID,MC)
                        else:
                            Regressor='/share/studies/David_FS/Real/MotionCorrection/{}/{}/{}/Visual.txt'.format(motion,subID,MC)
                    
                        GLM.main(InputNii,meth,Regressor,con)                
                        print 'Reg:\t{Regressor}\nFile:\t{InputNii}\nMeth:\t{meth}'.format(Regressor=Regressor,InputNii=InputNii,meth=meth)
        
        
        print '\n\n{0}\n{0}\n\n'.format(ln)        

