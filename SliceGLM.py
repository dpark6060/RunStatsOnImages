#!/usr/bin/env python

#!/usr/bin/env python

import MultipleRegression_David
import multiprocessing.pool as pl
import numpy as np
import nibabel as nb
import sys
import os

def CallGLM(Data,Reg):

    Beta,Tstat,Pval,Res=MultipleRegression_David.MultipleRegression(Data,Reg,1)
    return([Beta,Tstat,Pval,Res])


def main(Regressor,Data,Ref):
    ref=nb.load(Ref)
    Reg=np.loadtxt(Regressor)
    Slice=nb.load(Data).get_data()    
    Lx,Ly,Lz,Lt=Slice.shape    
    reg=np.zeros(Slice.shape)
    Betas=np.zeros((Lx,Ly))
    Tstat=np.zeros((Lx,Ly))
    Pval=np.zeros((Lx,Ly))
    
    for x in range(Lx):
        for y in range(Ly):
            r=CallGLM(np.squeeze(Slice[x,y,:]),Reg)
            
            Betas[x,y]=r[0][1]
            Tstat[x,y]=r[1][1]
            Pval[x,y]=r[2][1]
            
    
    Base,FileBase=os.path.split(Data)
    FileBase,trash=os.path.splitext(FileBase)
    while trash:
        FileBase,trash=os.path.splitext(FileBase)
        
    FINE=nb.Nifti1Image(Betas,ref.get_affine(),ref.get_header())
    nb.loadsave.save(FINE,os.path.join(Base,'Beta_{}.nii.gz'.format(FileBase)))
    
    FINE=nb.Nifti1Image(Tstat,ref.get_affine(),ref.get_header())
    nb.loadsave.save(FINE,os.path.join(Base,'tStat_{}.nii.gz'.format(FileBase)))
    
    FINE=nb.Nifti1Image(Pval,ref.get_affine(),ref.get_header())
    nb.loadsave.save(FINE,os.path.join(Base,'pVal_{}.nii.gz'.format(FileBase)))

    
if __name__ == '__main__':
    
    main(sys.argv[1],sys.argv[2],sys.argv[3])

