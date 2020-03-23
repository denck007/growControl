from unittest import TestCase
import tempfile
import os
import sys
import time

from growControl import Sensor_humidity_temp

class test_Sensor_humidity_temp(TestCase):
    '''
    Test cases for the Controller_ph_Pump class
    '''

    def assertFloatsClose(self,a,b,eps=1e-6):
        '''
        Asserts that a and b are within eps of eachother
        '''
        delta = abs(a-b)
        self.assertTrue(delta < eps,msg="Floats {} and {} are not within {} of eachother.".format(a,b,eps))

    def test_Sensor_humidity_temp(self):
        '''
        Verify that:
            * Readings of None do not affect the output
            * Verify moving average is correct (and excludes Nones)
            * Verify that a None response in one of the items causes another attempt
                on the next iteration (ie it doesn't update last_reading)
        '''
        try:
            tmp_file = tempfile.gettempdir()
            th = Sensor_humidity_temp(output_file_path=tmp_file,
                                        output_file_base="humidity_and_temp",
                                        gpio_pin=None,
                                        read_every=.15, # between loop_time and 2*loop_time
                                        average_factor_temp=0.9,
                                        average_factor_humidity=0.8,
                                        csv="test/test_inputs/sensor_humidity_temp_input.csv",
                                        verbose=False)
            tmp_file = th.output_file

            loop_time = .1
            start_time = time.time()
            for ii in range(11):
                th()
                loop_end = time.time()
                time.sleep(start_time+(ii+1)*loop_time - loop_end)
            
            # verify the temperature data
            with open(tmp_file,'r') as fp:
                data = fp.readlines()
            with open("test/test_inputs/sensor_humidity_temp_output_correct.csv",'r') as fp:
                data_correct = fp.readlines()
            self.assertEqual(data[0],data_correct[0])
            for line,line_correct in zip(data[1:],data_correct[1:]):
                t,_,temp_raw,temp_ma, humidity_raw, humidity_ma = line.strip("\n").split(",")
                t_c,_,temp_raw_c,temp_ma_c, humidity_raw_c, humidity_ma_c = line_correct.strip("\n").split(",")

                self.assertFloatsClose(float(t),float(t_c)+start_time,eps=.02)
                if temp_raw_c == "None":
                    self.assertEqual(temp_raw,temp_raw_c)
                else:
                    self.assertFloatsClose(float(temp_raw),float(temp_raw_c))
                self.assertFloatsClose(float(temp_ma),float(temp_ma_c))

                if humidity_raw_c == "None":
                    self.assertEqual(humidity_raw,humidity_raw_c)
                else:
                    self.assertFloatsClose(float(humidity_raw),float(humidity_raw_c))
                self.assertFloatsClose(float(humidity_ma),float(humidity_ma_c))

        finally:
            os.remove(tmp_file)

    def test_sensor_humidity_temp_real_readings(self):
        '''
        Test that we can actually read from the sensor
        '''
        if os.uname().machine != "armv6l":
            print("test_sensor_humidity_temp_real_readings only works on the raspberrypi!")
            return
        try:
            tmp_file = tempfile.gettempdir()
            th = Sensor_humidity_temp(output_file_path=tmp_file,
                                        output_file_base="humidity_and_temp",
                                        gpio_pin=18,
                                        read_every=.15,
                                        average_factor_temp=0.9,
                                        average_factor_humidity=0.9,
                                        csv=None,
                                        verbose=False)
            tmp_file = th.output_file

            start_time = time.time()
            for ii in range(2):
                th()

            with open(tmp_file,'r') as fp:
                data = fp.readlines()
            with open("test/test_inputs/sensor_humidity_temp_output_correct.csv",'r') as fp:
                header_correct = fp.readline()
            
            self.assertEqual(data[0],header_correct)
            none_counter_temp = 0
            none_counter_humidity = 0
            for line in data[1:]:
                t, dt_tz, temp_raw, temp_avg, humidity_raw, humidity_avg = line.strip("\n").split(",")
                if temp_raw == "None":
                    none_counter_temp +=1
                else: 
                    #If the items cannot be converted to float an error will be thrown
                    temp_raw = float(temp_raw)
                    temp_avg = float(temp_avg)
                    self.assertTrue(temp_raw > 0.,msg="Raw temperature should be greater than 0C")
                    self.assertTrue(temp_raw < 40.,msg="Raw temperature should be less than 40C")
                    self.assertTrue(temp_avg > 0.,msg="Average temperature should be greater than 0C")
                    self.assertTrue(temp_avg < 40.,msg="Average temperature should be less than 40C")
            

                if humidity_raw == "None":
                    none_counter_humidity +=1
                else: 
                    #If the items cannot be converted to float an error will be thrown
                    humidity_raw = float(humidity_raw)
                    humidity_avg = float(humidity_avg)
                    self.assertTrue(humidity_raw > 0.,msg="Raw humidity should be greater than 0%")
                    self.assertTrue(humidity_raw < 100.,msg="Raw humidity should be less than 100%")
                    self.assertTrue(humidity_avg > 0.,msg="Average humidity should be greater than 0%")
                    self.assertTrue(humidity_avg < 100.,msg="Average humidity should be less than 100%")
            self.assertFalse(none_counter_temp >= len(data)-2,msg="Every reading in output file is 'None' for temperature")
            self.assertFalse(none_counter_humidity >= len(data)-2,msg="Every reading in output file is 'None' for humidity")

        finally:
            os.remove(tmp_file)
