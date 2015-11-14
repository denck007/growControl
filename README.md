# growControl
###Scope
This is my first raspberry pi project, so we will see how it goes.

Grow Control is an experiment with a raspberry pi to control an indoor vegtable growing setup.

The initial goal is to control a light with a few tempature sensors and fans.
Future goals include automated watering, pH testing, and possibly control for hydroponics.

###Using growControl
The project is kind of set up as a package right now (I think...I have never made one before).  The control/operation parameters for lights, fans, temp sensors, and some simple control stuff is defined in the growControl.config file.  The file path is currently hard coded in readConfig.py.  When you call growControl.readConfig.readConfig(RPi.GPIO) it reads in the config file and returns objects that define input and output(setable) devices as well as the control object.

All of the control, reading sensors, changing status of output devices, and writing to the file is handeled by calling specific methods.  The methods are consistant across all devices. Calling the methods is straight forward and can be found in the growControlMain.py file.

To run the project as is, you will need the listed dependencies, and pull the project to /home/pi/git/growControl/
Configure the growControl.config file as needed.  Note there is almost no error checking implemented.  
Run growControlMain.py

###Dependencies: 
*Adafruit_DHT: Must be included in your sys.path

