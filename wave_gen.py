#program to communicate with wave generator
import os
import time


class WV:

	def __init__(self,path,position):

		self.File = os.open(path,os.O_RDWR)
		self.position = position
		

#function to write to wave generator
	def w(self,command):
    		print (command)
    		os.write(self.File,command.encode())
    		time.sleep(0.2)

#function that generates wave based on specifications
	def wave(self,freq,cycle,phase,period):

		self.prop_list = [freq,cycle,phase,period]
	
	#all specifications to create wave
		self.w("FUNC sin")
		self.w("FREQ %d" % freq)
		self.w("BURS:STAT ON")
		self.w("BURS:NCYC %d" % cycle)
		self.w("BURS:PHASE %d" % phase)
		self.w("BURS:INT:PER "+  str(period))
		self.w("OUTP ON")
	
	#location for recording inputed wave data

	def head_data(self):
		direc = str(os.path.dirname(os.path.abspath(__file__)))
		fullname = direc + '/Data/' + self.position + '/WaveSpecs.txt'

	#writing data to file
		with open(fullname, "w+") as f:
			f.write('Frequency(Hz): '+ str(self.prop_list[0])+'\n')
			f.write('Cycles: '+ str(self.prop_list[1])+'\n')
			f.write('Phase(deg): '+ str(self.prop_list[2])+'\n')
			f.write('period(sec): '+ str(self.prop_list[3]))
			f.close()

