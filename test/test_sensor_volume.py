from unittest import TestCase
import tempfile
import os
import sys
import time

from growControl import Sensor_volume

class test_Sensor_volume(TestCase):
    '''
    Test cases for the Sensor_volume class
    '''

    def assertFloatsClose(self,a,b,eps=1e-6):
        '''
        Asserts that a and b are within eps of eachother
        '''
        delta = abs(a-b)
        self.assertTrue(delta < eps,msg="Floats {} and {} are not within {} of eachother.".format(a,b,eps))

    def test_sensor_volume_csv(self):
        '''
        Verifies:
            * Recorded time is correct
            * Recorded values (raw and average) are correct
            * A reading of None does not terminate the run
            * Moving average handles reading None
            * read_every works properly
        '''
        
        try:
            tmp_file = tempfile.gettempdir()
            s = Sensor_volume(output_file_path=tmp_file,
                            output_file_base="sensor_volume",
                            trigger_pin=None,
                            echo_pin=None,
                            iterations_per_reading=2,
                            average_factor=0.8,
                            read_every=0.15,
                            csv="test/test_inputs/sensor_volume_test_input.csv",
                            calibration_file="test/test_inputs/sensor_volume_calibration_mock.json",
                            calibrate_on_startup=False,
                            verbose=False)
            tmp_file = s.output_file # update with the filename the object creates

            loop_time = 0.1
            start_time = time.time()
            for ii in range(10):
                s()
                loop_end = time.time()
                time.sleep(start_time+(ii+1)*loop_time - loop_end)

            with open(tmp_file,'r') as fp:
                data = fp.readlines()
            with open("test/test_inputs/sensor_volume_test_output_correct.csv",'r') as fp:
                data_correct = fp.readlines()
            # Verify header is correct
            self.assertEqual(data[0],data_correct[0])
            for line,line_correct in zip(data[1:],data_correct[1:]):
                t,_,time_raw,time_avg,volume_raw,volume_avg = line.strip("\n").split(",")
                t_c,_,time_raw_c,time_avg_c,volume_raw_c,volume_avg_c = line_correct.strip("\n").split(",")

                self.assertFloatsClose(float(t),float(t_c)+start_time,eps=.02) # Not really possible to gaurentee timesteps on order of 1ms
                self.assertFloatsClose(float(time_avg),float(time_avg_c))
                self.assertFloatsClose(float(volume_avg),float(volume_avg_c),1e-4)

                if time_raw == "None": # check case where a bad raw value exists
                    self.assertEqual(time_raw,time_raw_c)
                else:
                    self.assertFloatsClose(float(time_raw),float(time_raw_c))

                if volume_raw == "None": # check case where a bad raw value exists
                    self.assertEqual(volume_raw,volume_raw_c)
                else:
                    self.assertFloatsClose(float(volume_raw),float(volume_raw_c),1e-3)
        except:
            raise
        finally:
            os.remove(tmp_file)

    def test_sensor_ph_real_sensor(self):
        '''
        Verifies:
            * Recorded time is correct
        '''
        machine = os.uname().machine
        if not (machine == "armv6l" or machine == "armv7l") :
            print("test_sensor_ph_real_readings only works on the raspberrypi!")
            return
        
        try:
            tmp_file = tempfile.gettempdir()
            s = Sensor_volume(output_file_path=tmp_file,
                            output_file_base="sensor_volume",
                            trigger_pin=23,
                            echo_pin=24,
                            iterations_per_reading=2,
                            average_factor=0.8,
                            read_every=0.001,
                            csv=None,
                            calibration_file="test/test_inputs/sensor_volume_calibration_mock.json",
                            calibrate_on_startup=False,
                            verbose=False)
            tmp_file = s.output_file # update with the filename the object creates

            start_time = time.time()
            for ii in range(2):
                s()
                time.sleep(.01)
            with open(tmp_file,'r') as fp:
                data = fp.readlines()
            with open("test/test_inputs/sensor_volume_test_output_correct.csv",'r') as fp:
                header_correct = fp.readline()
            
            self.assertEqual(data[0],header_correct)
            none_counter_voltage = 0
            none_counter_ph = 0
            for line in data[1:]:
                t, dt_tz, time_raw, time_avg, volume_raw, volume_avg = line.strip("\n").split(",")
                if time_raw == "None":
                    none_counter_voltage +=1
                else: 
                    #If the items cannot be converted to float an error will be thrown
                    time_raw = float(time_raw)
                    time_avg = float(time_avg)
                    self.assertTrue(time_raw > 0.,msg="Raw pulse duration should be over 0.0s")
                    self.assertTrue(time_raw < 0.029,msg="Raw pulse duration should be under 0.029s (~5 meters)")
                    self.assertTrue(time_avg > 0.0,msg="Average pulse duration should be over 0.0s")
                    self.assertTrue(time_avg < 0.029,msg="Average pulse duration should be under 0.029s (~5 meters)")

                if volume_raw == "None":
                    none_counter +=1
                else: 
                    #If the items cannot be converted to float an error will be thrown
                    volume_raw = float(volume_raw)
                    volume_avg = float(volume_avg)
                    self.assertTrue(volume_raw > 0.,msg="Raw volume should be over 0.0, got {:}".format(volume_raw))
                    self.assertTrue(volume_raw < 15. ,msg="Raw volume should be under 15.0, got {:}".format(volume_raw))
                    self.assertTrue(volume_avg > 0. ,msg="Average volume should be over 0.0, got {:}".format(volume_avg))
                    self.assertTrue(volume_avg < 15,msg="Average volume should be under 15.0, got {:}".format(volume_avg))

            self.assertFalse(none_counter_voltage >= len(data)-2,msg="Output file must have at least 1 non-'None' value for voltage")
            self.assertFalse(none_counter_ph >= len(data)-2,msg="Output file must have at least 1 non-'None' value for ph")

        finally:
            os.remove(tmp_file)
