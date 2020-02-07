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

    def test_sensor_ph_csv(self):
        '''
        Verifies:
            * Recorded time is correct
            * Recorded values (raw and average) are correct
            * A reading of None does not terminate the run
            * Moving average handles reading None
            * read_every works properly
        '''
        
        try:
            tmp_file = tempfile.mkstemp(suffix=".csv")
            s = Sensor_ph(output_file=tmp_file[1],
                            average_factor=0.9,
                            read_every=0.15,
                            csv="test/test_inputs/sensor_ph_input.csv",
                            calibration_file="test/test_inputs/sensor_ph_calibration_mock.json",
                            verbose=False)

            loop_time = 0.1
            start_time = time.time()
            for ii in range(20):
                s()
                loop_end = time.time()
                time.sleep(start_time+(ii+1)*loop_time - loop_end)

            with open(tmp_file[1],'r') as fp:
                data = fp.readlines()
            with open("test/test_inputs/sensor_ph_output_correct.csv",'r') as fp:
                data_correct = fp.readlines()

            # Verify header is correct
            self.assertEqual(data[0],data_correct[0])

            for line,line_correct in zip(data[1:],data_correct[1:]):
                t,_,_,v_raw,v_avg,ph_raw,ph_avg = line.strip("\n").split(",")
                t_c,_,_,v_raw_c,v_avg_c,ph_raw_c,ph_avg_c = line_correct.strip("\n").split(",")

                self.assertFloatsClose(float(t),float(t_c)+start_time,eps=.02) # Not really possible to gaurentee timesteps on order of 1ms
                self.assertFloatsClose(float(v_avg),float(v_avg_c))
                self.assertFloatsClose(float(ph_avg),float(ph_avg_c))

                if v_raw == "None": # check case where a bad raw value exists
                    self.assertEqual(v_raw,v_raw_c)
                else:
                    self.assertFloatsClose(float(v_raw),float(v_raw_c))

                if ph_raw == "None": # check case where a bad raw value exists
                    self.assertEqual(ph_raw,ph_raw_c)
                else:
                    self.assertFloatsClose(float(ph_raw),float(ph_raw_c))
        except:
            raise
        finally:
            os.remove(tmp_file[1])

    def test_sensor_ph_real_sensor(self):
        '''
        Verifies:
            * Recorded time is correct
        '''
        if os.uname().machine != "armv6l":
            print("test_sensor_ph_real_readings only works on the raspberrypi!")
            return
        
        try:
            tmp_file = tempfile.mkstemp(suffix=".csv")
            s = Sensor_ph(output_file=tmp_file[1],
                            average_factor=0.9,
                            read_every=0.,
                            csv=None,
                            calibration_file="test/test_inputs/sensor_ph_calibration_mock.json",
                            verbose=False)

            start_time = time.time()
            for ii in range(2):
                s()
            with open(tmp_file[1],'r') as fp:
                data = fp.readlines()
            with open("test/test_inputs/sensor_ph_output_correct.csv",'r') as fp:
                header_correct = fp.readline()
            
            self.assertEqual(data[0],header_correct)
            none_counter_voltage = 0
            none_counter_ph = 0
            for line in data[1:]:
                t, dt, dt_tz, v_raw, v_avg, ph_raw, ph_avg = line.strip("\n").split(",")
                if v_raw == "None":
                    none_counter_voltage +=1
                else: 
                    #If the items cannot be converted to float an error will be thrown
                    v_raw = float(v_raw)
                    v_avg = float(v_avg)
                    self.assertTrue(v_raw > -0.2,msg="Raw voltage should be over -0.2v (~3.5ph)")
                    self.assertTrue(v_raw < 0.2,msg="Raw voltage should be under 0.2v (~10.5ph)")
                    self.assertTrue(v_avg > -0.2,msg="Average voltage should be over -0.2v (~3.5ph)")
                    self.assertTrue(v_avg < 0.2,msg="Average voltage should be under 0.2v (~10.5ph)")

                if ph_raw == "None":
                    none_counter +=1
                else: 
                    #If the items cannot be converted to float an error will be thrown
                    ph_raw = float(ph_raw)
                    ph_avg = float(ph_avg)
                    self.assertTrue(ph_raw > 3.5,msg="Raw ph should be over -0.2v (~3.5ph)")
                    self.assertTrue(ph_raw < 10.5,msg="Raw ph should be under 0.2v (~10.5ph)")
                    self.assertTrue(ph_avg > 3.5,msg="Average ph should be over 3.5ph")
                    self.assertTrue(ph_avg < 10.5,msg="Average ph should be under 10.5ph")

            self.assertFalse(none_counter_voltage >= len(data)-2,msg="Output file must have at least 1 non-'None' value for voltage")
            self.assertFalse(none_counter_ph >= len(data)-2,msg="Output file must have at least 1 non-'None' value for ph")



        finally:
            os.remove(tmp_file[1])

