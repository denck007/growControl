class control:
#all the control variables go here
	def __init__(self,maxTemp,minTemp,recordInterval,fileLength,baseFileName, currentTime):
		self.maxTemp = maxTemp #max tempature of the system , causes light to go off, in C
		self.minTemp = minTemp #minimum tempature of the system, in C
		self.recordInterval =recordInterval #how often to record, in seconds
		self.baseFileName = baseFileName #the file name to start with
		self.fileLength = fileLength #number of lines to record in the file
		self.fileName = baseFileName + currentTime + ".csv" #first file name to save to
		self.iterations = 1 #initialize the iteration counter to 1
		self.fileHeaders = "" # the headers for the output file, initialize to empty string
	
	def check(self,currentTime):
		# check to make sure that everything is within the extremes 
		print "Should probably check the extremes here"
		print "Max iterations " + str(self.fileLength) 
		print "Current iteration " + str(self.iterations)
		# update the file name if it is too long
		if self.iterations > self.fileLength:
			print "At iteration limit for file length, creating new file..."
			self.fileName = self.baseFileName + currentTime + ".csv"
			self.iterations = 1 #reset the counter
			outFile = open(self.fileName,"a") #open the file for appending
			outFile.write(self.fileHeaders + "\n") #append the file with the data
			outFile.close() #close the file
		else: 
			#print "Under limit of iterations"
			self.iterations = self.iterations + 1 #add to the counter
		
		