
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

        

if __name__ == "__main__":
    # Read in the config file
    with open("setup.json",'r') as f:
        config = json.loads(f.read())
    world = World(config)

    
    


    