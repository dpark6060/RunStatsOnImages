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


def main(Regressor,Data):
    Reg=np.loadtxt(Regressor)
    Slice=nb.load(Data).get_data()    
    Lx,Ly,Lz,Lt=Slice.shape    
    Betas=np.zeros((Lx,Ly,Lz))
    Tstat=np.zeros((Lx,Ly,Lz))
    Pval=np.zeros((Lx,Ly,Lz))
    
    for x in range(Lx):
        for y in range(Ly):
            for z in range(Lz):
                
            
                r=CallGLM(np.squeeze(Slice[x,y,z,:]),Reg)
                
                Betas[x,y,z]=r[0][1]
                Tstat[x,y,z]=r[1][1]
                Pval[x,y,z]=r[2][1]
            
    return Betas,Tstat,Pval

    
if __name__ == '__main__':
    
    main(sys.argv[1],sys.argv[2],sys.argv[3])

