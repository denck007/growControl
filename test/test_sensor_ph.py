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
            s = Sensor_ph(output_file=tmp_file[1],
                            average_factor=0.9,
                            read_every=0.15,
                            csv="test/test_inputs/sensor_ph_input.csv",
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
