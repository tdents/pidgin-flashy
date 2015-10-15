#!/usr/bin/python
import os, threading,socket,sys,subprocess,signal
from subprocess import Popen,PIPE
from thread import *
from time import sleep
global status,devicepowerlevel,exitapp

def signal_handler(signal, frame):
	print 'SIGTERM'

signal.signal(signal.SIGTERM, signal_handler)

exitapp=False
HOST = '127.0.0.1'   # Symbolic name meaning all available interfaces
PORT = 8888 # Arbitrary non-privileged port
code = '44231'
dVendor = '09da'
dProduct = '0006'
#delay in seconds
#def: 100 ms
light = 0.1
delay = 0.1

status = False

#Search for usb device path in /sys/bus/usb/devices/
proc = subprocess.Popen(
	"ls /sys/bus/usb/devices/*/idVendor | xargs grep -rl " + dVendor + " | awk -F '/idVendor' '{ print $1\"/idProduct\" }' | xargs grep -rl " + dProduct + " | awk -F '/idProduct' '{ print $1 }'",
	shell=True,
	stdout=PIPE, stderr=PIPE
)
proc.wait()
res = proc.communicate()
if proc.returncode:
    print res[1]
devicesystempath = res[0]
devicesystempath = devicesystempath.replace('\n','')
devicepowerlevel = devicesystempath + '/power/level'
deviceautosuspedfile = devicesystempath + '/power/autosuspend_delay_ms'

file = open(deviceautosuspedfile, "w")
file.write("0")
file.close()


def on():
	file = open(devicepowerlevel, "w")
	file.write("on")
	file.close()

def off():
	file = open(devicepowerlevel, "w")
	file.write("auto")
	file.close()

def ledwhile():
		while not exitapp:
			if status == True:
				on()
				sleep(light)
				off()
				sleep(delay)
			sleep(0.1);

#t1 = threading.Thread(target=ledwhile)
#t1.start()

def changestate( state ):
	global status
	if isinstance(state, (int,float,long)):
		if state > 0:
			status = True
		if state == 0:
			status = False

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    s.bind((HOST, PORT))
except socket.error as msg:
    print 'Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
    exitapp = True
    sys.exit()
     
s.listen(10)

print 'Server is listening'
 
def clientthread(conn):
	while not exitapp:
			data = conn.recv(128)
			if not data: 
				break
			parameters = data.split(' ')
			if parameters[0] == code:
				changestate(int(parameters[1]))
				conn.close()
				break
			sleep(0.1)

t1 = threading.Thread(target=ledwhile)
t1.start()

while not exitapp:
	try:
		conn, addr = s.accept()

		start_new_thread(clientthread ,(conn,))
		sleep(0.1)
	except KeyboardInterrupt:
		exitapp = True
		raise

s.close()
