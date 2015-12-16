# -*- coding: utf-8 -*-
"""
Created on Mon Dec 14 23:03:49 2015

@author: Neil
"""

directory = "C:\\Users\\Neil\\Documents\\GitHub\\growControl\\"
baseFileName = "allNight2_"
#inputFile = "allNight2_20151214020119.csv"
figureFile = "test.pdf"
figSaveTo = directory + figureFile
#fileName = directory + inputFile


import matplotlib.pyplot as plt
import numpy as np
import csv
import glob # to get the files in the directory


def getColumn(filename, column):
    results = csv.reader(open(fileName), delimiter=",")
    x = [result[column] for result in results]
    return [x[0], x[1:len(x)]]
    
def padString(strIn,endLength,padWith):
    # function adds padWith to the end of strIn until it is longer than endLength
    while(len(strIn)<endLength):
        strIn = strIn + padWith
    return strIn

class fileData:
    def __init__(self):
        self.title = ""
        self.data = []
    def getDataByColNum(self, fName, columnNum):
        # Open file fName and set the data to the instance
        results = csv.reader(open(fName), delimiter=",")        
        x = [result[columnNum] for result in results]
        
        # do a quick check to make sure the column titles are consistant, only wars you.
        if self.title != x[0] and self.title != "":
            print("Warning Changing the title of the column when reading data")
            print("The Title was: " + self.title)
            print("And is being changed to: " + x[0])
        self.title = x[0]
        self.data = self.data + x[1:]
    
    
class plotTimeData:
    def __init__(self):
        self.xTitle = ""
        self.yTitle = ""
        self.timeStrings = [] # list that contains the actual times
        self.xData = [] # integer list to plot
        self.yData = [] # y axis data to plot
        self.timeRange = 0 # the total time range of the data received
        self.dataLabelSpacing = 0 # how often to put a data label
        
    def getDataByColNum(self, fName, colTime, colData):
        # Open file fName and set the data to the instance
        results = csv.reader(open(fName), delimiter=",")        
        x = [result[colTime] for result in results]
        y =  [result[colData] for result in results]
        
        # do a quick check to make sure the column titles are consistant, only warns you.
        if self.xTitle != x[0] and self.xTitle != "":
            print("Warning: Changing the title of the time column when reading data")
            print("The Title was: " + self.xTitle)
            print("And is being changed to: " + x[0])
        self.xTitle = x[0]
        self.timeStrings = self.timeStrings + x[1:]
        
        # do a quick check to make sure the column titles are consistant, only warns you.
        if self.yTitle != y[0] and self.yTitle != "":
            print("Warning: Changing the title of the data column when reading data")
            print("The Title was: " + self.yTitle)
            print("And is being changed to: " + y[0])
        self.yTitle = y[0]
        self.yData = self.yData + y[1:]    
        
        self.xData = np.arange(0,len(self.timeStrings),1) # cannot plot using dates
        
    def setDataSpacing(self):
        self.timeRange = int(self.timeStrings[-1:])-int(self.timeStrings[0])
    
    
    
    
    
    
    
    
    
    
    
"""
The idea is that the user enters as specific as date as they want.  
The number of digits signifies how much data is returned.
                                        
Date string format must be of the form YYYYMMDDHHmmSS
There must be at least a year specified
Ex: if 2015-December-12 14:00:00 is requested this should be specified: 2015121414 
"""
startTime = 201512141900
endTime =   201512160000

#clean up the user input so it matches the file names
# Note that this adds 1 to endTime, this makes it inclusive
if startTime<endTime:
    startTime = int(padString(str(startTime),14,"0"))
    endTime = int(padString(str(endTime+1),14,"0"))
else:
    print("error, the start time is after the end time")
    

# get all files that are created with the correct base name 
potentialFiles = glob.glob(directory + baseFileName + "*.csv")

dataFiles = []
for f in potentialFiles:
    fileTime = int(f[-18:-4])
    if fileTime >= startTime and fileTime <= endTime:
        dataFiles.append(f)


print(str(len(potentialFiles)) + " Potential Files Found:")
for f in potentialFiles:
    print(f)
print(str(len(dataFiles)) + " Data Files Found:")
for f in dataFiles:
    print(f)
    

# initialize the data objects    
xData = fileData()
yData = fileData()

# read in the data
for f in dataFiles:
    xData.getDataByColNum(f,0)
    yData.getDataByColNum(f,1)



# create the plot
fig = plt.figure()


plt.plot(xNumbers,yData.data)

labels = xData.data
plt.xticks(xNumbers,labels,rotation='vertical')


#plt.plot(xNumbers,yData2)

fig.savefig(figSaveTo)#, bbox_inches='tight')
plt.show()
