#!/usr/bin/env python


import glob
import os
import sys
import numpy as np
import time
import MakeGLMSh as GLMsh
import subprocess as sp
import nibabel as nb



def Report(ReportFile,Syntax):
    cmd='echo {} >> {}'.format(Syntax,ReportFile)
    os.system(cmd)
    os.system("echo >> {}".format(ReportFile))
    pass    


def usage():
    print'USAGE: ./RunLinRegCompleteOnFile.py <InputFile> <con> <Regressor.txt> <Meth>'

def main(InputNii,con,Regressor,meth,WrkDir='',OutputDir=''):
    
    txt=np.loadtxt(Regressor)
    if not all([i==0 for i in txt]):
        
        RootDir,FileName=os.path.split(InputNii)
    
        trash='.exe'
        FileBase=FileName
        while trash:
            FileBase,trash=os.path.splitext(FileBase)
    
           
        OutputPath=os.path.join(RootDir,'tPython',meth,con)
        
        if not WrkDir:
            WrkDir=os.path.join(RootDir,'{}_Work'.format(FileBase))
            
        GLMFiles=os.path.join(WrkDir,'WorkFiles','GLM',meth,con)
        ClusterJobDir=os.path.join(WrkDir,'ShFiles','GLM',meth,con)
        ErrorOutput=os.path.join(WrkDir,'ClusterError','GLM',meth,con)
        ClusterOutput=os.path.join(WrkDir,'ClusterOutput','GLM',meth,con)
        
        ReportFile=os.path.join(GLMFiles,'Report.txt')
        if os.path.exists(ReportFile):
            cmd='rm {}'.format(ReportFile)
            print cmd
            os.system(cmd)
        BaseDir,fname=os.path.split(InputNii)
        
        while not fname.find('.')==-1:
            fname,trash=os.path.splitext(fname)
            
        
        if not os.path.exists(WrkDir):
            os.makedirs(WrkDir)
    
        if not os.path.exists(ClusterJobDir):
            os.makedirs(ClusterJobDir)
        else:
            cmd='rm {}/*.sh'.format(ClusterJobDir)
            Report(ReportFile,cmd)
            os.system(cmd)
        
        if not os.path.exists(GLMFiles):
            os.makedirs(GLMFiles)
        else:
            cmd='rm {}/*'.format(GLMFiles)
            Report(ReportFile,cmd)
            os.system(cmd)
            
        if not os.path.exists(ErrorOutput):
            os.makedirs(ErrorOutput)
        else:
            cmd='rm {}/*'.format(ErrorOutput)
            Report(ReportFile,cmd)
            os.system(cmd)
            
            
        if not os.path.exists(ClusterOutput):
            os.makedirs(ClusterOutput)
        else:
            cmd='rm {}/*'.format(ClusterOutput)
            Report(ReportFile,cmd)
            os.system(cmd)
            
            
        if not os.path.exists(OutputPath):
            os.makedirs(OutputPath)
        print InputNii
        img=nb.load(InputNii)
        nb.loadsave.save(img,'{}/FullNii.nii.gz'.format(GLMFiles))
        # cmd='cp {} {}/FullNii.nii'.format(InputNii,GLMFiles)
        # print cmd
        # process=sp.Popen(cmd,shell=True)
        # process.wait()
        
        cmd='fslsplit {0}/FullNii.nii {0}/RefVol -t'.format(GLMFiles)
        Report(ReportFile,cmd)
        process=sp.Popen(cmd,shell=True)
        process.wait()
        
        RVs=glob.glob(os.path.join(GLMFiles,'RefVol*'))
        
        for r in RVs[1:]:
            cmd='rm {}'.format(r)
            Report(ReportFile,cmd)
            process=sp.Popen(cmd,shell=True)
            process.wait()
        
        RV=RVs[0]
        cmd='fslsplit {} {}/RefZ -z'.format(RV,GLMFiles)
        Report(ReportFile,cmd)
        process=sp.Popen(cmd,shell=True)
        process.wait()    
        RefVol=RV
        
        
        RVs=glob.glob(os.path.join(GLMFiles,'RefZ*'))
        for r in RVs[1:]:
            cmd='rm {}'.format(r)
            Report(ReportFile,cmd)
            process=sp.Popen(cmd,shell=True)
            process.wait()
        RV=RVs[0]
        
        cmd='fslsplit {0}/FullNii.nii {0}/vol -z'.format(GLMFiles)
        Report(ReportFile,cmd)
        process=sp.Popen(cmd,shell=True)
        process.wait()
        
        vols=glob.glob(os.path.join(GLMFiles,'vol*.nii.gz'))
        nVols=len(vols)
        Report(ReportFile,'Number of Vols: {}'.format(nVols))
        for v in vols:
            trash,volID=os.path.split(v)
    
            volID,trash=os.path.splitext(volID)
    
            while trash:
                volID,trash=os.path.splitext(volID)
    
                
            rpt='Making SH for Volume {}'.format(volID)
            Report(ReportFile,rpt)
            shPath=os.path.join(ClusterJobDir,volID+'.sh')
            GLMsh.main(v,Regressor,RV,shPath,ErrorOutput,ClusterOutput)
        
    
        SubmitCmd='for Dir in `/bin/ls '+ClusterJobDir+'/*.sh`; do echo "Running GLM on ${Dir}.";qsub -cwd $Dir;sleep 2; done'
        Report(ReportFile,cmd)
        os.system(SubmitCmd)
        
        Min=0
        Nvols=len(glob.glob(os.path.join(GLMFiles,'vol*')))
        NBetas=len(glob.glob(os.path.join(GLMFiles,'Beta*')))
        
        while not Nvols==NBetas and Min<120*2:
            time.sleep(60)
            Min=Min+1
            Nvols=len(glob.glob(os.path.join(GLMFiles,'vol*')))
            NBetas=len(glob.glob(os.path.join(GLMFiles,'Beta*')))
            
            if Min==120*2:
                print ('Timeout Error For {}'.format(InputNii))
                Report(ReportFile,'Timeout Error For {}'.format(InputNii))
            print 'waiting'
            
        
        if Min<120*2:    
            Betas=sorted(glob.glob(os.path.join(GLMFiles,'Beta*')))
            #Report(ReportFile,cmd)
            files=''
            for b in Betas:
                files=files+b+' '
            cmd='fslmerge -z {} {}'.format(os.path.join(OutputPath,'Beta'),files)
            Report(ReportFile,cmd)
            process=sp.Popen(cmd,shell=True)
            process.wait()
            
            cmd='fslcpgeom {} {}'.format(RefVol,os.path.join(OutputPath,'Beta'))
            Report(ReportFile,cmd)
            process=sp.Popen(cmd,shell=True)
            process.wait()        
            
            Betas=sorted(glob.glob(os.path.join(GLMFiles,'tStat*')))
            #print Betas
            files=''
            for b in Betas:
                files=files+b+' '
            cmd='fslmerge -z {} {}'.format(os.path.join(OutputPath,'tStat'),files)
            Report(ReportFile,cmd)
            process=sp.Popen(cmd,shell=True)
            process.wait()
            
            cmd='fslcpgeom {} {}'.format(RefVol,os.path.join(OutputPath,'tStat'))
            Report(ReportFile,cmd)
            process=sp.Popen(cmd,shell=True)
            process.wait()
            
            
            Betas=sorted(glob.glob(os.path.join(GLMFiles,'pVal*')))
            #print Betas
            files='' 
            for b in Betas:
                files=files+b+' '
            cmd='fslmerge -z {} {}'.format(os.path.join(OutputPath,'pVal'),files)
            Report(ReportFile,cmd)
            process=sp.Popen(cmd,shell=True)
            process.wait()
            
            cmd='fslcpgeom {} {}'.format(RefVol,os.path.join(OutputPath,'pVal'))
            Report(ReportFile,cmd)
            process=sp.Popen(cmd,shell=True)
            process.wait()
        
    else:
        print ('All Zero Regressor.  Skipping.')
    
    

if __name__ == '__main__':
    
    if not len(sys.argv)==5:
        usage()
    else:
        main(sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4])


