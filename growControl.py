#this file defines the objects and functions for the grow control program

def readStatus(devices):
#read the status of the devices
#devices must have the self.update() method
	for deviceGrp in range(len(devices)):
		#print "readStatus - deviceGrp: " + str(deviceGrp)
		for device in range(len(devices[deviceGrp])):
			#print "readStatus - device: " + str(device)
			devices[deviceGrp][device].update()
		
def deviceControl(devices):
	for deviceGrp in range(len(devices)):
		#print "deviceControl - deviceGrp: " + str(deviceGrp)
		for device in range(len(devices[deviceGrp])):
			#print "deviceControl - device: " + str(device)
			devices[deviceGrp][device].control(devices,control)
	
	
def writeStatus(devices,fileName,theTime):
# this function goes over all the devices and writes their status to the output file.
# expects a list of lists of devices, each device must have the method returnStatusString()
	statusOut = theTime 
	for deviceGrp in range(len(devices)): #loop over each device group
		for device in range(len(devices[deviceGrp])): # loop over each device in the group
			print "writeStatus - deviceGrp: " + str(deviceGrp) + "  device: " + str(device) #debug
			print str(devices[deviceGrp][device].growType)
			statusOut=statusOut + devices[deviceGrp][device].returnStatusString() + "," # add the status to the string
	
	
	outFile = open(fileName,"a") #open the file for appending
	outFile.write(statusOut + "\n") #append the file with the data
	outFile.close() #close the file
	
	
def initFile(devices,fileName):
# This function reads in the headers defined in the object definition for the column headers
# writes device.reportItemHeaders() to the given file
	headersOut = "Date and Time:"
	for deviceGrp in range(len(devices)): #loop over each device group
		for device in range(len(devices[deviceGrp])): # loop over each device in the group
			headersOut=headersOut + devices[deviceGrp][device].reportItemHeaders + "," # add the status to the string
	
	
	outFile = open(fileName,"a") #open the file for appending
	outFile.write(headersOut + "\n") #append the file with the data
	outFile.close() #close the file
	
	
def getDateTime(d,t):
	#returns the date and or time
	# if date ==1 return the date
	# if time ==1 return the time 
	# if both return both in YYYY-MM-DD-HHMM format
	# if neither, return blank string
	from time import localtime, strftime
	
	date = strftime("%Y",localtime())+ "-" +strftime("%m",localtime())+ "-" +strftime("%d",localtime())
	time = strftime("%H",localtime())+strftime("%M",localtime())
	if d>1 or d<0 or t>1 or t<0:
		return "Error in passing time values: Value out of input range"
	if d and t:
		return date + "-" + time
	elif(d):
		return date	
	elif t:
		return time
	else:
		return ""
	
	
	
	
##########	
#Class Defintions
##########	
# Generic Class Notes:
## ids
### should be in order with no id being used twice.
#
## returnStatusString()
### must return a string
### data format must match self.reportItemHeaders for csv file to make any sense
### if more that 2 data points are to be returned, then they must be separated by a comma
### do not include a comma at the start or end of the string
### data validation should be done here
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
		self.status = 0 # 0 for off, 1 for on, always init to 0
		self.growType = "light" #debugging
		
	
	def returnStatusString(self):
		if self.status == 1:
			return "On"
		else:
			return "Off"
			
			
	def control(self, devices, configControl):
		print "In light[" + str(self.id) + "].control"

	
	
class fan:
#definition of a fan
	def __init__(self,fanNumber,pin, fanType):
		##########
		#configurable values
		##########
		self.id = fanNumber #number of the fan, index starts at 0
		self.pin = pin #GPIO pin used
		self.fanType = fanType # the type of fan it is, 1= inlet, 2 = exhaust, 3 = internal
		
		##########
		#hard coded but configurable in source code
		##########
		self.reportItemHeaders = "Fan:" + str(self.id) + "  On Pin:" + str(self.pin)
		
		
		##########
		#hard coded and should not be messed with
		##########
		self.status = 0 # 0 for off, 1 for on, always init to 0
		self.growType = "fan" #debugging
	
	
	def control(self, devices, configControl):
		print "In fan[" + str(self.id) + "].control"

	def returnStatusString(self):
		if self.status == 1:
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
	
	def __init__(self,sensorNumber,pin,sensorType,sensorLibrary):
		##########
		#configurable values
		##########
		self.id = sensorNumber #number of the sensor, index starts at 0
		self.pin = pin #GPIO pin used
		self.lastTemp = -9999 #set to the last measured temperature, init at impossible value, value in C
		self.lastHumd = -9999 #set the the last measured humidity, init at impossible value, value in %
		self.sensorLibrary = sensorLibrary #library that is called to read the sensor, needed for Adafruit stuff
		self.iteratationsToVal = -9999
		##########
		#hard coded but configurable in source code
		##########
		self.reportItemHeaders = "Temp Sensor:" + str(self.id) + "  On Pin:" + str(self.pin) + "," + "Humidity Sensor:" + str(self.id) + "  On Pin:" + str(self.pin) + "," + "Iterations to Get a Value:"
		self.growType = "tempSensor" #debugging
		self.retries = 5 # number of times to attempt to read before giving update
		self.retriesPause = 0.5 # time to wait between retries, in seconds
		
		##########
		#check for the sensor type
		##########
		if sensorType == "DHT22":
			self.sensorType = sensorLibrary.DHT22
		elif sensorType == "X":
			print 'This is only a test case'
			self.sensorType = -9999
		else:
			print("Error reading in temp sensor type. This should cause an exception")
			
			


	def update(self):
		print "In tempSensor[" + str(self.id) + "].update()"
		#if statement so other sensors can be easily added
		#only including the 22 here because that is all I have to test
		if self.sensorType == self.sensorLibrary.DHT22:
			#read in the sensor
			for ii in range(self.retries):
				humidity, temperature = self.sensorLibrary.read(self.sensorType, self.pin)
				if humidity is not None and temperature is not None:
					self.lastTemp = temperature
					self.lastHumd = humidity
					self.iteratationsToVal = ii
					print 'Temp={0:0.1f}*  Humidity={1:0.1f}%'.format(temperature, humidity)
					break # have the data, now leave
			else:
				self.iteratationsToVal = -9999
				print 'Failed to get reading'
		
	def returnStatusString(self):
		return str(self.lastTemp) + "," + str(self.lastHumd) + "," + str(self.iteratationsToVal)
		
		
class control:
#all the control variables go here
	def __init__(self,maxTemp,minTemp,recordInterval):
		self.maxTemp = maxTemp #max tempature of the system , causes light to go off, in C
		self.minTemp = minTemp #minimum tempature of the system, in C
		self.recordInterval =recordInterval #how often to record, in seconds
		
	
