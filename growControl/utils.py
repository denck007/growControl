#from growControl import Environments as Environments
#from growControl import Sensors as Sensors
#from growControl import Controls as Controls

class CircularBuffer(object):
    '''

    '''

    def __init__(self,data):
        '''
        Creates a circular buffer with length 10
        '''
        
        self.sum = 0.
        self.average = 0
        self.current_location = 0
        if type(data) is int:
            self.length = data
            self.data = [0]*self.length
        elif type(data) is list:
            self.length = len(data)
            self.data = [0]*self.length
            for item in data:
                self.update(item) # use existing method to add in and not repeat calcs

    def update(self,value):
        '''
        Add a value to the buffer
        '''
        self.sum -= self.data[self.current_location]
        self.data[self.current_location] = value
        self.sum += value
        
        self.advance_current_location()
        
        self.average = self.sum/self.length
    
    @property
    def value(self):
        '''
        The value at current_location
        '''
        return self.data[self.current_location]

    def advance_current_location(self):
        if self.current_location < self.length-1:
            self.current_location += 1
        else:
            self.current_location = 0

    def next(self):
        '''
        return the value at the current location and advance the current location
        '''
        v = self.value
        self.advance_current_location()
        return v

    def __len__(self):
        return self.length