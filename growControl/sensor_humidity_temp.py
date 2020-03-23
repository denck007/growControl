
import datetime
import os
import sys
import time

try:
    import Adafruit_DHT
except:
    print("In sensor_humidity_temp: Unable to import Adafruit_DHT" +\
           "\tWill only able to run in csv mode!")

class Sensor_humidity_temp:
    '''
    Read the temperature and humidity from a DHT11 or DHT22 sensor
    '''
    def __init__(self,
                gpio_pin,
                output_file_path,
                output_file_base,
                read_every=30.0,
                average_factor_temp=0.9,
                average_factor_humidity=0.9,
                csv=None,
                verbose=False):
        '''
        gpio_pin: The pin to read from
        output_file_path: Path to save the data to
        output_file_base_temp: start of the output file name. This will get the date appended to it
        output_file_base_humidity: start of the output file name. This will get the date appended to it

        read_every: Float, minimum seconds time between successful readings
        average_factor_temp: [Float,Float), How much emphasis is put on old vs new data. Higher value will do better with more noise, but it will lag more
            if the temperature changes quickly
        average_factor_humidity: [Float,Float), How much emphasis is put on old vs new data. Higher value will do better with more noise, but it will lag more
            if the humidity changes quickly
        csv: Path to file containting raw readings, used for debugging. Must have 2 values per row separated by a comma, first is humidity, second is temperature
            File must end with a new line, and not have excess blank rows.
        verbose: Output the reading whenever one is taken 
        '''

        self.output_file_path = output_file_path
        self.output_file_base = output_file_base
        os.makedirs(os.path.dirname(self.output_file_path),exist_ok=True)
        self.update_output_file_path()

        self.average_factor_temp = average_factor_temp
        self.average_factor_humidity = average_factor_humidity
        self.read_every = read_every # seconds, minimum time between readings

        self.verbose = verbose
        self.sensor_model = "DHT22"
        self.gpio_pin = gpio_pin
        self.retries = 15 # number of times to try and read the sensor
        self.retry_pause = 0.1 # Time to wait between retries
        
        if csv is None:
            self._initialize_sensor()
        else: # debugging
            self._initialize_csv(csv)

        self.temp_raw = None
        self.humidiy_raw = None
        self.temp_avg = 20. # initialize to 20 degrees C
        self.humidity_avg = 50. # initialize to 50% relative humidity

        self.last_reading_temp = time.time() - self.read_every - 1 # make it so imediatly the data is out of date to force reading
        self.last_reading_humidity = time.time() - self.read_every - 1 # make it so imediatly the data is out of date to force reading

    def update_output_file_path(self):
        '''
        Updates the property self.output_file
        Checks to see if the file <self.output_file_path> + <self.output_file_base> + <date in YYYY-MM-DD format> .csv
            If it does:
                do nothing
            If it does not exist:
                create it and initialize the header
        '''

        date = datetime.date.today().isoformat()
        self.output_file = os.path.join(self.output_file_path,"{}_{}.csv".format(self.output_file_base,date))
        if not os.path.isfile(self.output_file):
            with open(self.output_file,'a') as fp:
                fp.write("time,datetime_timezone,relative_humidity_raw,relative_humidity_average,temperature_raw,temperature_average\n")

    def _initialize_csv(self,csv):
        '''
        Read in all the data from the csv file, set up self to read from csv instead of sensor
        csv: path to valid csv file with mock readings
        '''
        with open(csv,'r') as fp:
            data = fp.readlines()
        self.csv_data = []
        for line in data:
            humidity,temp = line.strip().split(",")
            humidity = float(humidity) if humidity != 'None' else None
            temp = float(temp) if temp != 'None' else None
            self.csv_data.append((humidity,temp))
        self.csv_current_position = 0
        self._read = self._read_csv

    def _read_csv(self):
        '''
        Return the next value from a csv
        This lets us test without needing the sensor hooked up
        '''
        value = self.csv_data[self.csv_current_position]
        self.csv_current_position += 1
        return value

    def _initialize_sensor(self):
        '''
        Initialize the interface for the sensor
        '''
        if self.sensor_model == "DHT11":
            self._sensor = Adafruit_DHT.DHT11
        elif self.sensor_model == "DHT22":
            self._sensor = Adafruit_DHT.DHT22
        elif self.sensor_model == "AM2302":
            self._sensor = Adafruit_DHT.AM2302
        else:
            raise ValueError("Invalid sensor_model {}. Expected DHT11, DHT22, or AM2302".format(self.sensor_model))

        self._read = self._read_sensor

    def _read_sensor(self):
        '''
        Attempt to read the humidity and temp
        Return (humidity,temp) values in %RH and degrees C
            If it fails to read then returns (None,None)
        '''
        try:
            humidity,temp = Adafruit_DHT.read_retry(self._sensor,
                                            self.gpio_pin,
                                            retries=self.retries,
                                            delay_seconds=self.retry_pause)
        except:
            e = sys.exc_info()
            print("Exception thrown while reading humidity and temperature:")
            print("{}: {}".format(e[0],e[1]))
            humidity = None
            temp = None
        return (humidity,temp)

    def __call__(self):
        '''
        Reads the sensor
        '''

        current_time = time.time()
        # check to the see if the oldest reading is out of date
        if current_time - self.read_every < min(self.last_reading_temp,self.last_reading_humidity):
            return

        self.update_output_file_path() # Starts a new output file every day

        self.humidity_raw,self.temp_raw = self._read()

        if self.humidity_raw is not None:
            self.humidity_avg = self.humidity_avg * self.average_factor_humidity + self.humidity_raw * (1-self.average_factor_humidity)
            self.last_reading_humidity = current_time
        if self.temp_raw is not None:
            self.temp_avg = self.temp_avg * self.average_factor_temp + self.temp_raw * (1-self.average_factor_temp)
            self.last_reading_temp = current_time

        output = "{},{},".format(time.time(),datetime.datetime.now().astimezone())
        output += "{},{},".format(self.humidity_raw,self.humidity_avg)
        output += "{},{}\n".format(self.temp_raw,self.temp_avg)
        
        with open(self.output_file,'a') as fp:
            fp.write(output)

        if self.verbose:
            t = datetime.datetime.strftime(datetime.datetime.now(),"%m/%d %H:%M:%S")
            if self.humidity_raw is None:
                print("{} Humidity: Current: ---- Average: {:.1f}".format(t,self.humidity_avg))
            else:
                print("{} Humidity: Current: {:.1f} Average: {:.1f}".format(t,self.humidity_raw,self.humidity_avg))
            if self.temp_raw is None:
                print("{}     Temp: Current: ---- Average: {:.1f}".format(t,self.temp_avg))
            else:
                print("{}     Temp: Current: {:.1f} Average: {:.1f}".format(t,self.temp_raw,self.temp_avg))

if __name__ == "__main__":

    th_csv = Sensor_humidity_temp(output_file_path="tmp_output_files",
                                output_file_base="sensor_humidity_temp",
                                gpio_pin=None,
                                read_every=1.0,
                                average_factor_temp=0.9,
                                average_factor_humidity=0.8,
                                csv="test/test_inputs/sensor_humidity_temp_input.csv",
                                verbose=True)
    #th_sensor = Sensor_humidity_temp(output_file_temp="tmp_output_files/temp_{:.0f}.csv".format(time.time()),
    #                            output_file_humidity="tmp_output_files/humidity_{:.0f}.csv".format(time.time()),
    #                            read_every=2.0,
    #                            average_factor_temp=0.9,
    #                            average_factor_humidity=0.8,
    #                            csv=None,
    #                            verbose=True)

    for ii in range(10):
        print()
        th_csv()
        time.sleep(.5)
