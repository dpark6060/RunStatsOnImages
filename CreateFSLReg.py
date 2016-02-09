#!/usr/bin/env python
# encoding: utf-8
"""
ExtractRegionalPETUptake.py
This scripts extract the regional Amloyd PET uptake

Created by Ray Razlighi on 2010-09-08.
Copyright (c) 2010 __MyCompanyName__. All rights reserved.
"""
import sys
import nibabel as nb
import numpy as np
import scipy.stats as sps
import scipy.signal as sig
import matplotlib.pyplot as pl
import os
ReD = "\033[91m"
YelloW = "\033[93m"
EndC = "\033[0m"
def norm(data):
	data=(data-np.mean(data))
	data=data/np.amax(data)
	return data



	
def main(InputFmri,InputStimulus,Output,hrf='/share/studies/David_FS/Real/TextFiles/fslHRF.txt',delay=0):
	print 'Using {}'.format(hrf)

	
	TR = 2     # Input fMRI image repeatition time
	Fs = 20    # HRF sampling rate 
	if not os.path.exists(InputFmri):
		InputFmri=InputFmri+'.gz'
		
	Fmri_Data=nb.load(InputFmri)

	print "load stimulus Sequence, upsample, convolve with HRF, and downsample"
	Stimulus = np.loadtxt(InputStimulus)

	StimulusAtTwentyHz = np.zeros(Fmri_Data.get_shape()[3] * TR * Fs)
	
	for i in xrange(Stimulus.shape[0]):
		StimulusAtTwentyHz[np.round(Stimulus * Fs)[i,0]: (np.round(Stimulus * Fs)[i,0] + np.round(Stimulus * Fs)[i,1]) ] = 1
	
	
	
	print "Load double gamma hemodynamic Impulse respose function"
	#HRF = np.loadtxt('/share/studies/ECFf/Scripts/DoubleGammaHRF_WithUndershoot_20Hz.txt')
	#HRF = np.loadtxt('/share/studies/David_FS/Real/TextFiles/MatlabExtractedFslHrf.txt')
	#HRF = np.loadtxt('/share/studies/David_FS/Real/TextFiles/FslBasisHrf.txt')
	HRF = np.loadtxt(hrf)
	delay=delay*20
	print 'delay: {}'.format(delay)
	#RegressorAtTwentyHz = np.convolve(StimulusAtTwentyHz, HRF, 'full')[:StimulusAtTwentyHz.shape[0]]
	#pl.plot(RegressorAtTwentyHz[::40])
	if delay>0:
		HRF=np.concatenate((np.zeros(delay),HRF[:-1*delay]))	# Delay HRF by 1 sec (Starts later) ../\.. -> ..../\..
	elif delay==0:
		HRF=HRF
	else:
		HRF=np.concatenate((HRF[-1*delay:],np.zeros(-1*delay))) # Delay HRF by -1 sec (Starts ealier) ../\.. -> /\....

	print "Convolve the stimulus with the HRF"
	RegressorAtTwentyHz = np.convolve(StimulusAtTwentyHz, HRF, 'full')[:StimulusAtTwentyHz.shape[0]]
	#pl.plot(RegressorAtTwentyHz[::40])
	#pl.show()
	
	#RegressorAtTwentyHz=sig.lfilter()

	
	print "Downsample the regressor according to the slice number"	
	#SlicesOrder = np.int16(np.loadtxt('/share/studies/ECFf/Scripts/SliceOrder_Philips_37.txt'))
	SlicesOrder = np.int16(np.loadtxt('/share/studies/ECFf/Scripts/SliceOrder_Philips_41.txt'))
	RegressorDownsampled = np.zeros(Fmri_Data.get_shape()[3])	
	
	RegressorDownsampled = norm(RegressorAtTwentyHz[20::40])
	
	np.savetxt(Output,RegressorDownsampled)
	base,fln=os.path.split(Output)
	np.savetxt(os.path.join(base,'20_{}'.format(fln)),norm(RegressorAtTwentyHz))
if __name__ == '__main__':
	
	if len(sys.argv)<2:
		
		print 'Usage: Fmri_Regression.py <InputFmriImage> <InputStimulus> <OutputParFile>' 
		sys.exit(0)


	













