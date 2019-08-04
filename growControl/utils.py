from growControl import Environments as Environments
from growControl import Sensors as Sensors
from growControl import Controls as Controls

class CircularBuffer(object):
    '''

    '''

    def __init__(self,length=10):
        '''
        Creates a circular buffer with length 10
        '''
        self.length = length
        self.data = [0]*length
        self.sum = 0.
        self.current_location = 0
        self.average = 0.


    def update(self,value):
        '''
        Add a value to the buffer
        '''
        self.sum -= self.data[self.current_location]
        self.data[self.current_location] = value
        self.sum += value
        
        if self.current_location < self.length-1:
            self.current_location += 1
        else:
            self.current_location = 0
        
        self.average = self.sum/self.length

    def __len__(self):
        return self.length

def BuildChildren(config,parent):
    '''
    Take in the config dict and parent name
    Return the generated children for the object

    This uses the ImplmentedX dicts in the Environments, Controls, and Sensor files to resolve the 
        class that is to be created
    '''
    children = config["children"]
    result = {}
    for child in children:
        child_type = children[child]["type"]

        if child_type in Environments.ImplementedEnvironments:
            result[children[child]["name"]] = Environments.ImplementedEnvironments[child_type](children[child],parent)
        elif child_type in Sensors.ImplementedSensors:
            result[children[child]["name"]] = Sensors.ImplementedSensors[child_type](children[child],parent)
        elif child_type in Controls.ImplementedControls:
            result[children[child]["name"]] = Controls.ImplementedControls[child_type](children[child],parent)
        else:
            print("Did not find implementation for item with name: {} type: {}\n\t".format(config["name"],child_type) +
                "It may not be implemented or may not have been added to the .ImplementedX in the corresponding file")
    return result