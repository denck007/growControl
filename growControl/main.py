'''
Simple grow controller
All values are hardcoded in to the files

Will read ph, temp, humidity and save values to individual files
Will control ph using 2 pumps
'''
import time

from growControl import Sensor_ph
from growControl import Controller_ph_Pump
from growControl import Sensor_humidity_temp

if __name__ == "__main__":

    ph_min = 5.9
    ph_max = 6.1

    sensor_ph = Sensor_ph(output_file="tmp_output_files/ph_{:.0f}".format(time.time()),csv="/home/neil/growControl/testing_input_files/voltages.csv")
    controller_ph = Controller_ph_Pump(sensor_ph)
    sensor_ht = Sensor_humidity_temp(csv="/home/neil/growControl/testing_input_files/humidity_temp.csv")

    controller_ph.warmup_time = 0
    controller_ph.control_every = 2
    controller_ph.last_control = 0.

    for ii in range(10):
        #print()
        sensor_ht()
        sensor_ph()
        controller_ph()
        time.sleep(.5)