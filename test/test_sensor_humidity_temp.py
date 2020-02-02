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
            tmp_file_temp = tempfile.mkstemp(suffix=".csv")
            tmp_file_humidity = tempfile.mkstemp(suffix=".csv")
            th = Sensor_humidity_temp(output_file_temp=tmp_file_temp[1],
                                        output_file_humidity=tmp_file_humidity[1],
                                        read_every=.15, # between loop_time and 2*loop_time
                                        average_factor_temp=0.9,
                                        average_factor_humidity=0.8,
                                        csv="test/test_inputs/sensor_humidity_temp_input.csv",
                                        verbose=False)
            
            loop_time = .1
            start_time = time.time()
            for ii in range(11):
                th()
                loop_end = time.time()
                time.sleep(start_time+(ii+1)*loop_time - loop_end)
            
            # verify the temperature data
            with open(tmp_file_temp[1],'r') as fp:
                data = fp.readlines()
            with open("test/test_inputs/sensor_temp_output_correct.csv",'r') as fp:
                data_correct = fp.readlines()
            self.assertEqual(data[0],data_correct[0])
            for line,line_correct in zip(data[1:],data_correct[1:]):
                t,_,_,raw,ma = line.strip("\n").split(",")
                t_c,_,_,raw_c,ma_c = line_correct.strip("\n").split(",")
                self.assertFloatsClose(float(t),float(t_c)+start_time,eps=.005)
                if raw_c == "None":
                    self.assertEqual(raw,raw_c)
                else:
                    self.assertFloatsClose(float(raw),float(raw_c))
                self.assertFloatsClose(float(ma),float(ma_c))

            # Verify the  humidity data
            with open(tmp_file_humidity[1],'r') as fp:
                data = fp.readlines()
            with open("test/test_inputs/sensor_humidity_output_correct.csv",'r') as fp:
                data_correct = fp.readlines()
            self.assertEqual(data[0],data_correct[0])
            for line,line_correct in zip(data[1:],data_correct[1:]):
                t,_,_,raw,ma = line.strip("\n").split(",")
                t_c,_,_,raw_c,ma_c = line_correct.strip("\n").split(",")
                self.assertFloatsClose(float(t),float(t_c)+start_time,eps=.005)
                if raw_c == "None":
                    self.assertEqual(raw,raw_c)
                else:
                    self.assertFloatsClose(float(raw),float(raw_c))
                self.assertFloatsClose(float(ma),float(ma_c))


            

        finally:
            os.remove(tmp_file_temp[1])
            os.remove(tmp_file_humidity[1])