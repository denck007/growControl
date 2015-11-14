# This is the main file for growControl

import sys
import RPi.GPIO as GPIO #import the GPIO pins
import growControl as gc # Import the growControl module

from time import localtime, strftime, sleep


try:
	inputDevices, setableDevices, control = gc.readConfig.readConfig(GPIO)

	print "Setting GPIO mode"
	#all pins are set using BCM mode
	GPIO.setmode(GPIO.BCM)

	print "Initializing All Devices..."
	gc.initializeAllDevices(inputDevices+setableDevices,GPIO)

	#write the file headers
	gc.initFile(inputDevices+setableDevices,control)

	#variable that kills everything
	on = 1

	print "Starting the main control loop"
	while on:
		print ""
		print "-----------------------"
		print "--Starting Main Loop --"
		print "-----------------------"
		control.check(gc.getDateTime(0,0,0,1)) # needs the devices so it can recreate the headers for the file names
		print "Reading Status"
		gc.readStatus(inputDevices)
		print "Running deviceControl"
		gc.deviceControl(setableDevices,control, gc.getDateTime(0,0,1,0),GPIO) #time in is epoch
		print "Running writeStatus"
		gc.writeStatus(inputDevices+setableDevices,control.fileName, gc.getDateTime(1,1,0,0))
		print "Going to sleep"
		sleep(control.recordInterval)
			
except KeyboardInterrupt:
	# allow the user to end program with CTRL+C
	gc.errorDisplay("User Initiated Quit")
except:
	# If there are any errors, this should catch them
	gc.errorDisplay("Unhandeled Exception: " + str(sys.exc_info()[0]))
finally:
	# Reset GPIO settings
	GPIO.cleanup()