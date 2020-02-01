# Simple Grow Controller
The idea with this setup is to get a controller working very quickly at the expense of not being generic.

General outline:
1) Initialize ph sensor, ph pump controller, and humidity/temp sensor
2) In loop:
   1) Read ph (if enough time has passed)
   2) Control the ph if the ph sensor is reporting a value outside of range (if enough time has passed since last control)
   3) Read the humidity and temp (if enough time has passed)

* After every read the data is stored to disk in 1 csv file per sensor (humidity and temp are split into 2 files)
* The sensors keep a running average of the current state using a weighted moving average
 * Does not keep the history but does an update according to `running_average = weight*running_average + (1-weight)*new_reading`. THis means the value can lag some, but in the control of this system we are going to be recording every 30 seconds or so, and controlling every 30 minutes.
 * 

# Sensors:

All sensors have the following parameters:
* average_factor: range of (0,1), 1 per value read from sensor
* read_every: float, minimum number of seconds between reading
* last_reading: float, epoch of last reading, updated after each reading is taken, 1 value per value read from sensor
* output_file: str of valid path
 * Will create if does not exist
 * Always appends to this file

Sensors are also expected to have an optional initialization parameter of a csv file path for testing. This file should have 1 row per reading, if the device returns multiple parameters, the order those parameters are returned in (ie in the tuple) should be obeyed in the file. When a csv is passed the sensor will simply substitue the normal sensor reading function with a call to read the next line of the csv.

# Controllers:
Currently there is only the ph controller that runs pumps. This takes in the sensor that it is using to control from, and controls 2 pumps according to the sensor_ph.ph_avg value. If the ph is under the parameter self.ph_min, turn on the pump for the ph up solution. If the ph is over self.ph_max then turn on the pump for the ph down solution.  This controller is only expected to turn on the pumps for ~0.5seconds every hour if an adjustment is needed. Likely it will only turn on the pumps once a day or so. 

# Controllable devices:
Currently the only controllable device is the peristaltic pump. When called it takes the duration it should run for and will turn the pump on for the specified time. This actions blocks any other code with a sleep.