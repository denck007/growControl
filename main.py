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

    sensor_ph = Sensor_ph(output_file="tmp_output_files/ph_{:.0f}.csv".format(time.time()),
                    read_every=1.0,
                    csv="test/test_inputs/sensor_ph_sinewave01_voltage.csv",
                    verbose=True)

    pump_up = Controllable_Pump(-1,verbose=True)
    pump_down = Controllable_Pump(-2,verbose=True)
    controller = Controller_ph_Pump(sensor_ph,
                                    pump_up,
                                    pump_down,
                                    output_file="tmp_output_files/Controller_ph_Pump_{:.0f}.csv".format(time.time()),
                                    ml_per_s=5.0, # ml/sec
                                    dispense_volume=1.0, # ml
                                    control_every=2,
                                    warmup_time=5.,
                                    verbose=True)
    
    sensor_ht = Sensor_humidity_temp(output_file_temp="tmp_output_files/temp_{:.0f}".format(time.time()),
                                output_file_humidity="tmp_output_files/humidity_{:.0f}".format(time.time()),
                                read_every=1.0,
                                average_factor_temp=0.9,
                                average_factor_humidity=0.9,
                                csv="test/test_inputs/sensor_humidity_temp_input.csv",
                                verbose=True)

    for ii in range(10):
        print()
        sensor_ht()
        sensor_ph()
        controller()
        time.sleep(.5)