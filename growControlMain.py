# This is the main file for growControl

import sys
sys.path.append("C:\\Users\\Neil\\Documents\\GitHub\\Adafruit_Python_DHT")
sys.path.append("~/git/Adafruit/~/git/Adafruit_Python_DHT")
import Adafruit_DHT #import the AdaFruit libraries
import RPi.GPIO as GPIO #import the GPIO pins
import growControl as gc # Import the growControl module
from time import localtime, strftime, sleep


# remove for not testing
#initialize the setup
lights = []
#lights.append(gc.light(0,17,0700,1900,[0,1],[0,1]))

fans = []
#self,fanNumber,pin,fanOnType, onTime, offTime)
startTime = 2355
endTime = 0105
fans.append(gc.fan(0,3,1,2355,0005))
fans.append(gc.fan(1,4,1,2355,2358))#works
fans.append(gc.fan(2,5,1,0001,0002))
fans.append(gc.fan(3,6,1,2355,0005))
fans.append(gc.fan(4,7,1,2358,2355))
fans.append(gc.fan(5,8,1,0002,0001))
#fans.append(gc.fan(2,5,2,5,5)) # normal type 2 fan on 60s, off 60s
#fans.append(gc.fan(3,6,2,60,1)) # type 2 fan with normal on time, too low of off time
#fans.append(gc.fan(4,7,2,1,60)) # type 2 fan with too low on time, normal off time
#fans.append(gc.fan(5,8,2,1,1)) # type 2 fan with too low on time, too low off time
#fans.append(gc.fan(6,9,3,1,1)) # type 3 fan

#fans.append(gc.fan(1,22,2))

tempSensors = []
#tempSensors.append(gc.tempSensor(0,2,"DHT22",Adafruit_DHT))
#tempSensors.append(gc.tempSensor(1,6,"DHT22",Adafruit_DHT))

# max, min control
# order is: gc.control(self,maxTemp,minTemp,recordInterval):
control = gc.control(30,15,15)

#file name where everything is stored
outFileName = ("test1.csv")

# end of hard code for setup



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

gc.initializeAllDevices(inputDevices+setableDevices,GPIO)

#variable that kills everything
on = 1

#write the file headers
gc.initFile(inputDevices+setableDevices,outFileName)
while on:
	print ""
	print "----------------------------"
	print "--Starting Main Loop Again--"
	print "----------------------------"
	gc.readStatus(inputDevices)
	gc.deviceControl(setableDevices,control,gc.getDateTime(0,0,1),GPIO) #time in is epoch
	gc.writeStatus(inputDevices+setableDevices,outFileName,gc.getDateTime(1,1,0))
	sleep(control.recordInterval)
