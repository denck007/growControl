def readConfig(GPIO):
# This will eventually be the function that reads in the configuration file and does all of the initial validation
# Until then, this function will have kind of random things happening in it
# This function will eventually only need to be passed the GPIO module and the config file name
	
	# Check the relay type, allows support for normally open and normally closed relays
	# The intention here is to make the device methods easier to understand
	# 		by not having things turn on when set to low
	
	print "Starting to parse the config file"
	
	import growControl as gc
	import ConfigParser
	
	curTimeEpoch = gc.getDateTime(0,0,1,0)
	currentTimeString = gc.getDateTime(0,0,0,1)
	
	def ConfigSectionMap(section):
		dict1 = {}
		options = Config.options(section)
		for option in options:
			try:
				dict1[option] = Config.get(section, option)
				if dict1[option] == -1:
					DebugPrint("skip: %s" % option)
			except:
				print("exception on %s!" % option)
				dict1[option] = None
		return dict1
    
	inputs = []
	outputs = []
	controls = -1
	
	Config = ConfigParser.ConfigParser()

	configFile = '/home/pi/git/growControl/growControl.config' 
	#configFile = 'C:\\Users\\Neil\\Documents\\GitHub\\growControl\\growControl.config'
	Config.read(configFile)

	print "Devices found in the config file:"
	sectionNames = Config.sections()
	print sectionNames

	for ii in range(len(sectionNames)):
		try:
			name = sectionNames[ii][:-3]
			number = int(sectionNames[ii][-3:])
		except:
			gc.errorDisplay("Error in reading in a section name from the config file")
			
#controls
		if name == "controls":
			print "Creating controls"
			maxTemp = int(ConfigSectionMap(sectionNames[ii])['max_temp'])
			minTemp = int(ConfigSectionMap(sectionNames[ii])['min_temp'])
			recordInterval =int(ConfigSectionMap(sectionNames[ii])['record_interval']) #how often to record, in seconds
			baseFileName = ConfigSectionMap(sectionNames[ii])['base_file_name'] #the file name to start with
			fileLength = int(ConfigSectionMap(sectionNames[ii])['file_length']) #number of lines to record in the file
			controls = gc.control.control(maxTemp,minTemp,recordInterval,fileLength,baseFileName, currentTimeString)
			
#temp sensor
		elif name == "temp":
			print "Creating " + sectionNames[ii]
			id = number
			pin = int(ConfigSectionMap(sectionNames[ii])['pin'])
			sensorType = ConfigSectionMap(sectionNames[ii])['sensor_type']
			libraryPath = ConfigSectionMap(sectionNames[ii])['library_path']
			inputs.append(gc.tempSensor.tempSensor(number, pin, sensorType, libraryPath))

#fan
		elif name == "fan":
			print "Creating " + sectionNames[ii]
			id = number
			pin = int(ConfigSectionMap(sectionNames[ii])['pin'])
			fanOnType= int(ConfigSectionMap(sectionNames[ii])['fan_on_type'])
			timeOn = int(ConfigSectionMap(sectionNames[ii])['time_on'])
			timeOff = int(ConfigSectionMap(sectionNames[ii])['time_off'])
			relayOn, relayOff = checkRelayType(GPIO, ConfigSectionMap(sectionNames[ii])['relay_type'])
			outputs.append(gc.fan.fan(number, pin, fanOnType, timeOn, timeOff, relayOn, relayOff))
			
#light
		elif name == "light":
			print "Creating " + sectionNames[ii]
			id = number
			pin = int(ConfigSectionMap(sectionNames[ii])['pin'])
			timeOn = int(ConfigSectionMap(sectionNames[ii])['time_on'])
			timeOff = int(ConfigSectionMap(sectionNames[ii])['time_off'])
			relayOn, relayOff = checkRelayType(GPIO, ConfigSectionMap(sectionNames[ii])['relay_type'])
			outputs.append(gc.light.light(number, pin, timeOn, timeOff, relayOn, relayOff))


	return [inputs, outputs, controls]

def checkRelayType(GPIO, rt):


	if GPIO == "TEST":
		#testing on PC(GPIO does not exist here) testCase
		relayOn = 1
		relayOff = 0
	else:
		if rt == "NORMALLY_OPEN":
			# The relays are normally open, the attached device is not receiving power when the input pin is set to 0V
			relayOn = GPIO.HIGH
			relayOff = GPIO.LOW
		elif rt == "NORMALLY_CLOSED":
			# The relays are normally closed, the attached device is receiving power when the input pin is set to 0V
			relayOn = GPIO.LOW
			relayOff = GPIO.HIGH
		else: 
			gc.errorDisplay("The relay type of GPIO is not defined properly")
			relayOn = "ERROR"
			relayOff = "ERROR"

	
	return [relayOn, relayOff]
	