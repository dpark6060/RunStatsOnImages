#!/usr/bin/env python
import nibabel as nb
import numpy as np
import sys
import os
import glob
import matplotlib.pyplot as pl
import scipy.stats as sts
import subprocess as sp

def main(InputFile):
    base,Sh=os.path.split(InputFile)
    cmd='cd {};./{}'.format(base,Sh)
    print Sh
    pr=sp.Popen(cmd,shell=True)
    pr.wait()
    return()
