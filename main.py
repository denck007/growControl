'''
Simple grow controller
All values are hardcoded in to the files

Will read ph, temp, humidity and save values to individual files
Will control ph using 2 pumps
'''
import time
import os
from growControl import Sensor_ph, Controller_ph_Pump, Sensor_humidity_temp, Controllable_Pump

if __name__ == "__main__":

    ph_min = 6.0
    ph_max = 6.2
    average_factor = 0.99
    verbose = True
    output_dir = "/home/pi/growControl_Data"
    #output_dir = "tmp_output_files"
    sensor_ph = Sensor_ph(output_file=os.path.join(output_dir,"ph_{:.0f}.csv".format(time.time())),
                    average_factor=average_factor,
                    read_every=10.0,
                    #csv="test/test_inputs/sensor_ph_sinewave01_voltage.csv",
                    calibrate_on_startup=True,
                    verbose=verbose)

    pump_up = Controllable_Pump(27,verbose=verbose)
    pump_down = Controllable_Pump(17,verbose=verbose)
    controller = Controller_ph_Pump(sensor_ph,
                                    pump_up,
                                    pump_down,
                                    ph_min=ph_min,
                                    ph_max=ph_max,
                                    output_file=os.path.join(output_dir,"Controller_ph_pump_{:.0f}.csv".format(time.time())),
                                    ml_per_s=1.75, # ml/sec, measured 3.5ml in 2 seconds on 20200213
                                    dispense_volume=3, # ml
                                    control_every=10*60,
                                    warmup_time=5.*60,
                                    verbose=verbose)
    
    sensor_ht_ambient = Sensor_humidity_temp(gpio_pin=18,
                                output_file_temp=os.path.join(output_dir,"temp_ambient_{:.0f}.csv".format(time.time())),
                                output_file_humidity=os.path.join(output_dir,"humidity_ambient_{:.0f}.csv".format(time.time())),
                                read_every=5.0,
                                average_factor_temp=0.9,
                                average_factor_humidity=0.9,
                                #csv="test/test_inputs/sensor_humidity_temp_input.csv",
                                verbose=verbose)

    sensor_ht_grow = Sensor_humidity_temp(gpio_pin=23,
                                output_file_temp= os.path.join(output_dir,"temp_grow_{:.0f}.csv".format(time.time())),
                                output_file_humidity=os.path.join(output_dir,"humidity_grow_{:.0f}.csv".format(time.time())),
                                read_every=5.0,
                                average_factor_temp=0.9,
                                average_factor_humidity=0.9,
                                verbose=verbose)

    run_time_seconds = 30
    end_time = time.time() + run_time_seconds
    #while time.time() < end_time:
    while True:
        print()
        sensor_ht_ambient()
        sensor_ht_grow()
        sensor_ph()
        controller()
        time.sleep(1)
    print("Completed run with total runtime of {:.1f}s!".format(run_time_seconds))
