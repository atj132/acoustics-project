# Loads data into a dataframe for quicker replotting purposes
# Also performs fft on new data
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from scipy.fftpack import fft
from os import listdir
from os.path import isfile, join


class Organizer:
    def __init__(self, path, date, new_session = False):
        self.path = path
        self.date = date
        if new_session:
            self.dFrame = pd.DataFrame(columns = ['X','Y','Amp','Phs','Complex'])
            self.dFrame = self.dFrame.astype(dtype={'X':'int64','Y':'int64','Amp':'float64','Phs':'float64','Complex':'object'} )
        else:
            self.dFrame = pd.read_csv(self.path+"fft_data.csv")

    def horizontal(self, y):
        return self.dFrame.loc[self.dFrame['Y'] == y]

    def vertical(self, x):
        return self.dFrame.loc[self.dFrame['X'] == x]

    def myData(self):
        return self.dFrame

    def save_data(self):
        # self.dFrame = self.dFrame.astype({'X': int, 'Y': int, 'Amp': float, 'Phs': float, 'Complex': str})
        self.dFrame.to_csv(self.path+self.date+"fft_data.csv", index=False)

    def append_data(self, x, y, dt, volts, freq = 50000):
        # Getting complex value of the voltage data at point (x,y)
        bin_value = self.dataFFT(dt, volts, freq)
        phs = np.angle(bin_value) # Angle of complex value
        amp = np.abs(bin_value) # Amplitude of real voltage at freq bin

        # Appending data to dataframe
        self.dFrame.loc[len(self.dFrame)] = [int(x), int(y), float(amp), float(phs), str(bin_value)]

    def dataFFT(self, dt, volts, freq = 50000):
        N = np.size(volts)
        SR = 1/dt # Sampling Rate
        Fmax = SR/2 # Max Frequency
        SL = N/2 # Spectral Lines (Number of bins)
        dF = Fmax/SL # Frequency Resolution (bin width in Hz)

        signalFFT = fft(volts)
        bin = int(freq//dF)+1
        return signalFFT[bin]

    def createFigs(self, showFigs = False):
        plt.style.use('ggplot')

        amp_matrix = pd.pivot_table(self.dFrame, index='Y',columns='X',values='Amp')
        phs_matrix = pd.pivot_table(self.dFrame, index='Y',columns='X',values='Phs')

        # Looking at just the data across the horizontal where Y = 150
        y_150 = self.horizontal(150)

        y_150 = y_150.sort_values('X')

        fig1 = plt.figure()
        ax1 = fig1.add_subplot(1,2,1)
        ax2 = fig1.add_subplot(1,2,2)
        ax1.plot(y_150['X'].astype(float), y_150['Amp'].astype(float))
        ax2.plot(y_150['X'].astype(float), y_150['Phs'].astype(float))
        ax1.invert_xaxis()
        ax2.invert_xaxis()
        ax1.set_title('Amplitude across Horizontal')
        ax2.set_title('Phase across Horizontal')
        fig1.savefig(self.path+"("+self.date+")y_150Scan.png")

        fig2 = plt.figure()
        sns_plot = sns.heatmap(amp_matrix.astype(float), cmap='viridis')
        sns_plot.invert_yaxis()
        sns_plot.invert_xaxis()
        sns_plot.set_title('Amplitude Across Plane')
        fig2 = sns_plot.get_figure()
        fig2.savefig(self.path+"("+self.date+")PlaneAmplitude.png")

        if showFigs:
            plt.show()

    def Organize_Collection(self):
        collection_path = self.path+'/'+self.date+'Data'
        onlyfiles = [f for f in listdir(collection_path) if isfile(join(collection_path, f))]
        onlyfiles.remove('headData.txt')
        # Getting data timestep from headData.txt
        with open(collection_path+"/headData.txt","r") as f:
        	lines = f.readlines()
        head_dict = {}
        for line in lines:
        	split = line.split(':')
        	head_dict[split[0].strip()] = split[1].strip()
        dt = float(head_dict['XINC'])

        counter = 1

        for f in onlyfiles:
            coords = f.replace('(', ' ').replace(')',' ').split(' ')[1].split('_')
            x = int(coords[0])
            y = int(coords[1])

            fpath = collection_path + "/" + f
            with open(fpath, "r") as f:
                head = f.readline()
                data = f.readlines()

            N = np.size(data)
            volt = np.zeros(N)
            for i in range(N):
                data[i] = data[i].strip()
                vals = data[i].split(',')
                volt[i] = float(vals[1])

            if len(onlyfiles) % 10 == 0:
                print("Appending Data Progress {}% complete".format(counter*10))
                counter += 1
            self.append_data(x, y, dt, volt)
