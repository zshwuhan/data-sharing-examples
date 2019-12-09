import torch
import torch.nn.functional as F
import math

def logsumexp(inputs, dim=None, keepdim=False):
	return (inputs - F.log_softmax(inputs, dim=dim)).mean(dim, keepdim=keepdim)

def clip(model, C, dim=1):
	example_norms = 0
	for p in model.parameters():
		example_norms += p.grad.data.norm(dim=dim)**2
	example_norms = torch.sqrt(example_norms)
	clip = torch.clamp(example_norms/C, 1.0)
	for p in model.parameters():
		p.grad.data = p.grad.data.div_(clip.unsqueeze(1))

def pickle_stuff(stuff, DPVI_params, pickle_name, path='./results/'):
	import pickle, datetime
	today = datetime.date.today()
	file_name_extend = '_'+str(today.day)+'_'+str(today.month)
	fne_original = file_name_extend
	if np.all(DPVI_params['sigma']==0):
		pickle_name = pickle_name+'_nondp'
	else:
		pickle_name = pickle_name+'_dp'

	fne_extend = 0
	while True:
		try:
			f = open(path+pickle_name+file_name_extend+'.p', 'rb')
			print('You are trying to override an existing pickle file: %s'%pickle_name)
			f.close()
			file_name_extend = fne_original + '('+str(fne_extend)+')'
			fne_extend+=1
		except: 
			pickle.dump(stuff, open(path+pickle_name+file_name_extend+'.p', 'wb'))
			break
	return file_name_extend


import pandas as pd
import numpy as np
def C_n(df, strat_var, binary=True):
	"""
	df: a pandas dataframe
	strat_var: stratification feature
	return: category proportion w.r.t the strat_var
	"""
	sv = df[strat_var]
	C = pd.DataFrame()
	for v in np.unique(sv):
			U_n = np.array(df[df[strat_var] == v].drop(strat_var, axis=1), dtype=np.float32)
			"""
			 There might be countries that have zero entries in certain category.
			 In order to avoid numerical errors, we set 1 as a number of occurences
			 of that particular category in that country.
			"""
			if binary : C[v] = np.sum(U_n, axis=0)/len(U_n)
			else : C[v] = np.sum(U_n, axis=0)/np.sum(U_n)
	return C

def KL(p, q):
	p = np.clip(p, 1e-6, 1-1e-6)
	q = np.clip(q, 1e-6, 1-1e-6)
	y = p*(np.log2(p)-np.log2(q))
	y += (1-p)*(np.log2(1-p)-np.log2(1-q))
	#y[np.isfinite(y)!=1] = 0
	return sum(y)
