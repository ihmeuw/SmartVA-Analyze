import sys
#import pylab as pl
import numpy as pl
import matplotlib.mlab as mlab
import cPickle
import wx
import workerthread
import config

import my_randomforest as randomforest  # for easy development
reload(randomforest) # to get any new changes
num_features = 40
num_trees = 100
#suffixHCE = '' ##############

class Data:
	def __init__(self, notify_window, module='Adult', input_filename='/home/j/Project/VA/FinalAnalysis/Data/Models/%s/splitCustom.csv', available_filename='%s_available_symptoms.csv', HCE='HCE'):
		""" Load data from a va csv
		Parameters
		----------
		module : str, age group
		input_filename : str, the va file
		available_filename : str, contains mapping from the va input file to PHMRC variables used in training
		
		"""
	
		self.module=module
		self.cancelled = False
		
		if (HCE == 'HCE'):
			self.suffixHCE = ''
		else:
			self.suffixHCE = '_noHCE'
			
		#this file contains information about the cause list
		pkfile = open(config.basedir + "/pkl/"+'%s_causelist%s.pkl'%(self.module, self.suffixHCE), 'rb')
		self.cause_list = cPickle.load(pkfile)
		pkfile.close()
		
		#this file contains the list of symptoms used in PHMRC data
		pkfile = open(config.basedir + "/pkl/"+'%s_symptomlist%s.pkl'%(self.module, self.suffixHCE), 'rb')
		self.symptom_list = cPickle.load(pkfile)
		pkfile.close()		
		
		#print '%s module contains %d distinct causes of death' % (self.module, len(self.cause_list))
		#status.set('%s module contains %d distinct causes of death' % (self.module, len(self.cause_list)))
		#update('%s module contains %d distinct causes of death\n' % (self.module, len(self.cause_list)))
		updatestr = '%s module contains %d distinct causes of death\n' % (self.module, len(self.cause_list))
		wx.PostEvent(notify_window, workerthread.ResultEvent(updatestr))
		
		#print 'Label - Cause Name'
		#for i, cause in self.cause_list:
		#	print '%d - %s'%(i, cause)

		#this csv file is the mapping between input data fields and PHMRC fields, 0 means symptom is not avaialble
		symptomfile = config.basedir + "/pkl/"+available_filename
		self.symptom_list_available = mlab.csv2rec(symptomfile)
		
		#this csv file is the input va file, each row is one death
		fnameTest = input_filename
		#print "testing " + fnameTest
		#fnameTest = '/home/j/Project/VA/FinalAnalysis/Data/Models/%s/splitCustom.csv'
		#fnameTest = '/home/j/Project/VA/pyva/%suniformTrain.csv'
		#self.test = mlab.csv2rec(fnameTest % (self.module))
		updatestr = "Counting symptoms and deaths\n"
		wx.PostEvent(notify_window, workerthread.ResultEvent(updatestr))
		wx.PostEvent(notify_window, workerthread.ProgressEvent(None, None))
		self.test = mlab.csv2rec(fnameTest)

		
	def features(self, notify_window):
		""" reads data from the record, uses teh mapping of symptoms and construct an input matrix 
		Parameters
		----------
		
		"""
		X = pl.zeros([len(self.test), len(self.symptom_list)])
		try:
			for i, death in enumerate(self.test):
				num = 0
				for k, symptom in enumerate(self.symptom_list):
					#for each symptom in PHMRC symptom list, if it has a mapping in the data, we use it
					if (self.symptom_list_available[symptom][0] != 0 ):
						X[i, k] = death[self.symptom_list_available[symptom][0]]
						num = num + 1
					#otherwise we put zero
					else:
						X[i, k] = 0
		except:
			print '-----error occured in extracting input data.-----'
			#print 'number of mapped symptoms: %d'%sum([(i != 0) for i in self.symptom_list_available[0]])
			#print 'It seems there is something wrong with %s'%symptom
			#print 'Are you sure you have it in the input file? maybe you chose a wrong age module'
			#raise
		if (self.cancelled):
		    #wx.PostEvent(notify_window, workerthread.ResultEvent(None))
		    return
		#print 'your data has %d deaths and %d symptoms'%(len(X), num)
		updatestr = 'Your data has %d deaths and %d symptoms\n'%(len(X), num)
		wx.PostEvent(notify_window, workerthread.ResultEvent(updatestr))
		wx.PostEvent(notify_window, workerthread.ProgressEvent(20, 100))
		return X
		
	
	def calc_rf_scores(self, notify_window):
		""" Make random forest predictions for test data
		Parameters
		----------
		score_matrix : N x (J+1) array   ??
		"""
		#we use only highest tariff symptoms
		pkfile = open(config.basedir + "/pkl/"+'%s_tariff%s.pkl'%(self.module, self.suffixHCE), 'rb')
		tariff_matrix = cPickle.load(pkfile)
		pkfile.close()
		
		if (self.cancelled):
		    #wx.PostEvent(notify_window, workerthread.ResultEvent(None))
		    return
	
		abs_tariff = True
		if abs_tariff:
			self.symptom_list_for_cause = pl.argsort(-1 * pl.absolute(tariff_matrix), axis=0)  # argsort sorts lowest to highest
		else:
			self.symptom_list_for_cause = pl.argsort(-1 * tariff_matrix, axis=0)  # argsort sorts lowest to highest

		score_matrix = pl.zeros([len(self.test), len(self.cause_list)+1])
		
		tmp_symptom_list = self.symptom_list_for_cause[:num_features, :]
		features = self.features(notify_window)
		
		if (self.cancelled):
		    #wx.PostEvent(notify_window, workerthread.ResultEvent(None))
		    return
		
		#For processgin Neonate and Child, there is only one big rf model file that has to be read
		if (self.module != 'Adult'):
			#print 'please sit down and relax. we are reading the classifier file. This may take a few minutes ...'
			#status.set('please sit down and relax. we are reading the classifier file. this may take a few minutes ...')
			updatestr = 'Reading the classifier file. this may take a few minutes ...\n'
			wx.PostEvent(notify_window, workerthread.ResultEvent(updatestr))
			wx.PostEvent(notify_window, workerthread.ProgressEvent(None, None))
			
			pkfile = open(config.basedir + "/pkl/"+'%s_rf%s.pkl'%(self.module, self.suffixHCE), 'rb')
			self.rf = cPickle.load(pkfile)
			pkfile.close()
			wx.PostEvent(notify_window, workerthread.ProgressEvent(100, 100))
			if (self.cancelled):
			    #wx.PostEvent(notify_window, workerthread.ResultEvent(None))
			    return

			#print 'Processing input...'
			#status.set('Processing input...')
			updatestr = 'Processing input...\n'
			wx.PostEvent(notify_window, workerthread.ResultEvent(updatestr))
			
			total = len(features) * len(self.cause_list) * len(self.cause_list)
			current = 0
			for i in xrange(len(features)):
				for j1, cause1 in self.cause_list:
					for j2, cause2 in self.cause_list:
					    current = current + 1
					    wx.PostEvent(notify_window, workerthread.ProgressEvent(current, total))
					    if (self.cancelled):
					        #wx.PostEvent(notify_window, workerthread.ResultEvent(None))
					        return
					    if j1 < j2:
							X = features[i]
							X_i = X[pl.unique(tmp_symptom_list[:, [j1, j2]])]

							p, v = self.rf[(j1, j2)].apply(X_i, return_label=False)

							score_matrix[i, j2] += v
							score_matrix[i, j1] += num_trees-v
				if ((int)((float(i) / len(features))*100 ) % 10) == 0:
					#print '%d %%'% ((float(i) / len(features))*100)
					sys.stdout.flush()
					#status.set('%d %%'% ((float(i) / len(features))*100))
					updatestr = '%d %%\n'% ((float(i) / len(features))*100)
					#wx.PostEvent(notify_window, workerthread.ResultEvent(updatestr))
					#wx.PostEvent(notify_window, workerthread.ProgressEvent(float(i), len(features)))
					
			
		else:
			#for Adult module, ther are 46 rf file that we need to read. each one is read and used next, then scores are accumulated.
			#print 'reading the classifier file and processing the input. This may take a few minutes...'
			updatestr = 'please stay relaxed. we are reading the classifier file. this may take a few minutes (around 25 minutes)...\n'
			wx.PostEvent(notify_window, workerthread.ResultEvent(updatestr))
			
			total = len(self.cause_list) * len(self.cause_list)
			current = 0
			wx.PostEvent(notify_window, workerthread.ProgressEvent(0, 100))
			for j1, cause1 in self.cause_list:
				#print 'reading training file %d'%(j1-1)
				updatestr = 'reading training file ' + str(j1) + ' of ' + str(len(self.cause_list)) + '\n'
				wx.PostEvent(notify_window, workerthread.ResultEvent(updatestr))
				#wx.PostEvent(notify_window, workerthread.ProgressEvent(j1, len(self.cause_list)))
				pkfile = open(config.basedir + "/pkl/"+'train_%d%s.pkl'%((j1-1), self.suffixHCE), 'rb') #needs fix for HCE
				self.rf = cPickle.load(pkfile)
				pkfile.close()
				
				updatestr = 'Calculating for training file ' + str(j1)
				wx.PostEvent(notify_window, workerthread.ResultEvent(updatestr))
				
				for j2, cause2 in self.cause_list:
				    current = current + 1
				    wx.PostEvent(notify_window, workerthread.ProgressEvent(current, total))
				    if (self.cancelled):
				        #wx.PostEvent(notify_window, workerthread.ResultEvent(None))
				        return
				    if j1 < j2:
						for i in xrange(len(features)):
							X = features[i]
							X_i = X[pl.unique(tmp_symptom_list[:, [j1, j2]])]

							p, v = self.rf[(j1, j2)].apply(X_i, return_label=False)

							score_matrix[i, j2] += v
							score_matrix[i, j1] += num_trees-v
							
							# if ((int)((float(i) / len(features))*100 ) % 10) == 0:
								# print '%d %%'% ((float(i) / len(features))*100)
								# sys.stdout.flush()
				done = ((91. - j1)*j1/2.) / 1035.
				#status.set('please stay relaxed. we are reading the classifier file. this may take a few minutes (around 25 minutes). %f\%% done...'%done)
				#print '%f\%% done...'%done
		

		return score_matrix

	def max_rank_of_top_k_score_prediction(self, prediction_matrix, k=5):
		""" ranking using scores, not used in this version
		
		"""
		arg_max_score = pl.argsort(-1. * prediction_matrix, axis=1)

		# argsort is a confusing function; calling it twice replaces the values with their ranks
		# the -1 is because argsort always sorts lowest to highest
		ranked_score = pl.argsort(-1 * prediction_matrix, axis=0).argsort(axis=0)

		# the first column is just a place holder, so that the cause index
		# can start from 1; setting this to a lower value could implement
		# a way of predicting unknown, but it doesn't seem to give much
		# improvement (at least for tariff)
		ranked_score = pl.where(arg_max_score < k, ranked_score, 1. * len(ranked_score))

		return pl.argmin(ranked_score, axis=1)

	def max_rank_prediction(self, prediction_matrix):
		""" Rank deaths for each cause, and select highest ranked cause for	each death as the prediction, not used in this versions
		Parameters
		----------
		prediction_matrix : (deaths) x (causes + 1) array
			prediction_matrix[i, j] is a score for assigning cause j to death i

		Returns
		-------
		prediction : array
		"""
		# argsort is a confusing function; calling it twice replaces the values with their ranks
		# the -1 is because argsort always sorts lowest to highest
		ranked_score = pl.argsort(-1 * prediction_matrix, axis=0).argsort(axis=0)

		# the first column is just a place holder, so that the cause index
		# can start from 1; setting this to a lower value could implement
		# a way of predicting unknown, but it doesn't seem to give much
		# improvement (at least for tariff)
		ranked_score[:,0] = 1. * len(ranked_score)

		return pl.argmin(ranked_score, axis=1)
	
	def rank_against_train_prediction(self, prediction_matrix):
		""" ranks death comparing with the uniformly distributed training set scores (read from binary file)
		Parameters
		----------
		prediction_matrix: scores yield from calc_rf
		
		"""
		
		pkfile = open(config.basedir + "/pkl/"+'%s_uniformTrainScore%s.pkl'%(self.module, self.suffixHCE), 'rb')
		uniform_train_scores = cPickle.load(pkfile)
		pkfile.close()
		
		sorted_uniform_scores = -1. * pl.sort(-1.*uniform_train_scores, axis=0)
		
		self.ranks = pl.zeros([len(self.test), len(self.cause_list)+1])
		for j in range(1, len(self.cause_list)+1): #because cause 0 is nothing
			for i in range(len(prediction_matrix)):
				self.ranks[i, j] = self.rank(sorted_uniform_scores[:, j], prediction_matrix[i, j])
			
		
		return pl.argmin(self.ranks[:, 1:(len(self.cause_list)+1)], axis=1)+1
		
	def rank(self, sorted_score_array, score):
		""" finds rank of a number comapred to a sorted array of numbers (in log(n) time)
		Parameters
		----------
		sorted_score_array : float[], array of scores already sorted
		score : float
		"""
		
		min = 0
		max = len(sorted_score_array)-1
		while (max - min > 1):
			med = (max + min) / 2
			if (score > sorted_score_array[med]):
				max = med - 1
			else:
				min = med 
		if (score > sorted_score_array[max]):
			return max
		else:
			return min
		
	def save_scores(self, fname, prediction, score_matrix):
		""" Save results of prediction and also the input data to a file
		Parameters
		----------
		fname : str, the file name 
		prediction : int[], result of prediction
		score_matrix : float[][], rf scores matrix [num_deaths][num_causes]
		
		"""
		import os
		import csv

		f = open(fname, 'w')
		csv_f = csv.writer(f, lineterminator='\n')

		col_names = ['sid'] + ['cause%d'%i for i in 1+pl.arange(len(self.cause_list))] + ['est.cause']
		csv_f.writerow(col_names)

		score_list = []
		for i, row in enumerate(self.test):
			#score_list.append([row.sid] + list(score_matrix[i, 1:]) + [prediction[i]])
			score_list.append([row.sid] + list(self.ranks[i, 1:]) + [prediction[i]])
		csv_f.writerows(score_list)
		f.close()

		
	def calc_concordance(self, prediction):
		""" Calculate average concordance of predictions and self.test
		Parameters
		----------
		prediction : array

		Returns
		-------
		concordance : dict

		Example
		-------
		>>> data = Data('test_data.csv')
		data has 4 rows
		data contains 1 distinct causes of death
		data contains 2 dichotomous symptoms
		>>> data.test = data.death_list
		>>> concordance = data.calc_concordance(data.test.va46)
		mean concordance 100.00
		>>> concordance['cause1']
		1.0
		"""
		assert len(prediction) == len(self.test), 'Length of prediction array must match rows in self.test'

		# tally concordance by cause for these predictions
		concordance = {}
		for j, cause in self.cause_list:
			if (self.module == 'Adult'):
				deaths_for_cause_j = (self.test.va46 == j)
				concordance[cause] = pl.mean(prediction[deaths_for_cause_j] == \
											 self.test.va46[deaths_for_cause_j])
			if (self.module == 'Child'):
				deaths_for_cause_j = (self.test.va21 == j)
				concordance[cause] = pl.mean(prediction[deaths_for_cause_j] == \
											 self.test.va21[deaths_for_cause_j])
			if (self.module == 'Neonate'):
				deaths_for_cause_j = (self.test.va11 == j)	
				concordance[cause] = pl.mean(prediction[deaths_for_cause_j] == \
											 self.test.va11[deaths_for_cause_j])
			
			

		print 'mean concordance %.2f' % (pl.mean(concordance.values())*100)
		return concordance	
	
	def setCancelled(self):
	    self.cancelled = True;
		
if __name__ == '__main__':
	""" This main functio is for use if you want to call ths without using the GUI
	"""
	
	module='Neonate'
	
	#status='trainingscores' # set this if you want to save the scores in binary format (e.g. to update the training scores with new set of data)
	status='testing' # use this for normal use
	
	data = Data(module=module, input_filename='/home/j/Project/VA/FinalAnalysis/Data/Models/%s/splitCustom.csv'%module, available_filename = '%s_available_symptoms.csv'%module)
	
	score_matrix = data.calc_rf_scores()
	
	if (status == 'trainingscores'):
		outputScore = open(config.basedir + "/pkl/"+'%s_unifromTrainScore.pkl'%module, 'wb')
		cPickle.dump(score_matrix, outputScore, 2)
		outputScore.close()
	
	rank_against_train = True
	
	if rank_against_train:
		prediction = data.rank_against_train_prediction(score_matrix)
	else:
		prediction = data.max_rank_prediction(score_matrix)
	
	data.save_scores('/home/j/Project/VA/FinalAnalysis/Data/Models/%s/results.csv'%module, prediction, score_matrix)
	
	#concordance = data.calc_concordance(prediction)