from unittest import TestCase
import tempfile
import os
import sys
import time

from growControl import Controller_Volume_Pump, Sensor_volume, Controllable_Pump

class test_Controller_Volume_Pump(TestCase):
    '''
    Test cases for the Controller_Volume_Pump class
    '''

    def assertFloatsClose(self,a,b,eps=1e-6):
        '''
        Asserts that a and b are within eps of eachother
        '''
        delta = abs(a-b)
        self.assertTrue(delta < eps,msg="Floats {} and {} are not within {} of eachother.".format(a,b,eps))

    def test_Controller_Volume_Pump(self):
        '''
        Verifies:
            * dispense_time is correct
            * Output time in csv is correct
            * Output dispensed_time and dispensed_volumevalues in csv are correct
            * control_every is obeyed
            * warmup_time is obeyed
            * headers are correct
            '''
        try:
            tmp_file_sensor_volume = tempfile.gettempdir()
            s = Sensor_volume(output_file_path=tmp_file_sensor_volume,
                            output_file_base="sensor_volume",
                            calibration_file="test/test_inputs/sensor_volume_calibration_mock.json",
                            calibrate_on_startup=False,
                            iterations_per_reading=1,
                            read_every=.099, # handle slight errors in loop time
                            average_factor=.8,
                            csv="test/test_inputs/controller_volume_pump_test_volume_input_file.csv",
                            verbose=False)
            tmp_file_sensor_volume = s.output_file
            pump = Controllable_Pump(gpio_pin=None)

            tmp_file_controller = tempfile.gettempdir()
            controller = Controller_Volume_Pump(s,
                                            pump,
                                            output_file_path=tmp_file_controller,
                                            output_file_base="controller_volume_pump",
                                            volume_min=7.,
                                            ml_per_s=5.0, # ml/sec
                                            dispense_volume=0.3, # ml
                                            control_every=0.15,
                                            warmup_time=.25)
            tmp_file_controller = controller.output_file

            self.assertFloatsClose(controller.dispense_time,0.06) # check dispense_time is correct


            # To ensure this works across multiple computers, need to ensure
            #   that the loop time is consistent. The spacings allow for 0.05s of error,
            #   which should be plenty on any platform. 
            expected_loop_time = 0.1
            start_time = time.time() # used to test the timings in the output file
            for ii in range(10):
                s()
                controller()
                print("{:.2f}: average: {:.3f}".format(ii*.1,s.volume_avg))
                loop_end = time.time()
                time.sleep((start_time+(ii+1)*expected_loop_time) - loop_end) # force a loop to take a specific amount of time

            # Get the output file that was just made
            with open(tmp_file_controller,'r') as fp:
                data = fp.readlines()
                header = data[0]
                data = data[1:] # remove headers
                data = [line.strip("\n").split(",") for line in data] # get list of lists of values
            
            # Get the correct version of the object file
            with open("test/test_inputs/controller_volume_pump_output_file_correct.csv",'r') as fp:
                data_correct = fp.readlines()
                header_correct = data_correct[0]
                data_correct = data_correct[1:] # remove headers
                data_correct = [line.strip("\n").split(",") for line in data_correct] # get list of lists of values

            # check that the headers are correct
            self.assertEqual(header,header_correct)
            
            for line, line_correct in zip(data,data_correct):
                t, dt_tz, dispense_time, dispense_volume = line
                t_c, _, dispense_time_c, dispense_volume_c = line_correct
                 # make sure the times are saved correctly
                 # The looping logic ensures that a new loop is started every expected_loop_time
                 # t_c is relative to start of the run
                self.assertFloatsClose(float(t),start_time+float(t_c),eps=.02)

                self.assertFloatsClose(float(dispense_time),float(dispense_time_c))
                self.assertFloatsClose(float(dispense_volume),float(dispense_volume_c))
        except:
            raise
        finally:
            os.remove(tmp_file_sensor_volume)
            os.remove(tmp_file_controller)
            pump.cleanup()

