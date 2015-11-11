# This is the main file for growControl
print "Importing everything"
import sys
sys.path.append("C:\\Users\\Neil\\Documents\\GitHub\\Adafruit_Python_DHT")
sys.path.append("~/git/Adafruit/~/git/Adafruit_Python_DHT")
import Adafruit_DHT #import the AdaFruit libraries
import RPi.GPIO as GPIO #import the GPIO pins
import growControl as gc # Import the growControl module
from time import localtime, strftime, sleep


try:
	# This will read in the config file (eventually) 
	# Currently, it does some primitive error checking
	gc.readConfig(GPIO, "NORMALLY_CLOSED")

	# Hard code testing setup
	# remove for not testing
	curTime = float(strftime("%H%M",localtime()))
	lightDelay =2
	fanDelay = 3
	lightOnFor = 5
	fanOnFor = 3

	print "Start creating the devices"
	print "Create Lights"
	lights = []
	#lights.append(gc.light(0,27,curTime + lightDelay,curTime + lightDelay + lightOnFor,[0,1],[0,1]))
	print "Create Fans"
	fans = []
	#self,fanNumber,pin,fanOnType, onTime, offTime)
	fans.append(gc.fan(0,17,1,curTime + fanDelay,curTime + fanDelay + fanOnFor))
	#fans.append(gc.fan(1,27,2,curTime + fanDelay,curTime + fanDelay + fanOnFor))
	print "Create Temp Sensors"
	tempSensors = []
	tempSensors.append(gc.tempSensor(0,2,"DHT22",Adafruit_DHT))
	print "Create Control"
	# order is: gc.control(self,maxTemp,minTemp,relayType,recordInterval,fileLength,baseFileName):
	control = gc.control(30,15,"NORMALLY_CLOSED",1,5,"test_")
	
	#file name where everything is stored
	#outFileName = ("test1.csv")
	# end of hard code for setup



	print "Finished creating devices"

	print "Setting GPIO mode"
	#all pins are set using BCM mode
	GPIO.setmode(GPIO.BCM)

	#between inputDevices and setableDevices, everything that is going to be communicated with must be listed
	#create a list of all the sensors that are inputs, things that we can read from, sensors
	#these are things that we can monitor: temp, humidity,
	#something like a photo sensor would fall under here
	inputDevices = [tempSensors]

	#list of all the devices that are outputs
	#these are things that we can control like lights, fans pumps
	setableDevices = [fans,lights]

	print "Initializing"
	gc.initializeAllDevices(inputDevices+setableDevices,GPIO)
	#variable that kills everything
	on = 1
	#write the file headers
	gc.initFile(inputDevices+setableDevices,control)
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
	print ""
	print "-----------------------"
	print "User Initiated Quit"
	print "-----------------------"
	print ""
except:
	# If there are any errors, this should catch them
	print ""
	print "!!!!!--ERROR--!!!!!"
	print "There was some kind of error in the program!"
	print "!!!!!--ERROR--!!!!!"
	print ""
finally:
	# Reset GPIO settings
	GPIO.cleanup()