#!/usr/bin/env python


import glob
import os
import sys
import numpy as np
import time
import MakeGLMSh as GLMsh
import subprocess as sp
import nibabel as nb
from pylab import *
import scipy.signal as sig
from scipy import interpolate as tpl
from multiprocessing import Pool
import subprocess as sp
from scipy import interpolate as tpl




def MakeT(Int,Start,NumSlices,Tr):
# Creates timing sequence for the slices in a given image.
# Int - the interpolation value (1 - sequential, 2 - Odd/Even, 3 - 1,4,7,... 2,5,8,... 3,6,9..., etc)
# Start - the slice number to align to. 0 indicates the first slice.
# NumSlices - the total number of slices
# Tr - the TR of the data, or the sampling rate.

# Calculate dt: the time interval between any two slices acquired sequentially
	print Tr
	print NumSlices
	dt=float(Tr)/float(NumSlices)   # Calculate the change in time between acquisition of slices
	IntSeq=[]           # Initialize the sequence order array
	
# Create slice acquisition order sequence
	for i in range(int(Int)):
		IntSeq.extend(range(i,int(NumSlices),int(Int)))    

# Initialize slice timing array
	TimeList=range(len(IntSeq))
	trash,TimeSeq=zip(*sorted(zip(IntSeq,TimeList)))
	
	TimeSeq=np.array(TimeSeq)
	TimeSeq=(TimeSeq-TimeSeq[Start])*dt # Adjust shift times for which slice you're starting at
	print TimeSeq
	print IntSeq
	return(IntSeq,TimeSeq)




def Report(ReportFile,Syntax):
	cmd='echo {} >> {}'.format(Syntax,ReportFile)
	os.system(cmd)
	os.system("echo >> {}".format(ReportFile))
	pass    


def usage():
	print'USAGE: ./RunLinRegCompleteOnFile.py <InputFile> <con> <Regressor.txt> <Meth>'

def main(InputNii,con,Regressor,meth,TR,itl,Fs,WrkDir=''):
	
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
		nslice=img.get_shape()[2]
		

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
		
		vols=sorted(glob.glob(os.path.join(GLMFiles,'vol*.nii.gz')))
		nVols=len(vols)        
		
		SlicesOrder,SliceTiming=MakeT(itl,0,nslice,TR)
		
		Regressor=np.loadtxt(Regressor)
		if not len(Regressor) >= img.shape[-1]*np.round(Fs*TR):
			print 'Interpolating'
			t1=np.array(range(len(Regressor)))*2
			t20=np.arange(t1[0],t1[-1],1./Fs)
			f=tpl.interp1d(t1,Regressor,kind='cubic')
			Regressor=f(t20)
			
		
		for k in xrange(img.shape[2]):
			RegressorDownsampled=np.zeros((img.shape[-1]))
			
			if len(Regressor[np.round(SliceTiming[k]*Fs)::(np.round(Fs*TR))])<img.shape[3]:
				RegressorDownsampled = list(Regressor[np.round(SliceTiming[k]*Fs)::np.round(Fs*TR)]).append(0)       
			else:   
				RegressorDownsampled = Regressor[np.round((SliceTiming[k])*Fs)::np.round(Fs*TR)]
				print 'slice {} starting at {}*{}={}::{}'.format(k,SliceTiming[k],Fs,np.round(SliceTiming[k]*Fs),np.round(Fs*TR))
				

			print len(RegressorDownsampled)
			np.savetxt(os.path.join(GLMFiles,'SliceReg{0:04d}.txt'.format(int(k))),RegressorDownsampled,fmt='%1.16f')
		
		regs=sorted(glob.glob(os.path.join(GLMFiles,'SliceReg*.txt')))
		nRegs=len(regs)
		
		if not nRegs==nVols:
			print ('Number of slices does not equal number of regs')
			return
		
		Report(ReportFile,'Number of Vols: {}'.format(nVols))
		for v,r in zip(vols,regs):
			trash,volID=os.path.split(v)
	
			volID,trash=os.path.splitext(volID)
	
			while trash:
				volID,trash=os.path.splitext(volID)
	
				
			rpt='Making SH for Volume {}'.format(volID)
			Report(ReportFile,rpt)
			shPath=os.path.join(ClusterJobDir,volID+'.sh')
			GLMsh.main(v,r,RV,shPath,ErrorOutput,ClusterOutput)
		
	
		SubmitFiles=glob.glob(ClusterJobDir+'/*.sh')
		p=Pool(20)
		p.map(SH.main,SubmitFiles)
		p.close()
		p.join()
		
		Min=0
		Nvols=len(glob.glob(os.path.join(GLMFiles,'vol*')))
		NBetas=len(glob.glob(os.path.join(GLMFiles,'Beta*')))
		
		while not Nvols==NBetas and Min<120:
			time.sleep(60)
			Min=Min+1
			Nvols=len(glob.glob(os.path.join(GLMFiles,'vol*')))
			NBetas=len(glob.glob(os.path.join(GLMFiles,'Beta*')))
			
			if Min==120:
				print ('Timeout Error For {}'.format(InputNii))
				Report(ReportFile,'Timeout Error For {}'.format(InputNii))
			print 'waiting'
			
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
	
	if not len(sys.argv)==8:
		usage()
	else:
		main(sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4],float(sys.argv[5]),float(sys.argv[6]),float(sys.argv[7]))
#   def main(InputNii,     con, Regressor,    meth,     TR,     itl,        Fs  ,WrkDir=''):

