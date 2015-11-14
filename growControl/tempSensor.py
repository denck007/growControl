
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
	
	def __init__(self, sensorNumber, pin, sensorType, sensorLibraryPath):
		##########
		#configurable values
		##########
		self.id = sensorNumber #number of the sensor, index starts at 0
		self.pin = pin #GPIO pin used
		self.lastTemp = -9999 #set to the last measured temperature, init at impossible value, value in C
		self.lastHumd = -9999 #set the the last measured humidity, init at impossible value, value in %
		self.sensorType = sensorType
		self.iteratationsToVal = -9999
		##########
		#hard coded but configurable in source code
		##########
		try:
			import sys
			sys.path.append(sensorLibraryPath)
			import Adafruit_DHT #import the AdaFruit libraries
			self.sensorLibrary = Adafruit_DHT #library that is called to read the sensor, needed for Adafruit stuff

		except:
			print "Error importing Adafruit_DHT from path: " + sensorLibraryPath + " for temp sensor number " + str(self.id) + " on pin " + str(self.pin)
		self.reportItemHeaders = "Temp Sensor:" + str(self.id) + "  On Pin:" + str(self.pin) + "," + "Humidity Sensor:" + str(self.id) + "  On Pin:" + str(self.pin) + "," + "Iterations to Get a Value on Pin:" + str(self.pin)
		self.growType = "tempSensor"
		self.retries = 5 # number of times to attempt to read before giving update
		self.retriesPause = 0.5 # time to wait between retries, in seconds
	
	def initGPIO(self, GPIO, curEpochTime):
		#print "initGPIO inside of tempSensor " + str(self.id)
		x=0
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
