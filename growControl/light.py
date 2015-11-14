
class light:
	def __init__(self, lightNumber, pin, timeOn, timeOff, relayOn, relayOff):
		##########
		#configurable values
		##########
		self.id = lightNumber #number of the light, index starts at 0
		self.pin = pin #GPIO pin used
		self.timeOn = timeOn #time the light comes on, ex: 0705 for 7:05am; 1934 for 7:34 pm
		self.timeOff = timeOff #time the light turns off
		
		self.relayOn = relayOn
		self.relayOff = relayOff
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
		self.status = self.relayOff # Lights should only turn on after initialization
		self.growType = "light"
			
	def returnStatusString(self):
		if self.status == self.relayOn:
			return "On"
		else:
			return "Off"
		
	def control(self, devices, control, GPIO):
		import growControl as gc
		
		oldStatus = self.status
		testOn = gc.getMinuteDiff(self.timeOn)
		testOff = gc.getMinuteDiff(self.timeOff)
		
		if testOn >= 0 and testOff < 0:
			# time in the off times, set light off
			self.status = self.relayOn
			print "Controling Light" + str(self.id) + ": Set to On"
		else:
			# if the light is not between the off times, it should be on
			self.status = self.relayOff
			print "Controling Light" + str(self.id) + ": Set to Off"
		
		if oldStatus != self.status:
			print "STATUS CHANGE: LIGHT " + str(seld.id)
		
		# this must always be the last thing to run in the control method
		# it checks if any of the temperature sensors are exceeding the limit set in control and if so, sets light to low
		# by being the last check in the control method, it insures a high temp will cause light on
		for d in devices:
			if d.growType == "tempSensor":
				if d.lastTemp >control.MaxTemp:
					self.status = self.relayOff
					gc.errorDisplay("-- Light " + str(self.id) + " status changed because of high reading on Temp Sensor " + str(d.id))
											
		GPIO.output(self.pin, self.status) #finally set the light value
	
	def initGPIO(self, GPIO, curEpochTime):
		GPIO.setup(self.pin,GPIO.OUT) #initialize the pin as out
		GPIO.output(self.pin,self.status) # initialize the light to default value, should be off
		
		self.lastOn = curEpochTime #set the first on time light was turned on to now
		self.lastOff = curEpochTime # set the last time the light was turned off to now	

