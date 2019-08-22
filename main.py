
'''
This is the main file for running the grow control system
'''

import json
import time
from growControl import Environments
from growControl import Sensors
from growControl import Controls

class World:
    def __init__(self,config):
        '''
        '''
        # Save the output file name
        # Delete the reference so it is easier to loop over other items in the dict
        self.outfile = config["outfile"]
        config.pop("outfile")

        # Generate all of the objects    
        self.growObjects = self._initialize_child(config)

        # Generate all of the sensor and control links
        self._link_growObjects()

    def _initialize_child(self,config):
        '''
        Recursive function that creates all of the objects defined in the input file
        All objects are 
        '''
        children = config["children"]
        result = {}
        for child in children:
            child_type = children[child]["type"]
            
            if child_type in Environments.ImplementedEnvironments:
                result[children[child]["name"]] = Environments.ImplementedEnvironments[child_type](children[child])
            elif child_type in Sensors.ImplementedSensors:
                result[children[child]["name"]] = Sensors.ImplementedSensors[child_type](children[child])
            elif child_type in Controls.ImplementedControls:
                result[children[child]["name"]] = Controls.ImplementedControls[child_type](children[child])
            else:
                print("Did not find implementation for item with name: {} type: {}\n\t".format(config["name"],child_type) +
                    "It may not be implemented or may not have been added to the .ImplementedX in the corresponding file")
            
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

if __name__ == "__main__":
    # Read in the config file
    with open("setup.json",'r') as f:
        config = json.loads(f.read())
    world = World(config)
    #world.create_connections()

    
    for ii in range(10):
        world.update()
        world.run_controls()
        data = world.report_data()

        print()
        #print(data)
        time.sleep(1)
    


    