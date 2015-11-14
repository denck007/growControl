		
class fan:
#definition of a fan
	def __init__(self,fanNumber, pin, fanOnType, onTime, offTime, relayOn, relayOff):
		##########
		#configurable values
		##########
		self.id = fanNumber #number of the fan, index starts at 0
		self.pin = pin #GPIO pin used
		self.fanOnType = fanOnType # 1 = fan on between certain times in the day, 2=on for specified time, off for specified time, 3 = Always on
		self.fanOnAt = float(onTime) # the time the fan will turn on if fanOnType=1, duration fan on for if fanOnType=2
		self.fanOffAt = float(offTime) #time the fan turns off if fanOnType=1, duration fan off for if fanType=2
			# fanOffAt > fanOnAt, otherwise it will not work properly
		
		self.relayOn = relayOn
		self.relayOff = relayOff
		##########
		#hard coded but configurable in source code
		##########
		self.reportItemHeaders = "Fan:" + str(self.id) + "  On Pin:" + str(self.pin)
				
		##########
		#hard coded and should not be messed with
		##########
		self.status = self.relayOn # init to on
		self.growType = "fan"
		
	def initGPIO(self, GPIO, curEpochTime):
		GPIO.setup(self.pin,GPIO.OUT) #initialize the pin as out
		GPIO.output(self.pin,self.status) # initialize the fans to on
		
		self.lastOn = curEpochTime #set the first on time fan was turned on to now
		self.lastOff = curEpochTime # set the last time the fan was turned off to now
		
	def control(self, devices, control, GPIO):
		import growControl as gc
		oldStatus = self.status #record the original status so we know if it changes
		#run checks to see what type of fan and what controls to use, then actually control it
		if self.fanOnType == 1:
			#print "fanOnType == 1"
			testOn = gc.getMinuteDiff(self.fanOnAt)
			testOff = gc.getMinuteDiff(self.fanOffAt)
			#print ""
			#print "Fan " + str(self.id) + " testOn = " + str(testOn)
			#print "Fan " + str(self.id) + " testOff = " + str(testOn)

			if testOn >= 0 and testOff < 0:
				# time in the off times, set fan off
				self.status = self.relayOn
				print "Controling Fan" + str(self.id) + ": Set to On"
			else:
				# if the fan is not between the off times, it should be on
				self.status = self.relayOff
				print "Controling Fan" + str(self.id) + ": Set to Off"
			
		elif self.fanOnType ==2:
			# this type runs for fanOnAt minutes, then turns off for fanOffAt minutes
			print "fanOnType == 2 is not yet supported, please change the type of fan #" + str(self.id)
		elif self.fanOnType ==3:
			# this type is always on
			print "fanOnType == 3"				
			self.status = self.relayOn
		
		else:
			print "In fan" + str(self.id) + " fanOnType not defined or not recognized, setting to always on"
			self.status = self.relayOn

		if oldStatus != self.status:
			print "STATUS CHANGE: FAN " + str(self.id)
		
		#this should always be the last thing to run in the control method
		# it checks if any of the temperature sensors are exceeding the limit set in control and if so, sets fan to high
		#by being the last check in the control method, it insures a high temp will cause fans on
		for d in devices:
			if d.growType == "tempSensor":
				if d.lastTemp > control.MaxTemp:
					self.status = self.relayOn
					gc.errorDisplay("-- Fan " + str(self.id) + " status changed because of high reading on Temp Sensor " + str(d.id))
											
		GPIO.output(self.pin, self.status) #finally set the fan value

			
					
	def returnStatusString(self):
		if self.status == self.relayOn:
			return "On"
		else:
			return "Off"

