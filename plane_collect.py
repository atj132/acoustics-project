''' Importing Dependencies '''
import dataCollector
from serv import servo
import time
import dataOrganizer as dO
from datetime import datetime
import wave_gen as wg
import model


print('Input position of Scanner in relation to speaker (x,y) in cm \n\tWhere y is the distance away from the microphone\n\tWhere x=0 is centered on microphone')


ypos = input('y? : ')
xpos = input('x? : ')
t_offset = -float(ypos)/(343*100)

''' Scanner Parameters '''
#Move servos across simple step pattern
x_incr = 5
x_start = 0
x = x_start
y_incr = 5
y_start = 0
y = y_start
x_end = 300
y_end = 300
#time waiting in seconds after move for average
wait_time = 4

small = input('small capture? (y/n): ')
ybound = float(input('enter bounds for y: '))

if small == 'y':
	x_incr = 2
	x_start = 145
	x = x_start
	y_incr = 2
	y_start = 145
	y = y_start
	x_end = 155
	y_end = 155

if small == 'k':

	x_incr = 60
	x_start = 0
	x = x_start
	y_incr = 60
	y_start = 0
	y = y_start
	x_end = 300
	y_end = 300

normal = input('Do what Max says (Y/N)')

if normal == 'y' or normal == 'Y':
	
	runs = 1
	freqList = [50000]
	cycleList = [50]
	phaseList = [0]
	periodList = [0.01]
	d = float(input('Choose distance for model in cm: '))
	modeldistlist = [d]

else:

#setting up lists for multiple runs
	runs = int(input('Enter the number of runs: '))
	freqList = []
	cycleList = []
	phaseList = []
	periodList = []
	modeldistlist=[]





#collecting settings for the wave generator
	for i in range(runs):
		freq = float(input('Enter frequency '+ str(i) + ' in hertz: '))
		cycle = int(input('Enter number of cycles '+ str(i) + ': '))
		phase = float(input('Enter phase '+ str(i) + ' in degrees: '))
		period = float(input('Enter period '+ str(i) + ' in sec: '))
		modeldist = float(input('Enter distance for model '+ str(i) + ' in centimeters: '))
		freqList.append(freq)
		cycleList.append(cycle)
		phaseList.append(phase)
		periodList.append(period)
		modeldistlist.append(modeldist)




	#Start up servo controllers
x_serv = servo('/dev/ttyUSB0',38400)
y_serv = servo('/dev/ttyUSB1',38400)

#for loop for multiple runs
for i in range(runs):
	''' Collecting run information for file management '''
	today = str(datetime.now())
	today = today.replace('-','_')
	today = today[5:]+'_'+today[2:4] # Keeping format the same as past data collections
	position = 'MicrophonePos(' + str(xpos) + '_' + str(ypos) + ')/'+today

	''' Initializing Hardware '''

	WV = wg.WV("/dev/usbtmc0",position)
	
	#connect to wave generator
	WV.wave(freqList[i],cycleList[i],phaseList[i],periodList[i])
	x_serv.mov(150)
	y_serv.mov(150)
	#Start up collector
	DC = dataCollector.DC("/dev/usbtmc1", today, position, wait_time,t_offset)

	WV.head_data()

	x_serv.mov(0)
	y_serv.mov(0)

	''' Running Scanner '''
	while x <= x_end:
		x_serv.mov(x)
		print('Scanning across x=%s'%(x))
		while y <= y_end:
			y_serv.mov(y)
		#Collect info after y movement and short wait
			time.sleep(wait_time)
			DC.collect(x, y,small,ybound)
			y += y_incr
		y = y_start
		y_serv.mov(y)
		x += x_incr
	x = x_start

	

	print('Done Scanning')

	#Do analysis
	print('Doing Analysis')
	org1=dO.Organizer('./Data/'+position+'/', date=today, new_session=True)
	org1.Organize_Collection()
	org1.save_data()
	org1.createFigs(showFigs=False)

#Turn off servos and send home
x_serv.end()
y_serv.end()

print('Data Collection Done')

print('Generating Model')

model.model(position,today,modeldistlist[0])

print('Model Generation Done')
