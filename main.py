
'''
This is the main file for running the grow control system
'''

import json
import time
import sys

from growControl import Environments
from growControl import Sensors
from growControl import Controls
try:
    import RPi.GPIO as GPIO
except:
    print("Error importing RPi.GPIO, may need to run with fake data")

class World:
    def __init__(self,config):
        '''
        '''
        # Save the output file name
        # Delete the reference so it is easier to loop over other items in the dict
        self.outfile = config["outfile"]
        self.main_loop_min_time = config["main_loop_min_time"]
        self.last_loop = 0.0
        config.pop("outfile")

        # Generate all of the objects    
        self.growObjects = self._initialize_child(config)

        # Generate all of the sensor and control links
        self._link_growObjects()

    def _get_ImplemetedGrowObjects(self):
        '''
        Go through all of the implemented items and create a unified dict
        '''
        ImplemetedGrowObjects = {}
        ImplemetedGrowObjects.update(Environments.ImplementedGrowObjects)
        ImplemetedGrowObjects.update(Sensors.ImplementedGrowObjects)
        ImplemetedGrowObjects.update(Controls.ImplementedGrowObjects)

        return ImplemetedGrowObjects


    def _initialize_child(self,config):
        '''
        Recursive function that creates all of the objects defined in the input file
        All objects are 
        '''
        children = config["children"]
        result = {}
        ImplemetedGrowObjects = self._get_ImplemetedGrowObjects()
        for child in children:
            child_type = children[child]["type"]
            child_name = children[child]["name"]
            
            if child_type in ImplemetedGrowObjects:
                result[child_name] = ImplemetedGrowObjects[child_type](children[child])
            else:
                print("Did not find implementation for item with name: {} type: {}\n\t".format(config["name"],child_type) +
                    "It may not be implemented or may not have been added to the <Sensors/Environments/Controls>.Implemented in the corresponding file")
            
            # If there are any children the recurse on them
            if "children" in children[child]:
                result.update(self._initialize_child(children[child]))

        return result

    def _link_growObjects(self):
        ''' 
        After all of the growObjects are created then we need to link objects that require a refernce to another object
        This is mostly for Control objects
        '''
        for key in self.growObjects:
            self.growObjects[key].link(self.growObjects)

    def update(self):
        '''
        Update the state of the system
        Read all sensors and update all controls
        '''
        for key in self.growObjects:
            self.growObjects[key].update()
    
    def run_controls(self):
        '''
        Execute the run_control method on every growObject that is directly controllable
        '''

        for key in self.growObjects:
            if self.growObjects[key].directly_controllable:
                self.growObjects[key].run_controls()

    def report_data(self):
        '''
        Output a dict that can be passed up the chain for outputing the data
        '''
        # get all of the children's data
        data = {}
        for key in self.growObjects:
            data.update(self.growObjects[key].report_data())
        
        return data

    def pause_main_loop(self):
        '''
        sleep until at least self.main_loop_min_time has passes since last loop
        '''
        time_since_last = time.time()-self.last_loop
        print("\tSleepTime: {:.5f} ".format(self.main_loop_min_time - time_since_last))
        delta_to_min = max(self.main_loop_min_time - time_since_last,0)
        time.sleep(delta_to_min)
        self.last_loop = time.time()

if __name__ == "__main__":
    try:
        # Read in the config file
        with open("setup.json",'r') as f:
            config = json.loads(f.read())
        world = World(config)
       
        for ii in range(100):
            world.update()
            world.run_controls()
            data = world.report_data()
            world.pause_main_loop()
    except:
        GPIO.cleanup()
        print("Unexpected error:", sys.exc_info()[0])
        raise

        

        


    
