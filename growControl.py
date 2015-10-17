#this file defines the objects and functions for the grow control program
def readConfig(GPIO, relayType):
# This will eventually be the function that reads in the configuration file and does all of the initial validation
# Until then, this function will have kind of random things happening in it
# This function will eventually only need to be passed the GPIO module and the config file name
	
	# Check the relay type, allows support for normally open and normally closed relays
	# The intention here is to make the device methods easier to understand
	#		by not having things turn on when set to low
	global RELAYON
	global RELAYOFF
	if relayType == "NORMALLY_OPEN":
		# The relays are normally open, the attached device is not receiving power when the input pin is set to 0V
		RELAYON = GPIO.HIGH
		RELAYOFF = GPIO.LOW
	elif relayType == "NORMALLY_CLOSED":
		# The relays are normally closed, the attached device is receiving power when the input pin is set to 0V
		RELAYON = GPIO.LOW
		RELAYOFF = GPIO.HIGH
	else: 
		print "!!!!!--ERROR--!!!!!"
		print "The relay type is not defined properly"
		print "!!!!!--ERROR--!!!!!"
		RELAYON = "ERROR"
		RELAYOFF = "ERROR"
		
		
		
def readStatus(devices):
#read the status of the devices
#devices must have the self.update() method
	for deviceGrp in range(len(devices)):
		#print "readStatus - deviceGrp: " + str(deviceGrp)
		for device in range(len(devices[deviceGrp])):
			#print "readStatus - device: " + str(device)
			devices[deviceGrp][device].update()
		
def deviceControl(devices,control,theTime,GPIO):
	for deviceGrp in range(len(devices)):
		#print "deviceControl - deviceGrp: " + str(deviceGrp)
		for device in range(len(devices[deviceGrp])):
			#print "deviceControl - device: " + str(device)
			devices[deviceGrp][device].control(devices,control,GPIO)
		
def writeStatus(devices,fileName,theDateTime):
# this function goes over all the devices and writes their status to the output file.
# expects a list of lists of devices, each device must have the method returnStatusString()
	statusOut = theDateTime + "," #start each line with the date/time
	for deviceGrp in range(len(devices)): #loop over each device group
		for device in range(len(devices[deviceGrp])): # loop over each device in the group
			#print "writeStatus - deviceGrp: " + str(deviceGrp) + "  device: " + str(device) #debug
			#print str(devices[deviceGrp][device].growType)
			statusOut=statusOut + devices[deviceGrp][device].returnStatusString() + "," # add the status to the string
	
	
	outFile = open(fileName,"a") #open the file for appending
	outFile.write(statusOut + "\n") #append the file with the data
	outFile.close() #close the file
		
def initFile(devices,fileName):
# This function reads in the headers defined in the object definition for the column headers
# writes device.reportItemHeaders() to the given file
	headersOut = "Date and Time (YYYY-MM-DD-HH:MM:SS):,"
	for deviceGrp in range(len(devices)): #loop over each device group
		for device in range(len(devices[deviceGrp])): # loop over each device in the group
			headersOut=headersOut + devices[deviceGrp][device].reportItemHeaders + "," # add the status to the string
	
	
	outFile = open(fileName,"a") #open the file for appending
	outFile.write(headersOut + "\n") #append the file with the data
	outFile.close() #close the file

def initializeAllDevices(devices,GPIO):
# call the initGPIO on all the devices
	curEpochTime = getDateTime(0,0,1)
	for deviceGrp in range(len(devices)): #loop over each device group
		for device in range(len(devices[deviceGrp])): # loop over each device in the group
			devices[deviceGrp][device].initGPIO(GPIO,curEpochTime)
	
def getDateTime(d,t,s):
	#returns the date and or time
	# if date ==1 return the date
	# if time ==1 return the time 
	# if both return both in YYYY-MM-DD-HH:MM:SS format
	# if only s return epoch time
	from time import localtime, strftime, time

	if (d == 1 or t == 1) and not s: #cases for returning strings
		date = strftime("%Y",localtime())+ "-" +strftime("%m",localtime())+ "-" +strftime("%d",localtime())
		time = strftime("%H",localtime())+":"+strftime("%M",localtime())+":"+strftime("%S",localtime())
		if d>1 or d<0 or t>1 or t<0:
			print "!!!!!--ERROR--!!!!!"
			print "Error in passing time values: Value out of input range"
			print "!!!!!--ERROR--!!!!!"
		if d and t:
			return date + "-" + time
		elif d and not t:
			return date	
		elif t and not d:
			return time
		else:
			return "Something unexpected happened in getting the time"
	elif s: # get epoch time
		return time()
	else:
		print "!!!!!--ERROR--!!!!!"
		print "No values requested from getDateTime()"
		print "!!!!!--ERROR--!!!!!"

def  getMinuteDiff(timeToCompare):
	# returns the minute difference in the time from current time to timeToCompare()
	# 	EX: current local time is 1704, timeToCompare is 0605, returns 1099
	
	from time import strftime,localtime
	
	curTime = float(strftime("%H%M",localtime()))
	#print "Time to Compare: " + str(timeToCompare) #debugging
	#print "Current epoch Time: " + str(curTime) #debugging
	#print "Difference is: " + str(curTime - timeToCompare) #debugging
	return curTime - float(timeToCompare)
	
	
##########	
#Class Definitions
##########	
# Generic Class Notes:


########################
# IMPORTANT: ANYTHING ATTACHED TO A RELAY MUST NOT BE ATTACHED TO GPIO2-4 (PINS 3,5,7)
#			GPIO 2&3 have pull up resistors which make them want to flip between on and off (because they are I2C)
#			GPIO 4 has something else wrong with it, not sure what, but is causes the same problem
########################


## ids
### should be in order with no id being used twice.
#
## returnStatusString()
### must return a string
### data format must match self.reportItemHeaders for csv file to make any sense
### if more that 2 data points are to be returned, then they must be separated by a comma
### do not include a comma at the start or end of the string
### data validation should be done here
#
# all device classes must have:
## __init__(this varies between classes) - All the initialized values
## initGPIO(GPIO module, current time in epoch seconds) #call to initialize GPIO on the device
## returnStatusString() # returns the status of the device
#
# all Controlable devices need to have:
## control(list of all the devices, the control object, the GPIO module) # runs the device's control methods
#
# all readable devices must have:
## update() # reads the device status



class light:
	def __init__(self,lightNumber,pin,timeOn,timeOff,fans,tempS):
		##########
		#configurable values
		##########
		self.id = lightNumber #number of the light, index starts at 0
		self.pin = pin #GPIO pin used
		self.timeOn = timeOn #time the light comes on, ex: 0705 for 7:05am; 1934 for 7:34 pm
		self.timeOff = timeOff #time the light turns off
		
		# this links what fans and temp sensors belong to what lights
		# is a list of what fans/temp sensors are associated with this self.light
		# ex: self.fans = [0,1,2,4] means that self.light is associated with fans with ids 0,1,2, and 4
		self.fans = fans
		self.tempS = tempS
		
		
		
		##########
		#hard coded but configurable in source code
		##########
		# this is what the output file headers will display (using csv format)
		# this line must not end in a comma.  
		# If multiple columns are to be reported, then each one must be separated by a comma
		# Headers must match the order the reporting string is built in self.returnStatusString()
		self.reportItemHeaders = "Light:" + str(self.id) + "  On Pin:" + str(self.pin)
		
		##########
		#hard coded and should not be messed with
		##########
		self.status = RELAYOFF # Lights should only turn on after initialization
		self.growType = "light"
			
	def returnStatusString(self):
		if self.status == RELAYON:
			return "On"
		else:
			return "Off"
		
	def control(self, devices, control, GPIO):
		#this is written such that GPIO.HIGH is light on

		testOn = getMinuteDiff(self.timeOn)
		testOff = getMinuteDiff(self.timeOff)
		print ""
		print "Light " + str(self.id) + " testOn = " + str(testOn)
		print "Light " + str(self.id) + " testOff = " + str(testOn)
		
		if testOn >= 0 and testOff < 0:
			# time in the off times, set light off
			self.status = RELAYON
			print "STATUS CHANGE				Light " + str(self.id) + " is on"
		else:
			# if the light is not between the off times, it should be on
			self.status = RELAYOFF
			print "STATUS CHANGE				Light " + str(self.id) + " is off"
		
		
		# this should always be the last thing to run in the control method
		# it checks if any of the temperature sensors are exceeding the limit set in control and if so, sets light to low
		# by being the last check in the control method, it insures a high temp will cause light on
		for dg in devices:
			for d in dg:
				if d.growType == "tempSensor":
					if d.lastTemp >control.MaxTemp:
						self.status = RELAYOFF
						print "!!!!!--ERROR--!!!!!"
						print "-- Light " + str(self.id) + " status changed because of high reading on Temp Sensor " + str(d.id)
						print "!!!!!--ERROR--!!!!!"
						
		GPIO.output(self.pin, self.status) #finally set the light value
	
	def initGPIO(self, GPIO, curEpochTime):
		GPIO.setup(self.pin,GPIO.OUT) #initialize the pin as out
		GPIO.output(self.pin,self.status) # initialize the light to default value, should be off
		
		self.lastOn = curEpochTime #set the first on time light was turned on to now
		self.lastOff = curEpochTime # set the last time the light was turned off to now	
		
		
		
		
		
		
		
		
		
class fan:
#definition of a fan
	def __init__(self,fanNumber, pin, fanOnType,onTime, offTime):
		##########
		#configurable values
		##########
		self.id = fanNumber #number of the fan, index starts at 0
		self.pin = pin #GPIO pin used
		self.fanOnType = fanOnType # 1 = fan on between certain times in the day, 2=on for specified time, off for specified time, 3 = Always on
		self.fanOnAt = float(onTime) # the time the fan will turn on if fanOnType=1, duration fan on for if fanOnType=2
		self.fanOffAt = float(offTime) #time the fan turns off if fanOnType=1, duration fan off for if fanType=2
			# fanOffAt > fanOnAt, otherwise it will not work properly
		
		##########
		#hard coded but configurable in source code
		##########
		self.reportItemHeaders = "Fan:" + str(self.id) + "  On Pin:" + str(self.pin)
				
		##########
		#hard coded and should not be messed with
		##########
		self.status = RELAYON # init to on
		self.growType = "fan"
		
		##########
		#Program set values
		##########		
		curTime = getDateTime(0,0,1)
		self.lastOn = curTime # epoch, last time the fan was turned on
		self.lastOff = 0  #epoch, last time the fan was turned off
		
	def initGPIO(self, GPIO, curEpochTime):
		GPIO.setup(self.pin,GPIO.OUT) #initialize the pin as out
		GPIO.output(self.pin,self.status) # initialize the fans to on
		
		self.lastOn = curEpochTime #set the first on time fan was turned on to now
		self.lastOff = curEpochTime # set the last time the fan was turned off to now
		
	def control(self, devices, control, GPIO):
		#this is written such that GPIO.HIGH is fan on
			
		#run checks to see what type of fan and what controls to use, then actually control it
		if self.fanOnType == 1:
			#print "fanOnType == 1"
			testOn = getMinuteDiff(self.fanOnAt)
			testOff = getMinuteDiff(self.fanOffAt)
			print ""
			print "Fan " + str(self.id) + " testOn = " + str(testOn)
			print "Fan " + str(self.id) + " testOff = " + str(testOn)

			if testOn >= 0 and testOff < 0:
				# time in the off times, set fan off
				self.status = RELAYON
				print "STATUS CHANGE				Fan " + str(self.id) + " is on"
			else:
				# if the fan is not between the off times, it should be on
				self.status = RELAYOFF
				print "STATUS CHANGE				Fan " + str(self.id) + " is off"
			
		elif self.fanOnType ==2:
			# this type runs for fanOnAt minutes, then turns off for fanOffAt minutes
			print "fanOnType == 2 is not yet supported, please change the type of fan #" + str(self.id)
		elif self.fanOnType ==3:
			# this type is always on
			print "fanOnType == 3"				
			self.status = RELAYON
		
		else:
			print "fanOnType not defined or not recognized, setting to always on"
			self.status = RELAYON
		
		#this should always be the last thing to run in the control method
		# it checks if any of the temperature sensors are exceeding the limit set in control and if so, sets fan to high
		#by being the last check in the control method, it insures a high temp will cause fans on
		for dg in devices:
			for d in dg:
				if d.growType == "tempSensor":
					if d.lastTemp > control.MaxTemp:
						self.status = RELAYON
						print "!!!!!--ERROR--!!!!!"
						print "-- Fan " + str(self.id) + " status changed because of high reading on Temp Sensor " + str(d.id)
						print "!!!!!--ERROR--!!!!!"
						
		GPIO.output(self.pin, self.status) #finally set the fan value

			
					
	def returnStatusString(self):
		if self.status == RELAYON:
			return "On"
		else:
			return "Off"

		
class tempSensor:
#properties:	
	# sensorNumber: Index of the sensor, relative only to this class
	# pin: the GPIO number used on the pi
	# sensorType: sensor name ie: DHT22, DHT11, AM2302
	# sensorLibrary: the library that needs to be imported for the sensor
	#					is what is called to read the sensor, if not needed pass in dummy value
	# lastTemp: the value the last time temp was taken
	# lastHumd: the humidity last time it was taken
	# growType: value included in all growControl classes, describes the sensor.  Should not be used in production code
	# reportHeaders: the data in the top row of an output file
#methods
	# __init__: creates an instance
	# update(): reads the sensor
	# returnStatusString(): returns a string of the last recorded data
	
	def __init__(self, sensorNumber, pin, sensorType, sensorLibrary):
		##########
		#configurable values
		##########
		self.id = sensorNumber #number of the sensor, index starts at 0
		self.pin = pin #GPIO pin used
		self.lastTemp = -9999 #set to the last measured temperature, init at impossible value, value in C
		self.lastHumd = -9999 #set the the last measured humidity, init at impossible value, value in %
		self.sensorType = sensorType
		self.sensorLibrary = sensorLibrary #library that is called to read the sensor, needed for Adafruit stuff
		self.iteratationsToVal = -9999
		##########
		#hard coded but configurable in source code
		##########
		self.reportItemHeaders = "Temp Sensor:" + str(self.id) + "  On Pin:" + str(self.pin) + "," + "Humidity Sensor:" + str(self.id) + "  On Pin:" + str(self.pin) + "," + "Iterations to Get a Value on Pin:" + str(self.pin)
		self.growType = "tempSensor"
		self.retries = 5 # number of times to attempt to read before giving update
		self.retriesPause = 0.5 # time to wait between retries, in seconds
	
	def initGPIO(self, GPIO, curEpochTime):
		print "initGPIO inside of tempSensor " + str(self.id)
	
	def update(self):
		#print "In tempSensor[" + str(self.id) + "].update()" #debug
		#if statement so other sensors can be easily added
		#only including the 22 here because that is all I have to test
		print "Reading Tempature Sensor: " + str(self.id)
		if self.sensorType == "DHT22":
			#read in the sensor
			for ii in range(self.retries):
				humidity, temperature = self.sensorLibrary.read(22, self.pin) ## 22 is what Adafruit_DHT.DHT22 returns in example .\Adafruit_Python_DHT\examples\AdafruitDHT.py
				if humidity is not None and temperature is not None:
					self.lastTemp = temperature
					self.lastHumd = humidity
					self.iteratationsToVal = ii
					print 'Temp={0:0.1f}*C  Humidity={1:0.1f}%'.format(temperature, humidity)
					break # have the data, now leave
			else:
				self.iteratationsToVal = -9999
				print 'Failed to get reading'
		
		elif self.sensorType == "test": #test case
			from random import randint as rand
			self.lastTemp = rand(0,25)
			self.lastHumd = rand(0,100)
			self.iteratationsToVal = -1
			print "leaving Test"

		else:
			print("Error reading in temp sensor type. This should cause an exception")
	
	def returnStatusString(self):
		return str(self.lastTemp) + "," + str(self.lastHumd) + "," + str(self.iteratationsToVal)

		
class control:
#all the control variables go here
	def __init__(self,maxTemp,minTemp,recordInterval):
		self.maxTemp = maxTemp #max tempature of the system , causes light to go off, in C
		self.minTemp = minTemp #minimum tempature of the system, in C
		self.recordInterval =recordInterval #how often to record, in seconds