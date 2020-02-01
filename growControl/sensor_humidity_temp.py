
import os
import time
import datetime

class Sensor_humidity_temp:
    '''
    Read the temperature and humidity from a DHT11 or DHT22 sensor
    '''
    def __init__(self,csv=None):
        self.sensor_model = "DHT11"
        self.gpio_pin = -1
        self.retries = 15 # number of times to try and read the sensor
        self.retry_pause = 0.1 # Time to wait between retries

        self.average_factor_temp = 0.99 
        self.average_factor_humidity = 0.99 
        self.read_every = 1.0 # seconds, minimum time between readings

        self.output_file_temp = "/home/neil/growControl/output_files/temp_sensor.csv"
        self.output_file_humidity = "/home/neil/growControl/output_files/humidity_sensor.csv"
        os.makedirs(os.path.dirname(self.output_file_temp),exist_ok=True)
        os.makedirs(os.path.dirname(self.output_file_humidity),exist_ok=True)
        with open(self.output_file_temp,'a') as fp:
            fp.write("time,temperature_raw,temperature_average\n")   
        with open(self.output_file_humidity,'a') as fp:
            fp.write("time,relative_humidity_raw,relative_humidity_average\n")   

        if csv is None:
            self._initialize_sensor()
        else: # debugging
            self._initialize_sensor()

        self.temp = 20 # initialize to 20 degrees C
        self.humidity = 50 # initialize to 50% relative humidity

        self.last_reading_temp = time.time() - self.read_every - 1 # make it so imediatly the data is out of date to force reading
        self.last_reading_humidity = time.time() - self.read_every - 1 # make it so imediatly the data is out of date to force reading

    def _next_csv_value(self):
        '''
        Return the next value from a csv
        This lets us test without needing the sensor hooked up
        '''
        value = self.csv_data[self.csv_current_position]
        self.csv_current_position += 1
        return value

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
        self._read_sensor = self._next_csv_value

    def _initialize_sensor(self):
        '''
        Initialize the interface for the sensor
        '''
        import Adafruit_DHT

        if self.sensor_model == "DHT11":
            self._sensor = Adafruit_DHT.DHT11
        elif self.sensor_model == "DHT22":
            self._sensor = Adafruit_DHT.DHT22
        elif self.sensor_model == "AM2302":
            self._sensor = Adafruit_DHT.AM2302
        else:
            raise ValueError("Invalid sensor_model {}. Expected DHT11, DHT22, or AM2302".format(self.sensor_model))
            
        self._read_sensor = self._read_DHT

    def _read_DHT(self):
        '''
        Attempt to read the humidity and temp
        Return (humidity,temp) values in %RH and degrees C
            If it fails to read then returns (None,None)
        '''
        humidity,temp = Adafruit_DHT.read_retry(self._sensor,
                                        self.gpio_pin,
                                        retries=self.retries,
                                        delay_seconds=self.retry_pause)
        return (humidity,temp)

    def __call__(self):
        '''
        Reads the sensor
        '''
        
        current_time = time.time()
        # check to the see if the oldest reading is out of date
        if current_time - self.read_every < min(self.last_reading_temp,self.last_reading_humidity):
            return

        humidity,temp = self._read_sensor()

        if humidity is not None:
            self.humidity = self.humidity * self.average_factor_humidity + humidity * (1-self.average_factor_humidity)
            self.last_reading_humidity = current_time
        if temp is not None:
            self.temp = self.temp * self.average_factor_temp + temp * (1-self.average_factor_temp)
            self.last_reading_temp = current_time

        output = "{},{},{},".format(time.time(),datetime.datetime.now(),datetime.datetime.now().astimezone())
        output += "{},{}\n".format(humidity,self.humidity)
        with open(self.output_file_humidity,'a') as fp:
            fp.write(output)
        output = "{},{},{},".format(time.time(),datetime.datetime.now(),datetime.datetime.now().astimezone())
        output += "{},{}\n".format(temp,self.temp)
        with open(self.output_file_temp,'a') as fp:
            fp.write(output)
        
        print("{:.4f} Humidity: {} {}".format(time.time(),humidity,self.humidity))
        print("{:.4f} Temp: {} {}".format(time.time(),temp,self.temp))


if __name__ == "__main__":
    
    th = Sensor_humidity_temp(csv="/home/neil/growControl/testing_input_files/humidity_temp.csv")

    for ii in range(10):
        print()
        th()
        time.sleep(.5)
