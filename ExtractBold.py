#!/usr/bin/env python
import numpy as np
import sys
import os
import glob

def main(File,Key,fs,Output,Fbold=100.0):

    data=np.loadtxt(File)
    Numbers=data[:,0]
    region=np.where(Numbers==Key)[0][0]
    bold=data[region,1:]
    Down=int(np.round(Fbold/fs))
    print 'Downsampling Regressor from {} to by {}/{}={}'.format(Fbold,Fbold,fs,Down)
    bold2=bold[::Down]
    np.savetxt(Output,bold2)
    return()







