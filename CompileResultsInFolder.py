#!/usr/bin/env python

import os
import glob
import nibabel as nb
import time
import sys
import numpy as np



def CompileNii(OriginalFile):
    
    UnCorNii=os.path.join(OriginalFile)
    UnCorNii=nb.load(UnCorNii)
    lx,ly,lz,lt=UnCorNii.get_data().shape
    
    BaseDir,fname=os.path.split(OriginalFile)
    
    while not fname.find('.')==-1:
        fname,trash=os.path.splitext(fname)
        
    subID=fname
    
    SplitBase=subID
    
    StackList=np.zeros((lx,ly,1,lt))
    
    txtDir=os.path.join(BaseDir,'{}_Work'.format(subID),'WorkFiles','FS')
    
    for z in range(lz):
        zstack=np.zeros((lx*ly,lt))
        ztxts=os.path.join(txtDir,'FS_{}_{}_*.txt'.format('Image',z))
        nzchunks=len(glob.glob(ztxts))
        ind=np.loadtxt(os.path.join(txtDir,'SliceInd_{}.txt'.format(z)))
        if not len(ind)==0:
            print ind.shape
            ind=np.array([int(n) for n in ind])
            print('len ind:\t{}'.format(len(ind)))
            print('ind[-1]:\t{}'.format(ind[-1]))
            print(ind)
            print(ind[:])
            print(ind[0])
            
            zchunks=[]
            for ii in range(nzchunks):
                print(os.path.join(txtDir,'FS_{}_{}_{}.txt'.format('Image',z,ii)))
                newdata=np.loadtxt(os.path.join(txtDir,'FS_{}_{}_{}.txt'.format('Image',z,ii)))
                
                if newdata.ndim==1:
                    newdata=np.expand_dims(newdata,0)
                    
                zchunks.extend(newdata)
            print('len(zchunks):\t{}'.format(len(zchunks)))
            print('shape zchunks:\t{}'.format(np.shape(zchunks)))
            print('shape zstack:\t{}'.format(zstack.shape))
            
            print('zstack[ind,:] shape:\t{}'.format(zstack[ind,:].shape))
            zstack[ind,:]=zchunks
            zstack=np.reshape(zstack,(lx,ly,1,lt))
            StackList=np.concatenate((StackList,zstack),2)
        else:
            EmptyStack=np.zeros((lx,ly,1,lt))
            StackList=np.concatenate((StackList,EmptyStack),2)

    StackList=StackList[:,:,1:,:]
    
    img=nb.Nifti1Image(StackList,UnCorNii.get_affine(),UnCorNii.get_header())
    savefile=os.path.join(BaseDir,'{}_FilterShift_Corrected'.format(subID))
    nb.loadsave.save(img,savefile)
    #print('rm {}/*.txt'.format(BaseDir))
    print(savefile)
    #os.system('rm {}/*.txt'.format(BaseDir))
    return()

    
if __name__=="__main__":
    CompileNii(sys.argv[1])    
    
    
    
    
