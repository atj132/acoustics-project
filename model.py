#program to generate hologram model
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import os




#main function
def model(position,date,d):
	
	#setting position to place final data
	direc = str(os.path.dirname(os.path.abspath(__file__)))
	
	#read data from generated csv file
	data = pd.read_csv(direc+'/Data/'+position+'/'+date+'fft_data.csv')
	
	#changing from pandas dataframe to array that can be worked with
	data_array = data.rename_axis('ID').values
	
	#caculating amplitude and phase data at a distance d
	amplitudes, phases = modela(data_array.T[0],data_array.T[1],data_array.T[2],data_array.T[3],d)

	#replacing dataframe values with new values
	data['Amp'] = amplitudes
	data['Phs'] = phases

	#creating matrix for graphing
	amp_matrix = pd.pivot_table(data,index='Y',columns='X',values='Amp')
	
	#defining file position for graph and create graph
	file_name = direc + '/Data/' + position +'/ampmodel.png'
	sns_plot = sns.heatmap(amp_matrix.astype(float))
	fig2 = sns_plot.get_figure()
	fig2.savefig(file_name, dpi = 1000)
	
	#saving data to new csv file
	csv_file = direc + '/Data/' + position +'/model.csv'
	data.to_csv(csv_file,index = None,header = True)

	print('done')
	
#function to calculate model
def modela(x,y,a,p,d):

	#constant values
	v = 343
	f = 50000
	lam = v/f
    
	#setting up arrays to take new values
	amp = np.zeros(len(a))
	phs = np.zeros(len(p))
	
	#iterate over each element of the amplitude matrix for each element of the new matrix
	for i in range(len(a)):
		for j in range(len(x)):

			#calculates distance in x-y plane
			dist = np.sqrt((x[i]-x[j])**2+(y[i]-y[j])**2)
			#adds 3rd z dimension to get r
			r = np.sqrt(dist**2 + d**2)
			#calculate complex amplitude modified with phase
			A = (a[j]/(20*r+1))*np.exp((p[j]+ (r/lam)*2*np.pi)*1j)
			#adds magnitude of complex amplitude and phase
			amp[i] += np.sqrt(A.real**2 + A.imag**2)
			phs[i] += p[j] + (r/lam)*2*np.pi
            
            
        
	#returns amp and phs arrays
	return amp,phs






