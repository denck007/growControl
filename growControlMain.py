# This is the main file for growControl
print "Importing everything"
import sys
import RPi.GPIO as GPIO #import the GPIO pins
import growControl as gc # Import the growControl module
from time import localtime, strftime, sleep


try:
	#import sys
	#sys.path.append("C:\\Users\\Neil\\Documents\\GitHub\\Adafruit_Python_DHT")
	#sys.path.append("~/git/Adafruit/~/git/Adafruit_Python_DHT")
	#import Adafruit_DHT #import the AdaFruit libraries
	# This will read in the config file (eventually) 
	# Currently, it does some primitive error checking
	inputDevices,setableDevices= gc.readConfig(GPIO, "NORMALLY_CLOSED")

	#lights.append(gc.light(0,27,curTime + lightDelay,curTime + lightDelay + lightOnFor,[0,1],[0,1]))

	#self,fanNumber,pin,fanOnType, onTime, offTime)
	#fans.append(gc.fan(0,17,1,curTime + fanDelay,curTime + fanDelay + fanOnFor))
	#fans.append(gc.fan(1,27,2,curTime + fanDelay,curTime + fanDelay + fanOnFor))

	print "Create Control"
	# order is: gc.control(self,maxTemp,minTemp,relayType,recordInterval,fileLength,baseFileName):
	control = gc.control(30,15,"NORMALLY_CLOSED",1,5,"test_")

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
		control.check() # needs the devices so it can recreate the headers for the file names
		print "Reading Status"
		gc.readStatus(inputDevices)
		print "Running deviceControl"
		gc.deviceControl(setableDevices,control,gc.getDateTime(0,0,1,0),GPIO) #time in is epoch
		print "Running writeStatus"
		gc.writeStatus(inputDevices+setableDevices,control.fileName,gc.getDateTime(1,1,0,0))
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