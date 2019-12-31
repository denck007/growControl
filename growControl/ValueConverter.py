import logging

class ValueConverter:
    '''
    Converts a raw input into useable output
    '''
    def __init__(self,params,parent):
        '''
        Create an instance that can convert a raw value to a useable one
        '''
        self.name = "{}_valueconverter".format(parent.name)
        self.parent = parent
        self.logger=logging.getLogger("{}-{}".format(self.parent,self.name))
        self.logger.info("Initializing object")

        self.convert_type = params["convert_type"]
        
        if self.convert_type == "raw*scalar1+scalar2":
            self.scalar1 = params["scalar1"]
            self.scalar2 = params["scalar2"]
            self.conversion_function = self.raw_mul_add
        elif self.convert_type == "(raw+scalar1)*scalar2":
            self.scalar1 = params["scalar1"]
            self.scalar2 = params["scalar2"]
            self.conversion_function = self.raw_add_mul
        else:
            self.logger.critical("'convert_type' {} is not implemented - Program closing".format(self.convert_type))
            raise NotImplementedError("convert_type {} is not implemented for {} in growControl.ValueConverter".format(self.convert_type,self.name))

    def raw_mul_add(self,value):
        return value * self.scalar1 + self.scalar2

    def raw_add_mul(self,value):
        return (value + self.scalar1) * self.scalar2
    
    def __call__(self,value):
        return self.conversion_function(value)

