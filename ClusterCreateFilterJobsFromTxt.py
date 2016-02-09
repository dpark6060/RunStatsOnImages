#!/usr/bin/env python

import scipy as sp
import numpy as np,sys
import nibabel as nb
import scipy.signal as sig
import matplotlib.pyplot as pl
import sys
import time
import os
import glob
from subprocess import Popen, PIPE
#from multiprocessing import Pool


def MakeT(Int,Start,NumSlices,Tr):
# Creates timing sequence for the slices in a given image.
# Int - the interpolation value (1 - sequential, 2 - Odd/Even, 3 - 1,4,7,... 2,5,8,... 3,6,9..., etc)
# Start - the slice number to align to. 0 indicates the first slice.
# NumSlices - the total number of slices
# Tr - the TR of the data, or the sampling rate.

# Calculate dt: the time interval between any two slices acquired sequentially
	print Tr
	print NumSlices
	dt=float(Tr)/float(NumSlices)
	IntSeq=[]
	
# Create slice acquisition order sequence
	for i in range(int(Int)):
		IntSeq.extend(range(i,int(NumSlices),int(Int)))    
	IntSeq=np.array(IntSeq)

# Initialize slice timing array
	TimeList=range(len(IntSeq))
	trash,TimeList=zip(*sorted(zip(IntSeq,TimeList)))
	
	TimeList=np.array(TimeList)
	print TimeList
	print dt
	TimeList=(TimeList-TimeList[Start])*dt
	
	
	
# Zero the acquisition time around the slice of interest    
	return(IntSeq,TimeList)

def RunOnFile(InputNii,WrkDir,TxtOutput,Fs,Int,Fnew):
	print Fs
	RootDir,FileName=os.path.split(InputNii)
	ClusterJobDir=os.path.join(WrkDir,'ShFiles','Filt')
	ErrorOutput=os.path.join(WrkDir,'ClusterError','Filt')
	ClusterOutput=os.path.join(WrkDir,'ClusterOutput','Filt')
	
	if not os.path.exists(ClusterJobDir):
		os.mkdir(ClusterJobDir)
	if not os.path.exists(ErrorOutput):
		os.mkdir(ErrorOutput)    
	if not os.path.exists(ClusterOutput):
		os.mkdir(ClusterOutput)
	
	trash='.exe'
	subID=FileName
	while trash:
		subID,trash=os.path.splitext(subID)
	   
	
	SplitBase=subID
	
	Tr=1./Fs
	RefSlice=0
	
	Nii=nb.load(InputNii)
	NiiData=Nii.get_data()
	per=np.percentile(NiiData,3)
	lx,ly,lz,lt=NiiData.shape
	SliceOrder, SliceShift = MakeT(Int, RefSlice, lz, Tr) 
	txtLen=3000
	print 'ITS THIS ONE'
	SliceLen=glob.glob(os.path.join(TxtOutput,'SliceLen_*.txt'))
	
	if not SliceLen:   
	
		for z in range(lz):
			print z
			Extract=np.squeeze(NiiData[:,:,z,:])
			Extract=np.reshape(Extract,(-1,lt))
			LexOrig=len(Extract)
			ind=np.where(Extract.min(1)>per)
			Extract=Extract[ind]
			lentxt=os.path.join(TxtOutput,'SliceLen_{}.txt'.format(z))
			indtxt=os.path.join(TxtOutput,'SliceInd_{}.txt'.format(z))
			print LexOrig
			
			np.savetxt(lentxt,[LexOrig])
			np.savetxt(indtxt,ind[0])
			  
			for ii,inc in enumerate(range(0,len(Extract),txtLen)):
				
				if inc+txtLen>=len(Extract):
					txtdat=Extract[inc:]
				else:
					txtdat=Extract[inc:inc+txtLen]
				
				TxtName=os.path.join(TxtOutput,'Image_{}_{}.txt'.format(z,ii))
				
				np.savetxt(TxtName,txtdat)
			
				shPath=os.path.join(ClusterJobDir,'{}_slice{}_{}.sh'.format(subID,z,ii))
				
				if os.path.isfile(shPath):
					os.remove(shPath)
				
				shFile=open(shPath,'w')
				
				###################################################
				###### Create .sh file to submit to cluster #######
				###################################################
				
				shFile.write('#!/bin/bash\n')
				shFile.write('############################\n')
				shFile.write('# Job Options & Parameters #\n')
				shFile.write('############################\n')
				shFile.write('# (2) Resource Requirements:\n')
				shFile.write('#$ -l mem_free=4G\n')
				shFile.write('#$ -l h_vmem=5G\n')
				shFile.write('# (3) Environment Setup:\n')
				shFile.write('#$ -cwd\n')
				shFile.write('#$ -j y\n')
				shFile.write('#$ -S /bin/bash\n')
				shFile.write('#$ -o {}\n'.format(ClusterOutput))
				shFile.write('#$ -e {}\n'.format(ErrorOutput))
				shFile.write('# (4) Job:\n')
				shFile.write('source ~/.bashrc\n')
				shFile.write('source /usr/local/UniversalPathSetup.sh\n')
				shFile.write('cd /share/users/dparker/Code/Python/GenericCode/RunStatsOnImg \n')
				shFile.write('python ClusterFilterTxt.py {} {} {} {} {}\n'.format(TxtName,SliceShift[z],Fs,shPath,Fnew))
				shFile.close()
				
			
	else:
		print('{} Text Files Exist, Recreating Jobs'.format(subID))
		
		
		for z in range(lz):            
			txtfiles=glob.glob(os.path.join(TxtOutput,'{}_{}_*.txt'.format('Image',z)))
			print os.path.join(TxtOutput,'{}_{}_*.txt'.format('Image',z))
			for ii,f in enumerate(txtfiles):
				
				
				TxtName=os.path.join(TxtOutput,'{}_{}_{}.txt'.format('Image',z,ii))
				shPath=os.path.join(ClusterJobDir,'{}_slice{}_{}.sh'.format(subID,z,ii))                #print shPath
				if os.path.isfile(shPath):
					os.remove(shPath)
				
				Output=os.path.join(TxtOutput,'Filt_{}_{}_{}.txt'.format('Image',z,ii))
				if not os.path.exists(Output):
					shFile=open(shPath,'w')
					
					###################################################
					###### Create .sh file to submit to cluster #######
					###################################################
					
					shFile.write('#!/bin/bash\n')
					shFile.write('############################\n')
					shFile.write('# Job Options & Parameters #\n')
					shFile.write('############################\n')
					shFile.write('# (2) Resource Requirements:\n')
					shFile.write('#$ -l mem_free=4G\n')
					shFile.write('#$ -l h_vmem=5G\n')
					shFile.write('# (3) Environment Setup:\n')
					shFile.write('#$ -cwd\n')
					shFile.write('#$ -j y\n')
					shFile.write('#$ -S /bin/bash\n')
					shFile.write('#$ -o {}\n'.format(ClusterOutput))
					shFile.write('#$ -e {}\n'.format(ErrorOutput))
					shFile.write('# (4) Job:\n')
					shFile.write('source ~/.bashrc\n')
					shFile.write('source /usr/local/UniversalPathSetup.sh\n')
					shFile.write('cd /share/users/dparker/Code/Python/GenericCode/RunStatsOnImg \n')
					shFile.write('python ClusterFilterTxt.py {} {} {} {} {}\n'.format(TxtName,SliceShift[z],Fs,shPath,Fnew))
					shFile.close()
	print SliceShift
	np.savetxt(os.path.join(TxtOutput,'SliceOrder.txt'),SliceOrder)
	np.savetxt(os.path.join(TxtOutput,'SliceShift.txt'), SliceShift)
	
	
   
if __name__=="__main__":
	#print (sys.argv[4])
	RunOnFile(sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4],float(sys.argv[5]),int(sys.argv[6]))
	
