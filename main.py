
'''
This is the main file for running the grow control system
'''

import json
from growControl.Environments import Zone

class World:
    def __init__(self,config):
        '''
        '''
        self.outfile = config["outfile"]
        self.children = []

        for key in config:
            if key == "outfile":
                pass
            elif config[key]["type"] == "Zone":
                self.children.append(Zone(config[key],self))
            else:
                print("Unrecognized key {} in world".format(key))

    def update(self):
        '''
        Update the state of the system
        Read all sensors and update all controls
        '''
        for child in self.children:
            child.update()
    
    def report_data(self):
        '''
        Output a dict that can be passed up the chain for outputing the data
        '''
        # get all of the children's data
        data = {}
        for child in self.children:
            data[child.name] = child.report_data()
        
        return data

if __name__ == "__main__":
    # Read in the config file
    with open("setup.json",'r') as f:
        config = json.loads(f.read())
    world = World(config)

    
    for ii in range(10):
        world.update()
        data = world.report_data()
        print(data)
    


    