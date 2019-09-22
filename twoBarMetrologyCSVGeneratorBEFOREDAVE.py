import sys
import csv
import time
import dial_indicator
from Phidget22.Devices.Encoder import *
from Phidget22.PhidgetException import *
from Phidget22.Phidget import *
from Phidget22.Net import *
# import twoBarMetrologyCollection

tick_per_rev = 4096
mm_per_rev = 3.175
samplerate_hz = float(3)
sampletime_s = 0
dataInterval_ms = 25

try:
    ch = Encoder()
except RuntimeError as e:
    print "Runtime Exception %s" % e.details
    print "Press Enter to Exit...\n"
    readin = sys.stdin.read(1)
    exit(1)

def EncoderAttached(self):
    try:
        attached = self
        '''
        print "\nAttach Event Detected (Information Below)"
        print "==========================================="
        print "Library Version: %s" % attached.getLibraryVersion()
        print "Serial Number: %d" % attached.getDeviceSerialNumber()
        print "Channel: %d" % attached.getChannel()
        print "Channel Class: %s" % attached.getChannelClass()
        print "Channel Name: %s" % attached.getChannelName()
        print "Device ID: %d" % attached.getDeviceID()
        print "Device Version: %d" % attached.getDeviceVersion()
        print "Device Name: %s" % attached.getDeviceName()
        print "Device Class: %d" % attached.getDeviceClass()
        print "\n"
        '''

    except PhidgetException as e:
        print "Phidget Exception %i: %s" % (e.code, e.details)
        print "Press Enter to Exit...\n"
        readin = sys.stdin.read(1)
        exit(1)   
    
def EncoderDetached(self):
    detached = self
    try:
        print "\nDetach event on Port %d Channel %d" % (detached.getHubPort(), detached.getChannel())
    except PhidgetException as e:
        print "Phidget Exception %i: %s" % (e.code, e.details)
        print "Press Enter to Exit...\n"
        readin = sys.stdin.read(1)
        exit(1)   

def initEncoder(channel):
	try:
	    ch0 = Encoder()
	except RuntimeError as e:
	    print "Runtime Exception %s" % e.details
	    print "Press Enter to Exit...\n"
	    readin = sys.stdin.read(1)
	    exit(1)

	#Initialize Phidgetboard encoder
	try:
	    ch0.setOnAttachHandler(EncoderAttached)
	    ch0.setOnDetachHandler(EncoderDetached)
	    ch0.setOnErrorHandler(ErrorEvent)
	    ch0.setChannel(channel)

	    print "Waiting for the Phidget Encoder Object to be attached..."
	    ch0.openWaitForAttachment(5000)
	except PhidgetException as e:
	    print "Phidget Exception %i: %s" % (e.code, e.details)
	    print "Press Enter to Exit...\n"
	    readin = sys.stdin.read(1)
	    exit(1)
	if(not ch0.getEnabled()):
	    ch0.setEnabled(1)
	ch0.setDataInterval(dataInterval_ms)
	return ch0

def ErrorEvent(self, eCode, description):
    print "Error %i : %s" % (eCode, description)

def main():
	global samplerate_hz
	global sampletime_s
	#Initialize Digital dial indicator
	#Plug indicator into port 'W'
	d = dial_indicator.DialIndicatorBoard()
	d.set_leds([0,0,0]*4) #sets LEDs OFF

	#Initialize Phidgetboard encoder
	e0 = initEncoder(0)
	e1 = initEncoder(1)

	# Open CSV file and initialize
	timestamp = time.strftime("%Y_%m_%d_%H%M", time.localtime(time.time()))
	# filename = 'Data_{}.csv'.format(timestamp)
	filename = 'Sample1.txt'
	csvfile = open(filename, "w+") 
	csvfile.write('time, e0, e1, deflection\n')
	# twoBarMetrologyCollection.startPlot()

	# Main data collection loop
	if sampletime_s == 0:
		sampletime_s = 1000000

	#d.zero()
	stime = time.time()
	etime = stime + sampletime_s
	inc_time = float(1 / samplerate_hz)
	settime = stime + inc_time
	layer = 0
	color = 0
	x_homed = 0
	xlast = 0
	xpos = 0
	index = 0
	returning = 0
	missCount = 0
	ticker = 0
	while time.time() < etime:
		#Get current xposition
		ticks0 = e0.getPosition()
		ticks1 = e1.getPosition()

		#Get deflection
		deflect = d.get_readings()[3]

		#Save data to csv file
		print 'time: {}, e0: {}, e1: {} deflection: {}'.format(time.time(), ticks0, ticks1, deflect)
		csvfile.write('{},{},{},{}\n'.format(time.time() - stime, ticks0, ticks1, deflect))
		csvfile.flush()

                fields=[0,ticks0,ticks1,deflect]
                with open(r'csvfile', 'a') as f:
                    writer = csv.writer(f)
                    writer.writerow(fields)
        	#csvfile.close()
        	#csvfile = open(filename, "w")
        	
		# Wait for next update and keep track of timing misses. 
		missCount += 1
		while time.time() < settime:
			missCount = 0
		if missCount > 2:
			settime += inc_time
			print "TIMING MISS: CONSIDER LOWER SAMPLE RATE"

		#Update next time setpoint
		settime += inc_time

	csvfile.close()
	try:
	    ch.close()
	except PhidgetException as e:
	    print "Phidget Exception %i: %s" % (e.code, e.details)
	    print "Press Enter to Exit...\n"
	    readin = sys.stdin.read(1)
	    exit(1) 
	print "Closed Encoder device"

if __name__ == '__main__':
	main()
	exit(0)
