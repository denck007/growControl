from unittest import TestCase
import tempfile
import os
import sys
import time

from growControl import Sensor_ph

class test_Sensor_ph(TestCase):
    '''
    Test cases for the Sensor_ph class
    '''

    def assertFloatsClose(self,a,b,eps=1e-6):
        '''
        Asserts that a and b are within eps of eachother
        '''
        delta = abs(a-b)
        self.assertTrue(delta < eps,msg="Floats {} and {} are not within {} of eachother.".format(a,b,eps))

    def test_simple_init(self):
        '''
        Verify that the basic initialization code works
        Verifies the moving averge code works
        '''
        
        try:
            tmp_file = tempfile.mkstemp(suffix=".csv")
            s = Sensor_ph(output_file=tmp_file[1],csv="test/test_inputs/sensor_ph_sinewave01_voltage.csv",verbose=False)
            s.average_factor = 0.9 # make sure that nothing has changed internal
            s.read_every = 0. #have to override values
            s.last_reading = 0. # reset to we dont miss the first values

            # load in the solution files for voltage and ph, both the raw and moving average versions
            with open("test/test_inputs/sensor_ph_sinewave01_voltage_ma0.9.csv",'r') as fp:
                data = fp.readlines()
            voltage_ma_correct = [float(item.strip("\n")) for item in data]
            with open("test/test_inputs/sensor_ph_sinewave01_voltage.csv",'r') as fp:
                data = fp.readlines()
            voltage_raw_correct = [float(item.strip("\n")) for item in data]

            with open("test/test_inputs/sensor_ph_sinewave01_ph_ma0.9.csv",'r') as fp:
                data = fp.readlines()
            ph_ma_correct = [float(item.strip("\n")) for item in data]
            with open("test/test_inputs/sensor_ph_sinewave01_ph.csv",'r') as fp:
                data = fp.readlines()
            ph_raw_correct = [float(item.strip("\n")) for item in data]
            
            # Test that the moving average is correct every step of the way
            for v,ph in zip(voltage_ma_correct,ph_ma_correct):
                s()
                self.assertFloatsClose(s.voltage_avg,v)
                self.assertFloatsClose(s.ph_avg,ph)
            
            # now validate the result in the output file is correct
            with open(tmp_file[1],'r') as fp:
                data = fp.readlines()
                data = data[1:] # skip headers
            
            # Go through the output file and make sure all the data is correct
            #fp.write("time,datetime,datetime_timezone,voltage_raw,voltage_avg,ph_raw,ph_avg\n")
            for line, v_ma_c, v_raw_c, ph_ma_c, ph_raw_c in zip(data, voltage_ma_correct, voltage_raw_correct, ph_ma_correct, ph_raw_correct):
                t, dt, dt_tz, v_raw, v_avg, ph_raw, ph_avg = line.strip("\n").split(",")
                self.assertFloatsClose(float(t),time.time(),eps=3.) # check that the time is within 3 seconds of now

                self.assertFloatsClose(float(v_raw),  float(v_raw_c))
                self.assertFloatsClose(float(v_avg),  float(v_ma_c))
                self.assertFloatsClose(float(ph_raw), float(ph_raw_c))
                self.assertFloatsClose(float(ph_avg), float(ph_ma_c))
        except:
            raise
        finally:
            os.remove(tmp_file[1])