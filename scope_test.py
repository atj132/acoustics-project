import os

f = os.open("/dev/usbtmc1",os.O_RDWR)

def write(f, command):
		os.write(f, command.encode())

def read(f, length = 4000):
		return os.read(f, length)

write(f,":TIM:OFFS?")
timeoffset = float(read(f,20))

print(timeoffset)
