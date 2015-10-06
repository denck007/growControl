# This is the main file for growControl

import sys
sys.path.append("C:\\Users\\Neil\\Documents\\GitHub\\Adafruit_Python_DHT")
import Adafruit_DHT
import growControl as gc
from time import localtime, strftime

# hard code this for now
#initialize the setup
lights = []
lights.append(gc.light(0,17,0700,1900,[0,1],[0,1]))

fans = []
fans.append(gc.fan(0,27,1))
fans.append(gc.fan(1,22,2))



tempSensors = []
tempSensors.append(gc.tempSensor(0,5,"DHT22"))
tempSensors.append(gc.tempSensor(1,6,"DHT22"))



control = gc.control(30,15,2)

# end of hard code for setup


#file name where everything is stored
outFileName = ("test1.csv")


#between inputDevices and setableDevices, everything that is going to be communicated with must be listed
#create a list of all the sensors that are inputs, things that we can read from, sensors
#these are things that we can monitor: temp, humidity,
#something like a photo sensor would fall under here
inputDevices = [tempSensors]

#list of all the devices that are outputs
#these are things that we can control like lights, fans pumps
setableDevices = [fans,lights]

#variable that kills everything
on = 1

	

#write the file headers
gc.initFile(inputDevices+setableDevices,outFileName)
while on:
	localTime = strftime("%Y",localtime())+ "-" +strftime("%m",localtime())+ "-" +strftime("%d",localtime())+ "-" + strftime("%H",localtime())+strftime("%M",localtime())
	gc.readStatus(inputDevices)
	gc.deviceControl(setableDevices)
	gc.writeStatus(inputDevices+setableDevices,outFileName)
	time.sleep(control.recordInterval)
