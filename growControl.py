#this file defines the objects and functions for the grow control program

def readStatus(devices):
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
	
	
def writeStatus(devices,fileName):
# this function goes over all the devices and writes their status to the output file.
# expects a list of lists of devices, each device must have the method returnStatusString()

	statusOut = "" 
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
	headersOut = "" 
	for deviceGrp in range(len(devices)): #loop over each device group
		for device in range(len(devices[deviceGrp])): # loop over each device in the group
			headersOut=headersOut + devices[deviceGrp][device].reportItemHeaders + "," # add the status to the string
	
	
	outFile = open(fileName,"a") #open the file for appending
	outFile.write(headersOut + "\n") #append the file with the data
	outFile.close() #close the file
	
	
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
		# return what ever data we want to output here
		# all data validation should be done here
		# order must be the same as self.reportItemHeaders
		
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
		# return what ever data we want to output here
		# all data validation should be done here
		# order must be the same as self.reportItemHeaders
		
		if self.status == 1:
			return "On"
		else:
			return "Off"
			
		
	
	
class tempSensor:
	def __init__(self,sensorNumber,pin,sensorType):
		##########
		#configurable values
		##########
		self.id = sensorNumber #number of the sensor, index starts at 0
		self.pin = pin #GPIO pin used
		self.sensorType = type #string "DHT22" is only one currently being used
		self.lastTemp = -9999 #set to the last measured tempature, init at impossible value, value in C
		self.lastHumd = -9999 #set the the last measured humidity, init at impossible value, value in %
	
	
		##########
		#hard coded but configurable in source code
		##########
		self.reportItemHeaders = "Temp Sensor:" + str(self.id) + "  On Pin:" + str(self.pin) + "," + "Humidity Sensor:" + str(self.id) + "  On Pin:" + str(self.pin)
		self.growType = "tempSensor" #debugging
		
		
	def update(self):
		print "In tempSensor[" + str(self.id) + "].update()"
	
	def returnStatusString(self):
		# return what ever data we want to output here
		# all data validation should be done here
		# order must be the same as self.reportItemHeaders
		
		return str(self.lastTemp) + "," + str(self.lastHumd)
		
		

class control:
#all the control variables go here
	def __init__(self,maxTemp,minTemp,recordInterval):
		self.maxTemp = maxTemp #max tempature of the system , causes light to go off, in C
		self.minTemp = minTemp #minimum tempature of the system, in C
		self.recordInterval =recordInterval #how often to record, in seconds
		
	
