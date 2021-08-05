from pipython.gcscommands import GCSCommands
from pipython.gcsmessages import GCSMessages
from pipython.interfaces.piserial import PISerial
import time

class servo:
	
	def __init__(self, my_port, my_baudrate):
		self.max_pos = ''
		self.min_pos = ''
		# Initialize message reader for servo
		gateway = PISerial(port=my_port, baudrate = my_baudrate)
		self.msg = GCSMessages(gateway)
		#start up servo
		self.start()

	def start(self):
		#Turn off servo if already on for some reason (resets servo)
		self.serv_pow('0')
		#Turn on servo
		self.serv_pow('1')
		#Move servo home (initializes the axis)
		self.msg.send('FNL 1')
		self.waitonmove()
		#Log max and min positions
		self.max_pos = self.msg.read('TMX? 1').strip().split('=')[1]
		self.min_pos = self.msg.read('TMN? 1').strip().split('=')[1]

	def waitonmove(self):
		# Sleeps the program until servo is done moving
		rdy = self.msg.read(chr(5))
		while int(rdy) > 0:
			time.sleep(.75)
			rdy = self.msg.read(chr(5))

	def serv_pow(self, switch):
		#z = self.msg.read('SAI?')
		#print(z)
	# Just a method to make changing the power state easier
		self.msg.send('SVO 1 %s'%(switch))
		#servo_state = self.msg.read('SVO? 1').strip().split('=')[1]
		#print('Servo state = ', servo_state)
	
	def mov(self, pos):
	# Method to move server and check for boundary conditions
		if pos <= int(float(self.max_pos)) and pos >= int(float(self.min_pos)):
			self.msg.send('MOV 1 %s'%(pos))
			self.waitonmove()
		else:
			print('move position out of bounds')
		
	def end(self):
		#Final Positions
		print('Sending servo to center of axis')
		self.mov(0)
		self.waitonmove()
		#Turn off servos
		self.serv_pow('0')
		print('Servo turned off')
