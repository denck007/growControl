from unittest import TestCase
import tempfile
import os
import sys
import time

from growControl import Controller_ph_Pump, Sensor_ph, Controllable_Pump

class test_Controller_ph_Pump(TestCase):
    '''
    Test cases for the Controller_ph_Pump class
    '''

    def assertFloatsClose(self,a,b,eps=1e-6):
        '''
        Asserts that a and b are within eps of eachother
        '''
        delta = abs(a-b)
        self.assertTrue(delta < eps,msg="Floats {} and {} are not within {} of eachother.".format(a,b,eps))

    def test_Controller_ph_Pump(self):
        '''
        Verifies:
            * dispense_time is correct
            * Output time in csv is correct
            * Output ph_<up/down>_<volume/time> values in csv are correct
            * control_every is obeyed
            * warmup_time is obeyed
            * headers are correct
            '''
        try:
            tmp_file_sensor_ph = tempfile.gettempdir()
            s = Sensor_ph(output_file_path=tmp_file_sensor_ph,
                            output_file_base="sensor_ph",
                            average_factor=0., # this will make no averaging happen
                            read_every=0.0, # read every chance it gets
                            csv="test/test_inputs/controller_ph_pump_test_ph_input_file.csv",
                            calibration_file="test/test_inputs/sensor_ph_calibration_mock.json",
                            calibrate_on_startup=False)
            tmp_file_sensor_ph = s.output_file
            pump_up = Controllable_Pump(gpio_pin=None)
            pump_down = Controllable_Pump(gpio_pin=None)

            tmp_file_controller = tempfile.mkstemp(suffix=".csv")
            controller = Controller_ph_Pump(s,
                                            pump_up,
                                            pump_down,
                                            output_file=tmp_file_controller[1].format(time.time()),
                                            ph_min=5.8,
                                            ph_max=6.2,
                                            ml_per_s=5.0, # ml/sec
                                            dispense_volume=0.3, # ml
                                            control_every=0.15,
                                            warmup_time=.25)
            self.assertFloatsClose(controller.dispense_time,0.06) # check dispense_time is correct


            # To ensure this works across multiple computers, need to ensure
            #   that the loop time is consistent. The spacings allow for 0.05s of error,
            #   which should be plenty on any platform. 
            expected_loop_time = 0.1
            start_time = time.time() # used to test the timings in the output file
            for ii in range(10):
                s()
                controller()
                loop_end = time.time()
                time.sleep((start_time+(ii+1)*expected_loop_time) - loop_end) # force a loop to take a specific amount of time

            # Get the output file that was just made
            with open(tmp_file_controller[1],'r') as fp:
                data = fp.readlines()
                header = data[0]
                data = data[1:] # remove headers
                data = [line.strip("\n").split(",") for line in data] # get list of lists of values
            
            # Get the correct version of the object file
            with open("test/test_inputs/controller_ph_pump_output_file_correct.csv",'r') as fp:
                data_correct = fp.readlines()
                header_correct = data_correct[0]
                data_correct = data_correct[1:] # remove headers
                data_correct = [line.strip("\n").split(",") for line in data_correct] # get list of lists of values
            
            # check that the headers are correct
            self.assertEqual(header,header_correct)
            
            for line, line_correct in zip(data,data_correct):
                t, dt, dt_tz, down_t, down_v, up_t, up_v = line
                t_c, _, _, down_t_c, down_v_c, up_t_c, up_v_c = line_correct
                 # make sure the times are saved correctly
                 # The looping logic ensures that a new loop is started every expected_loop_time
                 # t_c is relative to start of the run
                self.assertFloatsClose(float(t),start_time+float(t_c),eps=.02)

                self.assertFloatsClose(float(down_t),float(down_t_c))
                self.assertFloatsClose(float(down_v),float(down_v_c))
                self.assertFloatsClose(float(up_t),float(up_t_c))
                self.assertFloatsClose(float(up_v),float(up_v_c))
        except:
            raise
        finally:
            os.remove(tmp_file_sensor_ph)
            os.remove(tmp_file_controller[1])
            pump_up.cleanup()
            pump_down.cleanup()

