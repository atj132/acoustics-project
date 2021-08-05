from serv import servo


#Start up servo controllers
x_serv = servo('/dev/ttyUSB0',38400)
y_serv = servo('/dev/ttyUSB1',38400)

print('Where do you want to move the microphone?')
flag = True
while flag:
	x = input('x: ')
	y = input('y: ')
	x_serv.mov(int(x))
	y_serv.mov(int(y))
	f2 = input('Do you want to move the microphone again? Y/N: ')
	if (f2.lower() == 'n'):
		flag = False

#Turn off servos and send home
print('Centering servos')
x_serv.end()
y_serv.end()
print('Done Scanning')
