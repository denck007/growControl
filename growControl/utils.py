#from growControl import Environments as Environments
#from growControl import Sensors as Sensors
#from growControl import Controls as Controls

class CircularBuffer(object):
    '''

    '''

    def __init__(self,data,outlier_rejection_value=None):
        '''
        If data is an integer, create a buffer with length data
        If data is a list, create a buffer with length len(data) populated with values from data

	If outlier_rejection_value is not None, then reject any new value that is more than outlier_rejection_value*100% from the current average. Note that if the buffer makes it all the way through the circle without updating then it will disable outlier rejection for 1 full round.

        '''
        self.outlier_rejection_value = outlier_rejection_value
        self.sum = 0.
        self.average = 0
        self.current_location = 0
        self.location_last_update = 0
        self.consecutive_skips = 0
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
        self.advance_current_location()
        if self.outlier_rejection_value is not None:
            # test if the value is outlier
            if abs((self.average-value)/self.average) > self.outlier_rejection_value:
                # is outlier
                if self.consecutive_skips < self.length:
                    # Has Not made it all the way around yet, so do not update
                    # Do this by just copying the existing value forward
                    value = self.value
                    self.consecutive_skips += 1
                    
                


        self.sum -= self.data[self.current_location]
        self.data[self.current_location] = value
        self.sum += value
        
        self.average = self.sum/self.length
        #d = ""
        #for v in self.data:
        #   d += " {:>4.2f}".format(v)
        #d += "   {:>6.3f}".format(self.average)
        #print(d)
    
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
