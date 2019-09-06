
'''
This is the main file for running the grow control system
'''

import json
import time
import sys

from growControl import World
from growControl import Environments
from growControl import Sensors
from growControl import Controls
try:
    import RPi.GPIO as GPIO
except:
    print("Error importing RPi.GPIO, may need to run with fake data")

if __name__ == "__main__":
    try:
        # Read in the config file
        with open("setup.json",'r') as f:
            config = json.loads(f.read())
        world = World.World(config)
       
        for ii in range(10000):
            world.update()
            world.run_controls()
            data = world.report_data()
            world.pause_main_loop()
    except:
        GPIO.cleanup()
        print("Unexpected error:", sys.exc_info()[0])
        raise

        

        


    
