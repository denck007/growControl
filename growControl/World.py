
import json
import time

from growControl import Environments
from growControl import Sensors
from growControl import Controls

class World:
    '''
    The World object holds all of the references to all of the created GrowObjects. It is where they are all created, where sensors are triggered to be read, controls activated from, and where data is saved.
    '''
    def __init__(self,config):
        '''
        '''
        # Initialize an empty dict to hold data in as needed
        # Note that this dict will be emptied each time the data is saved
        # This is a dict of dicts. The keys of self.data are the sensor names. 
        self.data = {}

        # Setup how data is saved. This is controlled by the output_type value in config
        if config["output_type"] == "csv":
            self.save_data = self._save_data_csv
            self.csv_name = config["csv_name"]
            self.csv_name = self.csv_name.replace(".csv","") # strip of extension if given
        elif config["output_type"] == "influxdb":
            self.save_data = self._save_data_influxdb
            # All the influxdb setup should go here
        else:
            raise TypeError("{} is not a defined value for config['output_type'] in World.__init__()".format(config["output_type"]))

        self.main_loop_min_time = config["main_loop_min_time"]
        self.last_loop = 0.0

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
            children[child]["world"] = self
            child_type = children[child]["type"]
            child_name = children[child]["name"]

            if child_type in ImplemetedGrowObjects:
                result[child_name] = ImplemetedGrowObjects[child_type](children[child])
            else:
                raise NotImplementedError("{} is not implemented or is has not been added to the corresponding *.Implemented dictionary")
            
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
        Update self.data with current values. self.data is a dict of dicts. The keys of
            self.data are the growObjects name
        '''
        # get all of the children's data
        for key in self.growObjects:
            data = self.growObjects[key].report_data()
            if data is not None:            
                self.data.update(data)

        # Save all the data to disk. The save_data() method is assigned in __init__()
        self.save_data()

        # Now reset so that new controls are writing to the empty dict
        self.data = {}
        return None

    def _save_data_csv(self):
        '''
        The function is assigned to self.save_data if config["output_type"] == "csv"
        It is called each time self.report_data() is called and will save the data to
            self.csv_name which is set by config["csv_name"]
        Each item in the dict self.data will be saved to its own file based on csv_name
        '''
        for key in self.data:
            if key is None:
                continue
            fname = "{}_{}.csv".format(self.csv_name,key)
            line = ""
            for item in self.data[key]:
                if line != "":
                    line += ","
                line += "{}".format(self.data[key][item])
            line += "\n"
            with open(fname,'a') as f:
                f.write(line)

    def _save_data_influxdb(self):
        '''
        
        '''
        raise NotImplementedError("world._save_data_influxdb")

    def pause_main_loop(self):
        '''
        sleep until at least self.main_loop_min_time has passes since last loop
        '''
        time_since_last = time.time()-self.last_loop
        #print("\tSleepTime: {:.5f} ".format(self.main_loop_min_time - time_since_last))
        delta_to_min = max(self.main_loop_min_time - time_since_last,0)
        time.sleep(delta_to_min)
        self.last_loop = time.time()


