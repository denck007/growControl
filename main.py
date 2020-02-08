'''
Simple grow controller
All values are hardcoded in to the files

Will read ph, temp, humidity and save values to individual files
Will control ph using 2 pumps
'''
import time

from growControl import Sensor_ph, Controller_ph_Pump, Sensor_humidity_temp, Controllable_Pump

if __name__ == "__main__":

    ph_min = 5.9
    ph_max = 6.1
    verbose = False
    sensor_ph = Sensor_ph(output_file="tmp_output_files/ph_{:.0f}.csv".format(time.time()),
                    read_every=10.0,
                    #csv="test/test_inputs/sensor_ph_sinewave01_voltage.csv",
                    calibrate_on_startup=True,
                    verbose=verbose)

    pump_up = Controllable_Pump(27,verbose=verbose)
    pump_down = Controllable_Pump(17,verbose=verbose)
    controller = Controller_ph_Pump(sensor_ph,
                                    pump_up,
                                    pump_down,
                                    output_file="tmp_output_files/Controller_ph_Pump_{:.0f}.csv".format(time.time()),
                                    ml_per_s=5.0, # ml/sec
                                    dispense_volume=1.0, # ml
                                    control_every=10*60,
                                    warmup_time=5.*60,
                                    verbose=verbose)
    
    sensor_ht = Sensor_humidity_temp(output_file_temp="tmp_output_files/temp_{:.0f}.csv".format(time.time()),
                                output_file_humidity="tmp_output_files/humidity_{:.0f}.csv".format(time.time()),
                                read_every=10.0,
                                average_factor_temp=0.9,
                                average_factor_humidity=0.9,
                                #csv="test/test_inputs/sensor_humidity_temp_input.csv",
                                verbose=verbose)
    run_time_seconds = 12*60*60
    end_time = time.time() + run_time_seconds
    while time.time() < end_time:
        sensor_ht()
        sensor_ph()
        controller()
        time.sleep(1)
    print("Completed run with total runtime of {:.1f}s!".format(run_time_seconds))
