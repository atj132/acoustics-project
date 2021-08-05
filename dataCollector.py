# Research
# 7/17/2018
# Class to collect data

import os
import numpy
import matplotlib.pyplot as plot
import time as ti

class DC:
	''' Class to collect data from oscilloscope, initialize with device path usually "/dev/usbtmc0" or "/dev/usbtmc1"'''
	def __init__(self, path, date, position, wait_time = 0,t_offset=0, points = 1000):
		self.File = os.open(path, os.O_RDWR)
		self.collect_count = 1
		self.date = date
		self.position = position
		self.wait_time = wait_time
		self.reference = 0
		self.offset = t_offset
		self.points = points
		self.timescale = 0
		self.timeoffset = 0
		self.voltscale = 0
		#self.start = 0
		#self.end = 0
		# Create folders to store data/images based on Date program was run
		self.position_path = 'Data/' + self.position + '/'
		os.makedirs(os.path.dirname(self.position_path), exist_ok=True)
		self.data_path = self.position_path + self.date + 'Data/'
		os.makedirs(os.path.dirname(self.data_path), exist_ok=True)
		self.img_path = self.position_path + self.date + 'Screenshot/'
		os.makedirs(os.path.dirname(self.img_path), exist_ok=True)
		# Create a file that holds some basic information about the oscilloscope
		self.headData()

		
	def write(self, command):
		os.write(self.File, command.encode())
	
	def read(self, length = 4000):
		return os.read(self.File, length)

	def init_axes(self):
		# Get Position of wave in internal memory
		self.write(":TRIG:POS?")
		#self.write(":WAV:XREF?")
		self.reference = int(self.read(20))

	def headData(self):
		#turn on channels and set auto scaling
		self.write(":CHAN1:DISP ON")
		self.write(":CHAN4:DISP ON")
		self.write(":AUT")
		self.write(":CHAN4:SCAL 1")
		self.write(":CHAN4:OFFS 0")
		self.write(":STOP") #used to take data in
		# dictionary used to hold information on oscilloscope setup

		ti.sleep(10)

		d = {}

		# collecting difference between 2 points in the x direction
		self.write(":WAV:MODE NORM")
		self.write(":WAV:SOUR CHAN4")
		self.write(":WAV:XINC?")
		x_inc = self.read(20)
		x_inc = x_inc.decode("utf-8").strip()
		d['XINC'] = x_inc

		# collecting difference between 2 points in the y direction
		self.write(":WAV:YINC?")
		y_inc = self.read(20)
		y_inc = y_inc.decode("utf-8").strip()
		d['YINC'] = y_inc

		# recording the time waited in seconds after move during averages
		d['WaitTime'] = self.wait_time	
	
		# Setting a reference point for internal memory
		self.init_axes()
		d['Reference'] = self.reference

		#whats the memory depth? (How many points can we collect?)
		self.write(":ACQ:MDEP?")
		val = self.read(20)
		d['MDEP'] = val.decode('utf-8').strip()

		#how many points are we collecting per read
		d['Collected_points'] = self.points

		# Get the timescale
		#self.write(":TIM:SCAL " + str(2.5*10**-5))
		self.write(":TIM:SCAL?")
		self.timescale = float(self.read(20))
		d['TScale']=self.timescale
		
		# Get the timescale offset
		#self.write(":TIM:DEL:OFF "+str(self.offset))
		self.write(":TIM:OFFS?")
		self.timeoffset = float(self.read(20))
		d['TOffset'] = self.timeoffset
		
		# Get the voltage scale
		self.write(":CHAN4:SCAL?")
		self.voltscale = float(self.read(20))
		d['VScale'] = self.voltscale
		
		# Get the Number of Averages
		self.write(":ACQ:AVER?")
		aver = self.read(20)
		d['Averages'] = aver.decode('utf-8').strip()
		
		# put scope back in run state
		self.write(":RUN")

		#trigger channel 4 off of channel 1
		self.write(":TRIG:MODE DEL")
		self.write(":TRIG:DEL:SA CHAN1")
		self.write(":TRIG:DEL:SB CHAN4")
		ti.sleep(0.1)
		self.write(":TRIG:DEL:SLOPB POS")
		
		#Write info to file
		filename = 'headData.txt'
		fullname = self.data_path + filename
		with open(fullname, 'w') as f:
			for key, value in d.items():
				f.write(str(key) + ': ' + str(value)+'\n')
			f.close()


	def collect(self, x, y,small,ybound):	
		# Stop data acquisition
		self.write(":STOP")
		 
		# Grab the data from channel 4
		self.write(":WAV:SOUR CHAN4")
		self.write(":WAV:MODE NORM")
		self.write(":WAV:FORM BYTE")
		
		chunks = []
		for i in range(1):
			start = self.reference #+self.timeoffset/self.timescale #- (1-i)*self.points + i*100
			end = start + self.points			
			#self.write("WAV:STAR {}".format(start))
			#self.write("WAV:STOP {}".format(end))
			self.write(":WAV:DATA?")
			rawdata = self.read(10*self.points+100)

			data_chunk = numpy.frombuffer(rawdata, 'B') 
			# First 12 points are garbage values
			data_chunk = data_chunk[1000:data_chunk.size-1]
			
			# subtract voltage by mean to center wave data on zero, then scale for voltage
			data_chunk = (data_chunk-data_chunk.mean())/(24*self.voltscale)
			chunks.append(data_chunk)
		
		#put all of our data chunks into one np array
		data = numpy.concatenate(chunks)

		# Now, generate a time axis
		# Create numpy array from 0th second to the last recorded second
		# Array increments by timescale (time between recorded data points)
		time = numpy.arange(0, int(data.size*self.timescale), self.timescale)
		while time.size < data.size:
			time = numpy.append(time, time.size*self.timescale)

		# Adding time offset to the time data 
		time = time #+ self.timeoffset

		# See if we should use a different time axis
		if (time[-1] < 1e-3):
				time = time * 1e6
				tUnit = "uS"
		elif (time[-1] < 1):
				time = time * 1e3
				tUnit = "mS"
		else:
				tUnit = "S"

		#Write data to file
		filename = 'point(%s_%s).txt'%(str(x),str(y))
		fullname = self.data_path + filename
		with open(fullname, 'w') as f:
			f.write('Time, Voltage\n')
			for instance in range(len(data)):
				f.write('%s, %s \n'%(str(time[instance]),str(data[instance])))
			f.close()
		 
		# Start data acquisition again, and put the scope back in local mode
		self.write(":RUN")
		self.write(":KEY:FORC")

		if(y%25 == 0 and x%25 == 0) or small == 'y' or small == 'k':
			# Plot the data
			plot.plot(time, data)
			plot.title("Oscilloscope Channel 4")
			plot.ylabel("Voltage (V)")
			plot.xlabel("Time (" + tUnit + ")")
			plot.ylim(ybound,-ybound)
			plot.xlim(time[0], time[len(time)-1])
			plot.savefig(self.img_path+'plot(%s_%s).png'%(str(x),str(y)))
			plot.clf()

