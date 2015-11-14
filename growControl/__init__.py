
#init file for growControl


#import the everything needed
import readConfig 
import fan
import light
import tempSensor
import control


######################
# Generic functions end up here
######################
def readStatus(devices):
#read the status of the devices
#devices must have the self.update() method

	for device in range(len(devices)):
		#print "readStatus - device: " + str(device)
		devices[device].update()
		
def deviceControl(devices,control,theTime,GPIO):
	#print "In deviceControl"

	for device in range(len(devices)):
		#print "deviceControl - device: " + str(device)
		devices[device].control(devices,control,GPIO)
		
def writeStatus(devices,fileName,theDateTime):
# this function goes over all the devices and writes their status to the output file.
# expects a list of lists of devices, each device must have the method returnStatusString()
	statusOut = theDateTime + "," #start each line with the date/time

	for device in range(len(devices)): # loop over each device in the group
		statusOut=statusOut + devices[device].returnStatusString() + "," # add the status to the string
	
	
	outFile = open(fileName,"a") #open the file for appending
	outFile.write(statusOut + "\n") #append the file with the data
	outFile.close() #close the file
		
def initFile(devices,control):
# This function reads in the headers defined in the object definition for the column headers
# writes device.reportItemHeaders() to the given file
	headersOut = "Date and Time (YYYY-MM-DD-HH:MM:SS):,"
	for device in range(len(devices)): # loop over each device in the group
		headersOut=headersOut + devices[device].reportItemHeaders + "," # add the status to the string
	
	control.fileHeaders = headersOut
	outFile = open(control.fileName,"a") #open the file for appending
	outFile.write(headersOut + "\n") #append the file with the data
	outFile.close() #close the file

def initializeAllDevices(devices,GPIO):
# call the initGPIO on all the devices
	curEpochTime = getDateTime(0,0,1,0)
	for device in range(len(devices)):
		devices[device].initGPIO(GPIO,curEpochTime)
		
def getDateTime(d,t,s,iso):
	#returns the date and or time
	# if date ==1 return the date
	# if time ==1 return the time 
	# if both return both in YYYY-MM-DD-HH:MM:SS format
	# if only s return epoch time
	# iso returns the time in accordance with ISO 8601: YYYYMMDDTHHMMSS, in the local time zone
	from time import localtime, strftime, time

	if (d == 1 or t == 1 or iso == 1) and not s: #cases for returning strings
		date = strftime("%Y",localtime())+ "-" +strftime("%m",localtime())+ "-" +strftime("%d",localtime())
		time = strftime("%H",localtime())+":"+strftime("%M",localtime())+":"+strftime("%S",localtime())
		if d>1 or d<0 or t>1 or t<0:
			print "!!!!!--ERROR--!!!!!"
			print "Error in passing time values: User input value out of input range"
			print "!!!!!--ERROR--!!!!!"
		if (d and t) and not iso:
			return date + "-" + time
		elif (d and not t) and not iso:
			return date	
		elif (t and not d) and not iso:
			return time
		elif iso and not (t or d):
			return strftime("%Y",localtime())+strftime("%m",localtime())+strftime("%d",localtime()) + strftime("%H",localtime())+strftime("%M",localtime())+strftime("%S",localtime())
		else:
			return "Something unexpected happened in getting the time"
	elif s: # get epoch time
		return time()
	else:
		print "!!!!!--ERROR--!!!!!"
		print "No values requested from getDateTime()"
		print "!!!!!--ERROR--!!!!!"

def getMinuteDiff(timeToCompare):
	# returns the minute difference in the time from current time to timeToCompare()
	# 	EX: current local time is 1704, timeToCompare is 0605, returns 1099
	
	from time import strftime,localtime
	
	curTime = float(strftime("%H%M",localtime()))
	#print "Time to Compare: " + str(timeToCompare) #debugging
	#print "Current epoch Time: " + str(curTime) #debugging
	#print "Difference is: " + str(curTime - timeToCompare) #debugging
	return curTime - float(timeToCompare)

def errorDisplay(t):
	# cleanish way to call out an error in interactive mode 
	print ""
	print "!!!!!--ERROR--!!!!!"
	print t
	print "!!!!!--ERROR--!!!!!"
	print ""
	