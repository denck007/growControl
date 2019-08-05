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