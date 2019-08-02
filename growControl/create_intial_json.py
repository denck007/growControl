import json

SensorTemperature = 1
SensorPh = 2
ControlPeristalticPump = 3
ControlPeristalticPump = 4

ph_up = {"type":"ControlPeristalticPump","name":"ph_up"}
ph_down = {"type":"ControlPeristalticPump","name":"ph_down"}
pot1_temp = {"type":"SensorTemperature","name":"pot1_temp","comms_address":"0x40"}
pot1_ph = {"type":"SensorPh_ADS1115", # The name of the python class to use
            "name":"pot1_ph", # What the sensor is called, this is saved in the output
            "bus_address":"0x48", # In this case the SensorPh uses I2C so this address is used
            "save_every_seconds":60, # Wait at least this many seconds before saving the next datapoint
            "average_over_samples":30, # Keep running average of last n samples
            "ads1115_gain":8, # The gain to use from the ads1115, 
            "ads1115_data_sample_rate":8, # the sample rate from ads1115, note that the device will average the analog input since the last reading
            "differential_input1":"P0", # The pin to use as reference
            "differential_input2":"P1" # the pin to use as the value
            }
pot1_children = {"temperature":pot1_temp,"pot1_ph":pot1_ph,"ph_up":ph_up,"ph_down":ph_down}
pot1 = {"type":"Pot","name":"Pot1","children":pot1_children}

temperature_environment = {"type":"SensorTemperature",
                            "name":"temperature_environment",
                            "comms_address":"0x40"}

children = {"pot1":pot1,
            "temperature_environment":temperature_environment}
zone1 = {"type":"Zone","name":"Zone1","children":children}
zone2 = {"type":"Zone","name":"Zone2","children":children}

world = {"zone1":zone1,"zone2":zone2,"outfile":"dataout.json"}

with open("setup.json",'w') as f:
    json.dump(world,f,indent=2)



