#!/usr/bin/env python

############################################################################### Multiple Regression
### This function is written with numpy and scipy to perform Multiple Regression 
### The dependent variable inputs Y should be column vectors
### The independent variable/s input X can be a sigle or multi-column vector
### The number of columns in X determines the number of independent variables
### It will spit out the results by default and it can all return the results if
### the PRT variable is set to 1 
### Number of rows in Y and X show be equal and is the number of sample

import numpy as np
import scipy.stats as sps
import matplotlib.pylab as pb

def MultipleRegression(Y, X, PRT=0):
	#print 'THIS ONE'
	
	# Extract the number of samples
	NumberOfSample = Y.size
	
	# Reshaping Y to have coulmn shape
	Y = Y.reshape(Y.size,1)
	
	# Extract the number of independent variables
	if np.size(X.shape)==1 :
		NumberOfVar = 1
		X = X.reshape(Y.size,1)
	else:	
		if X.shape[1] == Y.size:
			NumberOfVar = X.shape[0]
		else:
			NumberOfVar = X.shape[1]
	
	# Reshaping the data to column vectors
	if ((X.shape[0]!=NumberOfSample) & (X.shape[1]!=NumberOfVar)):
		X=X.T
		
		
	dof = NumberOfSample - NumberOfVar - 1 
	
	# Add a colume of one as the first column for intercept
	A = np.ones((NumberOfSample,NumberOfVar+1))
	A[:,1:(NumberOfVar+1)] = X.copy()
	
	# Compute the Beta coefficients
	Inv = pb.inv(np.dot(A.T, A))
	SecondTerm = np.dot(A.T, Y)
	
	Betas = np.dot(Inv, SecondTerm)
	
	# Compute the residuals
	Residuals = Y - np.dot(A, Betas) 
	
	# Compute the mean squared error
	MSE = (np.square(Residuals)).sum()/(dof)
	
	# Compute the standard error for Betas		
	Betas_SE = np.sqrt((MSE * Inv).diagonal())

	# Compute the T test statistics for each Beta and corresponding P value
	Tstats = np.zeros((NumberOfVar+1))
	Pvalues = np.zeros((NumberOfVar+1))
	for i in xrange(NumberOfVar+1):
		Tstats[i] = Betas[i]/Betas_SE[i]
		Pvalues[i] = 2*(1.0 - sps.t( dof ).cdf( abs(Tstats[i]) ))

	
	# Compute the R squared
	Rsquared = 1 - (((np.square(Residuals)).sum()) / ((np.square(Y-Y.mean())).sum()))
	
	# Compute the adjusted R squared
	Adj_Rsquared = Rsquared - (1-Rsquared)*(NumberOfVar/float(dof))
	
	# Compute F stats and probability
	MSM = (np.square(np.dot(A, Betas) - Y.mean())).sum() / NumberOfVar
	F = MSM / MSE
	Fprob = 1.0 - sps.f.cdf(F,NumberOfVar,dof)
	

	# Print out the results
	if (PRT ==0):
		
		print("=========================================================")
		print("                  coef               t              P>|t|   ")
		print("---------------------------------------------------------")
		print("Intercept        % .4f            % .4f        %.4f  " % (Betas[0][0],Tstats[0],Pvalues[0]))
		
		for i in xrange(NumberOfVar):
			print("X%1d               % .4f            % .4f        %.4f  " % (i,Betas[i+1][0],Tstats[i+1],Pvalues[i+1]))
			return Betas.flatten(), Tstats.flatten(), Pvalues.flatten(), Residuals.flatten()

	# Return the results 
	else:

		return Betas.flatten(), Tstats.flatten(), Pvalues.flatten(), Residuals.flatten()






