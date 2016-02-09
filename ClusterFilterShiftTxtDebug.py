#!/usr/bin/env python

import scipy as sp
import numpy as np,sys
import nibabel as nb
import scipy.signal as sig
import time
import sys
import os
from multiprocessing import Pool
import multiprocessing



##################################################################################################
##################################################################################################
## Filter Construction functions:
##
## BANDPASS: Allows for the creation of a kaiser window bandpass filter
## CutOffFreq: [fstop1, fstop2]
## SamplingRate: sampling frequency of data
## StopGain: the gain of the stopband, where the stopband gain = -1*StopGain dB
## TranWidth: the transition width of the filter centered around the cutoff frequency.
## For example, if Fcutoff = 2hz, and TranWidth = 0.8, the transition band will be 1.6hz - 2.4 hz 
##
##
## LOWPASS: Allows for the creation of a kaiser window lowpass filter
## CutOffFreq: [fstop1]
## SamplingRate: sampling frequency of data
## StopGain: the gain of the stopband, where the stopband gain = -1*StopGain dB
## TranWidth: the transition width of the filter centered around the cutoff frequency.
## For example, if Fcutoff = 2hz, and TranWidth = 0.8, the transition band will be 1.6hz - 2.4 hz 
##
##################################################################################################
##################################################################################################

def bandpass(CutOffFreq, SamplingRate, StopGain, TranWidth):
	NiquistRate = SamplingRate/2.0
	N, beta = sig.kaiserord(StopGain,TranWidth/NiquistRate)
	taps = sig.firwin(N, CutOffFreq, window=('kaiser', beta), pass_zero=False, scale=True, nyq=NiquistRate)
	return (taps,NiquistRate)

def lowpass(CutOffFreq, SamplingRate, StopGain, TranWidth):
	NiquistRate = SamplingRate/2.0   
	N, beta = sig.kaiserord(StopGain,TranWidth/NiquistRate)        
	taps = sig.firwin(N, CutOffFreq, window=('kaiser', beta), pass_zero=True, scale=True, nyq=NiquistRate)
	return (taps,NiquistRate)


def loadNIIimg(Fname):
	img=nb.load(Fname).get_data()
	return img



def FiltShift(Zimg,tShift,Fs,meta,Fnew):
# The main filtershift function, takes a single vector ZTshift
# ZTshift: [Slice Number, Time Shift]
# where Slice Number is the index of the slice to be shifted, and Time Shift is the amount to shift.  This can be positive or negative.

# Set sampling information  
	Tr= 1./Fs
	Foriginal = Fs # Hz
	#Fnew = np.ceil( #Hz
	Stopgain = 60 # -1*dB
	Tranwidth = 0.08 # Hz
	print 'TR:{}'.format(Tr)
	print 'Foriginal:{}'.format(Fs)
	print 'Fnew:{}'.format(Fnew)
	print 'tShift:{}'.format(tShift)


# The slice is extracted from the 4D global image and reshaped into a 3D volume, representing the 2D slice and its time series.
	#dbg.write(time.ctime()+': Extracting slice {}\n'.format(Z))
	#dbg.flush()
	base,fname=os.path.split(Zimg)
	
	ext='.exe'
	fnameStrip=fname
	while ext:
		fnameStrip,ext=os.path.splitext(fnameStrip)
		
	
	
	
	debugFolder=os.path.join(base,'Debug')
	if not os.path.exists(debugFolder):
		try:
			os.mkdir(debugFolder)
		except:
			print('debugFolder Already Created...hopefully')
	
# Create lowpass Filter
	BPF, Nyq = lowpass(0.2, Fnew, Stopgain, Tranwidth)
	Sig=np.loadtxt(Zimg)
	print Sig.dtype
# The time axis must be the last dimension.
	tdim=len(list(np.shape(Sig)))-1    
	
# Length Time Sig (LTS) is the length of the time series associated with the slice signal.
	LTS=Sig.shape[-1]

# Padding is added to the front end end of the slice, where half the signal is mirrored on each end
# FR - Front Range: the range of indicies to be padded on the front (beginning) of the signal
# FR starts at 1 and ends at LTS/2. (0 is the first index)
# BR - Back Range: the range of indicies to be padded on the back (end) of the signal
# BR starts at LTS-1 and goes to LST/2
	FR=np.array(range(int(round(LTS/2.)),0,-1))
	BR=np.array(range(LTS-1,int(FR.shape[-1])-1,-1))

	#dbg.write('{}: Slice {}, Padding...\n'.format(time.ctime(),Z))        
	#dbg.flush()
# Pad the signal, with conditions for each dimension so that all data shapes can be accomodated. 
	if tdim==0:
	# One dimensional case (Single Vector)
	
# The signal to be padded on the front is the values of Sig at indecies FR
# The signal to be padded to the     
		FrontPad=(Sig[FR])	
		BackPad=Sig[BR]

# The length of the padding is stored as LFP
		LFP=FrontPad.shape[-1]
	

	elif tdim==1:
	
		FrontPad=Sig[:,FR]
		BackPad=Sig[:,BR]
	

		LFP=FrontPad.shape[-1]

	elif tdim==2:
	
		FrontPad=Sig[:,:,FR]
		BackPad=Sig[:,:,BR]

		LFP=FrontPad.shape[-1]

	elif tdim==3:
	
		FrontPad=Sig[:,:,:,FR]
		BackPad=Sig[:,:,:,BR]

		LFP=FrontPad.shape[-1]

	else:
		print('Bad Array Dimensions for Padding')

# The padding is added to the signal along the time axis
	Sig=np.concatenate((FrontPad,Sig,BackPad),-1)
	#dbg.write('{}: Slice {}, Done\n'.format(time.ctime(),Z))        
	#dbg.flush()
# Upsampling/interpolation paramaters are calculated
# S: Upsampling Factor, or the number of samples to be added between existing samples
# Dm: the dimensions that the upsampled signal will be
# SS: the dimensions of the padded signal
	S=int(round(Fnew/Foriginal))
	Dm=list(np.shape(Sig))
	SS=Dm
	tdim=len(Dm)-1
	Dm[tdim]=Dm[tdim]*S

# Initialize upsampled signal as zeros
	ZeroSig=np.zeros(Dm)

	k=0
	#dbg.write('{}: Slice {}, Creating Upsampled Version\n'.format(time.ctime(),Z))        
	#dbg.flush()
# Create Zero Padded Signal    
	if tdim==0:

	
# Assign every S samples in ZeroSig to values in Sig    
		ZeroSig[::S]=Sig
	elif tdim==1:       
		ZeroSig[:,::S]=Sig
	elif tdim==2:        
		ZeroSig[:,:,::S]=Sig                 
	elif tdim==3:       
		ZeroSig[:,:,:,::S]=Sig
	else:
		print("Bad Array Dimensions")  

# Cleanup Sig as it's no longer needed   
	del Sig    
	#dbg.write('{}: Slice {}, Upsampling Complete\n'.format(time.ctime(),Z))        
	#dbg.flush()
# Filter the Zero padded signal with the designed filter

	#dbg.write('{}: Slice {}, Filtering...\n'.format(time.ctime(),Z))        
	#dbg.flush()
	
	
	####################################################
	################## DEBUGGING #######################
	####################################################
	
	sampleSeconds=8*Tr
	dl=sampleSeconds*Fnew/2
	if tdim==0:
		lsig=len(ZeroSig)
		mid=int(np.round(lsig/2))
		debugSample=ZeroSig[mid-dl:mid+dl]
		
	elif tdim==1:
		x,lsig=np.shape(ZeroSig)
		xmid=int(np.round(x/2))
		mid=int(np.round(lsig/2))
		debugSample=ZeroSig[xmid,mid-dl:mid+dl]
		
	elif tdim==2:
		x,y,lsig=np.shape(ZeroSig)
		xmid=int(np.round(x/2))
		ymid=int(np.round(y/2))
		mid=int(np.round(lsig/2))
		debugSample=ZeroSig[xmid,ymid,mid-dl:mid+dl]	
		
	elif tdim==3:
		x,y,z,lsig=np.shape(ZeroSig)
		xmid=int(np.round(x/2))
		ymid=int(np.round(y/2))
		zmid=int(np.round(z/2))
		mid=int(np.round(lsig/2))
		debugSample=ZeroSig[xmid,ymid,zmid,mid-dl:mid+dl]
	
	debugFig=pl.figure(figsize=(17,8))
	ax1=debugFig.add_subplot(111)
	t=np.array(range(len(debugSample)))/Fnew
	ax1.plot(t,debugSample)
	figName=os.path.join(debugFolder,'{}_ZeroPad.pdf'.format(fnameStrip))
	debugFig.savefig(figName)
	pl.close(debugFig)

	####################################################
	####################################################
	
	ZeroSig = sig.filtfilt(BPF, [1], ZeroSig*float(S), axis=-1,padtype='even', padlen=0)
	
	####################################################
	################## DEBUGGING #######################
	####################################################
	
	sampleSeconds=8*Tr
	dl=sampleSeconds*Fnew/2
	if tdim==0:
		lsig=len(ZeroSig)
		mid=int(np.round(lsig/2))
		debugSample=ZeroSig[mid-dl:mid+dl]
		
	elif tdim==1:
		x,lsig=np.shape(ZeroSig)
		xmid=int(np.round(x/2))
		mid=int(np.round(lsig/2))
		debugSample=ZeroSig[xmid,mid-dl:mid+dl]
		
	elif tdim==2:
		x,y,lsig=np.shape(ZeroSig)
		xmid=int(np.round(x/2))
		ymid=int(np.round(y/2))
		mid=int(np.round(lsig/2))
		debugSample=ZeroSig[xmid,ymid,mid-dl:mid+dl]	
		
	elif tdim==3:
		x,y,z,lsig=np.shape(ZeroSig)
		xmid=int(np.round(x/2))
		ymid=int(np.round(y/2))
		zmid=int(np.round(z/2))
		mid=int(np.round(lsig/2))
		debugSample=ZeroSig[xmid,ymid,zmid,mid-dl:mid+dl]
	
	debugFig=pl.figure(figsize=(17,8))
	ax1=debugFig.add_subplot(111)
	t=np.array(range(len(debugSample)))/Fnew
	ax1.plot(t,debugSample)
	figName=os.path.join(debugFolder,'{}_Filtered.pdf'.format(fnameStrip))
	debugFig.savefig(figName)
	pl.close(debugFig)
	####################################################
	####################################################
	
	
	
	
	
	#dbg.write('{}: Slice {}, Filtering complete\n'.format(time.ctime(),Z))     

	#dbg.flush()
# Calculate new frequency and time parameters for the upsampled signal
	tdim=len(SS)-1
	Fs=Fnew
	Ts=1/Fs

# Initialize a variable the length of the padded signal at the original frequency
	Sig=np.zeros(SS)
	
# Calculate the number of indicies to shift when resampling    
	shift=round(tShift*Fs)
	print 'shift:{}'.format(shift)
	print 'tdim:{}'.format(tdim)
# Shift the Signal
	#dbg.write('{}: Slice {}, Shifting...\n'.format(time.ctime(),Z))        
	#dbg.flush()
	if tdim==0:
	# One Dimensional Case (1D vector)
	
		if shift>0:
	# If the shift is larger than zero
	# Extend the Upsampled signal by repeating the values at the beginning of the signal by the shift amount
	# then resample the signal, starting at index 0, every S indecies, to one S of the end
			Rep=np.tile(ZeroSig[0],shift)
			ZeroSig=np.append(Rep,ZeroSig,-1)
			Sig=ZeroSig[range(0,ZeroSig.shape[-1]-S,S)]       
	
		else:
	# If the Shift is less than zero
	# Extend the Upsampled signal by repeating the values at the end of the signal by the shift amount
	# Then resample the signal, starting at index shift, every s indicies, to the end
			Rep=np.tile(ZeroSig[-1],abs(shift))
			ZeroSig=np.append(ZeroSig,Rep,-1)
			Sig=ZeroSig[range(int(abs(shift)),ZeroSig.shape[-1]-1,S)]
	
	# Crop the signal to remove the padding preformed earlier    
		Sig=Sig[LFP:LFP+LTS]
	
	elif tdim==1:   
		if shift>0:
			Rep=np.tile(np.expand_dims(ZeroSig[:,0],axis=-1),[1,shift])
			#Rep=np.expand_dims(Rep,axis=-1)

			ZeroSig=np.append(Rep,ZeroSig,-1)
			Sig=ZeroSig[:,range(0,ZeroSig.shape[-1]-S,S)]       
		
		else:
			Rep=np.tile(np.expand_dims(ZeroSig[:,-1],axis=-1),[1,abs(shift)])
			#Rep=np.expand_dims(Rep,axis=-1)

			ZeroSig=np.append(ZeroSig,Rep,-1)
			Sig=ZeroSig[:,range(int(abs(shift)),ZeroSig.shape[-1]-1,S)]
			
		Sig=Sig[:,LFP:LFP+LTS]

	elif tdim==2: 

		if shift>0:
		
			Rep=np.tile(np.expand_dims(ZeroSig[:,:,0],axis=-1),[1,1,shift])
			#Rep=np.expand_dims(Rep,axis=-1)
			ZeroSig=np.append(Rep,ZeroSig,-1)
			Sig=ZeroSig[:,:,range(0,ZeroSig.shape[-1]-S,S)]       
		
		else:
			Rep=np.tile(np.expand_dims(ZeroSig[:,:,-1],axis=-1),[1,1,abs(shift)])
			#Rep=np.expand_dims(Rep,axis=-1)

			ZeroSig=np.append(ZeroSig,Rep,-1)
			Sig=ZeroSig[:,:,range(int(abs(shift)),ZeroSig.shape[-1]-1,S)]
		
		Sig=Sig[:,:,LFP:LFP+LTS]

	   
	elif tdim==3:   
		if shift>0:
		
			Rep=np.tile(np.expand_dims(ZeroSig[:,:,:,0],axis=-1),[1,1,1,shift])
			#Rep=np.expand_dims(Rep,axis=-1)
			ZeroSig=np.append(Rep,ZeroSig,-1)
			Sig=ZeroSig[:,:,:,range(0,ZeroSig.shape[-1]-S,S)]       
		
		else:
			Rep=np.tile(np.expand_dims(ZeroSig[:,:,:,-1],axis=-1),[1,1,1,shift])
	
			#Rep=np.expand_dims(Rep,axis=-1)
			ZeroSig=np.append(ZeroSig,Rep,-1)
			Sig=ZeroSig[:,:,:,range(int(abs(shift)),ZeroSig.shape[-1]-1,S)]
		
		Sig=Sig[:,:,:,LFP:LFP+LTS]

	else:
	
		print("Bad Array Dimensions")  
	#dbg.write('{}: Slice {}, Shifting Complete\n'.format(time.ctime(),Z))        
	#dbg.flush()
	#print('Slice '+str(Z))

	####################################################
	################## DEBUGGING #######################
	####################################################
	
	sampleSeconds=8
	dl=sampleSeconds/2
	if tdim==0:
		lsig=len(Sig)
		mid=int(np.round(lsig/2))
		debugSample=Sig[mid-dl:mid+dl]
		
	elif tdim==1:
		x,lsig=np.shape(Sig)
		xmid=int(np.round(x/2))
		mid=int(np.round(lsig/2))
		debugSample=Sig[xmid,mid-dl:mid+dl]
		
	elif tdim==2:
		x,y,lsig=np.shape(Sig)
		xmid=int(np.round(x/2))
		ymid=int(np.round(y/2))
		mid=int(np.round(lsig/2))
		debugSample=Sig[xmid,ymid,mid-dl:mid+dl]	
		
	elif tdim==3:
		x,y,z,lsig=np.shape(Sig)
		xmid=int(np.round(x/2))
		ymid=int(np.round(y/2))
		zmid=int(np.round(z/2))
		mid=int(np.round(lsig/2))
		debugSample=Sig[xmid,ymid,zmid,mid-dl:mid+dl]
	
	debugFig=pl.figure(figsize=(17,8))
	ax1=debugFig.add_subplot(111)
	t=np.array(range(len(debugSample)))/Fs
	ax1.plot(t,debugSample)
	figName=os.path.join(debugFolder,'{}_Sampled.pdf'.format(fnameStrip))
	debugFig.savefig(figName)
	pl.close(debugFig)
	####################################################
	####################################################	
	
	savefile=os.path.join(base,'FS_'+fname)
	print savefile
	np.savetxt(savefile,Sig)
	os.system('chmod 777 {}'.format(savefile))
	
	os.system('rm {}'.format(meta))

	return

if __name__=="__main__":
	
	Zimg=sys.argv[1]
	tShift=float(sys.argv[2])
	Fs=float(sys.argv[3])
	meta=sys.argv[4]
	Fnew=float(sys.argv[5])
	
	
	FiltShift(Zimg,tShift,Fs,meta,Fnew)



