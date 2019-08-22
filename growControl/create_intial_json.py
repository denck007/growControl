import json

SensorTemperature = 1
SensorPh = 2
ControlPeristalticPump = 3
ControlPeristalticPump = 4


pot1_temp = {"type":"SensorTemperature","name":"pot1_temp","comms_address":"0x40"}
Pot1_ph = {"type":"SensorPh_ADS1115", # The name of the python class to use
            "name":"Pot1_Ph", # What the sensor is called, this is saved in the output
            "bus_address":"0x48", # In this case the SensorPh uses I2C so this address is used
            "save_every_seconds":60, # Wait at least this many seconds before saving the next datapoint
            "average_over_samples":30, # Keep running average of last n samples
            "ads1115_gain":8, # The gain to use from the ads1115, 
            "ads1115_data_sample_rate":8, # the sample rate from ads1115, note that the device will average the analog input since the last reading
            "single_ended_input":"P0", # The pin on the ADC to read for the pH
            }

Pot1_ControlPh= {"type":"ControlPh", # The object type we are creating
                "name":"Pot1 Control Ph", # What to call it in the output
                "directly_controllable":True, # sets if the object has its own control algorithm, or if it is in another objects control algorithm
                "minimum_control_time":3.0, # Minimum amount of time between actions for this control
                "SensorPh_name":"Pot1_Ph", # Item that it needs information from
                "ControlPh_up_name":"Pot1_Ph_up", # The name of the oject that runs ph up
                "ControlPh_down_name":"Pot1_Ph_down", # The name of the oject that runs ph down
                "targetValue":6.0, # the ph value we are targeting
                "targetRange":0.2, # +/- tolerance on targetValue. targetValue=6 w/ targetRange=0.2 => control to 5.8-6.2
                "mL_per_control":1.0 # mL to dispense per action
                }
Pot1_Ph_up = {"type":"ControlPeristalticPump",
                "name":"Pot1_Ph_up",
                "directly_controllable":False,
                "mL_per_second": 1.0,
                "GPIO":17} # The GPIO pin to use, GPIO17 is header pin 11
Pot1_Ph_down = {"type":"ControlPeristalticPump",
                "name":"Pot1_Ph_down",
                "directly_controllable":False,
                "mL_per_second": 1.0,
                "GPIO":27}# The GPIO pin to use, GPIO27 is header pin 13

pot1_children = {"temperature":pot1_temp,
                "pot1_ph":Pot1_ph,
                "Pot1_ControlPh":Pot1_ControlPh,
                "Pot1_Ph_down":Pot1_Ph_down,
                "Pot1_Ph_up":Pot1_Ph_up}

pot1 = {"type":"Pot",
        "name":"Pot1",
        "children":pot1_children}

temperature_environment = {"type":"SensorTemperature",
                            "name":"temperature_environment",
                            "comms_address":"0x40"}

children = {"pot1":pot1,
            "temperature_environment":temperature_environment}
zone1 = {"type":"Zone","name":"Zone1","children":children}
#zone2 = {"type":"Zone","name":"Zone2","children":children}

world = {"name":"world","type":"World","outfile":"dataout.json","children":{"zone1":zone1}}

with open("setup.json",'w') as f:
    json.dump(world,f,indent=2)



