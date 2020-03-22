'''
Simple grow controller
All values are hardcoded in to the files

Will read ph, temp, humidity and save values to individual files
Will control ph using 2 pumps
'''
import time
import datetime
import os
from growControl import Sensor_ph, Controller_ph_Pump, Sensor_humidity_temp, Controllable_Pump

from blessed import Terminal

def sensor_box(top,left,width,name,current,average):
    data = term.move_xy(left,top)
    data += term.on_green(name + " "*(width-len(name)))
    current_value = "{:.3f}".format(current) if type(current) is float else "-"
    average_value = "{:.3f}".format(average) if type(average) is float else "-"
    data += term.move_xy(left+2,top+1) + "Current Value: " + current_value
    data += term.move_xy(left+2,top+2) + "Average Value: " + average_value
    return data

def controller_box(top,left,width,name,action,action_time,loop_time):
    data = term.move_xy(left,top)
    data += term.on_green(name + " "*(width-len(name)))
    action_time_value = "{:.0f}".format(time.time() - action_time) if type(action_time) is float else "-"
    loop_time_value = "{:.0f}".format(time.time() - loop_time) if type(loop_time) is float else "-"
    data += term.move_xy(left+2,top+1) + "Last Action: {}".format(action)
    data += term.move_xy(left+2,top+2) + "Time since last action: " + action_time_value + " s"
    data += term.move_xy(left+2,top+3) + "Time since last loop: " + loop_time_value + " s"
    return data

class MenuItem():
    '''
    Used to hold the menu items and what happens when they are called
    '''
    def __init__(self,name,key,function):
        '''
        name: The title of the command
        key: The key to be pressed, must be lower case, only 1 character is allowed

        '''
        self.name = name
        self.key = key.lower()[0]
        self.function = function
    
    def __call__(self):
        self.function()

    def __str__(self):

        s = term.on_darkolivegreen("{}: {}".format(self.name,self.key))

        return s

def pause():
    val = ""
    while val.lower() != "p":
        text = "System Paused! Press 'p' to resume"
        screen = term.move_xy(0,3)+ term.center(term.white_on_firebrick3(text))
        print(screen)
        val=term.inkey(timeout=None) # block until user presses a key
    return

def quit():
    val = ""
    while True:
        text = "Exit? Press 'y' to exit, 'n' to return to program"
        screen = term.move_xy(0,3) + term.center(term.white_on_firebrick3(text))
        print(screen)
        
        if val == "y":
            raise KeyboardInterrupt()
        elif val == "n":
            break
        val = term.inkey(timeout=None)
    return

def ph_calibration():

    calibration_data = {}
    calibration_time = 1 # seconds
    calibration_samples_per_second = 5

    def ph_calibration_menu():
        text = "Commands"
        screen = term.move_xy(term.width//2 - len(text)//2, term.height -3) + text
        screen += term.move_xy(0,term.height-2) + "Quit Calibration: q"

        return screen 

    while True:
        mode = "4ph"
        val = term.inkey(timeout=.5) # how often to update the screen 
        screen = term.clear()
        screen += term.move_xy(0,5) + term.center("pH Calibration Screen")
        
        if val == "q":
            break
        elif val == " ":
            calibration_data.update(sensor_ph._calibration_get_point_data(mode,duration=calibration_time,sps=calibration_samples_per_second))
            
            break
        screen += term.move_xy(0,10) + term.center(term.on_hotpink("Place probe in {} soluion and press <SPACE>".format(mode)))
        screen += ph_calibration_menu()
        print(screen)

    while True:
        mode = "7ph"
        val = term.inkey(timeout=.5) # how often to update the screen 
        screen = term.clear()
        screen += term.move_xy(0,5) + term.center("pH Calibration Screen")
        
        if val == "q":
            break
        elif val == " ":
            calibration_data.update(sensor_ph._calibration_get_point_data(mode,duration=calibration_time,sps=calibration_samples_per_second))
            break
        screen += term.move_xy(0,11) + term.center(term.on_olivedrab3("Place probe in {} soluion and press <SPACE>".format(mode)))
        screen += ph_calibration_menu()
        print(screen)        

    calibration_data = sensor_ph._calibration_compute_line(calibration_data)

    while True:
        mode = "save"
        val = term.inkey(timeout=.5) # how often to update the screen 
        screen = term.clear()
        screen += term.move_xy(0,5) + term.center("pH Calibration Screen")
        
        if val == "q":
            break
        elif val == "s":
            calibration_file = sensor_ph._calibration_save_data(calibration_data)
            sensor_ph._load_calibration_params(calibration_file=calibration_file)
            break

        screen += term.move_xy(0,10) + term.center("Determined the equation is: ph = {:.3f}*voltage + {:.3f}".format(calibration_data["m"],calibration_data["b"]))
        screen += term.move_xy(0,11) + term.center("         Ideal equation is: ph = {:.3f}*voltage + {:.3f}".format(-.057,7.0))

        screen += term.move_xy(0,13) + term.center("Average value for 4ph: {:.3f} volts, ideal is 0.057 volts".format(calibration_data["4ph_mean"]))
        screen += term.move_xy(0,14) + term.center("Average value for 7ph: {:.3f} volts, ideal is 0.000 volts".format(calibration_data["7ph_mean"]))
        screen += term.move_xy(0,16) + term.center(term.on_darkolivegreen("Press 's' to Save, or press 'q' to quit"))
        screen += ph_calibration_menu()
        print(screen)
        

class MenuItems():
    '''
    Hold onto all the menu items
    '''
    def __init__(self):
        self.items = []

    def addItem(self,item):
        self.items.append(item)
    
    def __iter__(self):
        self.iter_idx = 0
        return self

    def __next__(self):
        if self.iter_idx < len(self.items):
            item = self.items[self.iter_idx]
            self.iter_idx += 1
            return item
        else:
            raise StopIteration

    def __str__(self):
        n_cols = 3
        n_rows = len(self.items)//n_cols + 1
        col_width = term.width//n_cols

        title = "Commands"
        s = term.move_xy(term.width//2-len(title)//2, term.height-n_rows-1) + term.on_darkolivegreen(title)
        for idx, item in enumerate(self.items):
            x = idx%n_cols * col_width
            y = term.height - n_rows + idx//n_cols
            s += term.move_xy(x,y) + str(item)
                
        return s
   
if __name__ == "__main__":

    top = 5
    left = 2
    rows_per_device = 5
    cols_per_device = 38
    col_padding = 2

    ph_min = 6.0
    ph_max = 6.2
    average_factor = 0.99
    verbose = False
    output_dir = "/home/neil/growControl_Data"

    sensor_ph = Sensor_ph(output_file_path=output_dir,
                            output_file_base="sensor_ph_bin1",
                            average_factor=average_factor,
                            read_every=1.0,
                            csv="test/test_inputs/sensor_ph_sinewave01_voltage.csv",
                            #calibrate_on_startup=True,
                            calibration_file="test/test_inputs/sensor_ph_calibration_mock.json",
                            calibrate_on_startup=False,
                            verbose=verbose)

    pump_up = Controllable_Pump(None,verbose=verbose)
    pump_down = Controllable_Pump(None,verbose=verbose)
    controller = Controller_ph_Pump(sensor_ph,
                                    pump_up,
                                    pump_down,
                                    ph_min=ph_min,
                                    ph_max=ph_max,
                                    output_file_path=output_dir,
                                    output_file_base="controller_ph_pump",
                                    ml_per_s=1.75, # ml/sec, measured 3.5ml in 2 seconds on 20200213
                                    dispense_volume=3, # ml
                                    control_every=10*60,
                                    warmup_time=5.*60,
                                    verbose=verbose)
    
    sensor_ht_ambient = Sensor_humidity_temp(output_file_path=output_dir,
                                                output_file_base="humidity_temp_ambient",
                                                gpio_pin=None,
                                                read_every=5.0,
                                                average_factor_temp=0.99,
                                                average_factor_humidity=0.99,
                                                csv="test/test_inputs/sensor_humidity_temp_input.csv",
                                                verbose=False)
    
    sensor_ht_grow = Sensor_humidity_temp(output_file_path=output_dir,
                                                output_file_base="humidity_temp_grow",
                                                gpio_pin=None,
                                                csv="test/test_inputs/sensor_humidity_temp_input.csv",
                                                read_every=5.0,
                                                average_factor_temp=0.99,
                                                average_factor_humidity=0.99,
                                                verbose=verbose)

    start_dt = datetime.datetime.now()
    start_dt_string = start_dt.strftime("%m-%d %H:%M")

    term = Terminal()
    with term.cbreak(), term.hidden_cursor(), term.fullscreen():

        menuItems = MenuItems()
        menuItems.addItem(MenuItem(name="Quit",key="q",function=quit))
        menuItems.addItem(MenuItem(name="Pause",key="p",function=pause))
        menuItems.addItem(MenuItem(name="Calibrate pH",key="c",function=ph_calibration))

        try:
            while True:
                sensor_ph()
                sensor_ht_ambient()
                controller()

                val = term.inkey(timeout=.5) # how often to update the screen 
                
                for item in menuItems:
                    if val.lower() == item.key:
                        item()

                screen = term.clear

                # ph sensor
                sensor = sensor_box(top=top,
                                    left=left,
                                    width=cols_per_device,
                                    name="pH Sensor",
                                    current=sensor_ph.ph_raw,
                                    average=sensor_ph.ph_avg)
                screen += sensor
                #name,action,action_time,loop_time)
                sensor = controller_box(top=top,
                                        left=left + col_padding + cols_per_device,
                                        width=cols_per_device,
                                        name="pH Controller",
                                        action=controller.last_action,
                                        action_time=controller.last_action_time,
                                        loop_time=controller.last_loop_time)
                screen += sensor

                sensor = sensor_box(top=top+rows_per_device,
                                    left=left,
                                    width=cols_per_device,
                                    name="Ambient Temperature Sensor",
                                    current=sensor_ht_ambient.temp_raw,
                                    average=sensor_ht_ambient.temp_avg)
                screen += sensor
                sensor = sensor_box(top=top+rows_per_device,
                                    left=left + col_padding + cols_per_device,
                                    width=cols_per_device,
                                    name="Ambient Humidity Sensor",
                                    current=sensor_ht_ambient.humidity_raw,
                                    average=sensor_ht_ambient.humidity_avg)
                screen += sensor
                
                sensor = sensor_box(top=top+2*rows_per_device,
                                    left=left,
                                    width=cols_per_device,
                                    name="Chamber Temperature Sensor",
                                    current=sensor_ht_ambient.temp_raw,
                                    average=sensor_ht_ambient.temp_avg)
                screen += sensor
                sensor = sensor_box(top=top+2*rows_per_device,
                                    left=left + col_padding + cols_per_device,
                                    width=cols_per_device,
                                    name="Chamber Humidity Sensor",
                                    current=sensor_ht_ambient.humidity_raw,
                                    average=sensor_ht_ambient.humidity_avg)
                screen += sensor

                # Handle the titles and menu
                uptime = datetime.datetime.now() - start_dt
                uptime = str(uptime).split(".")[0] # get the delta, strip off decimal seconds
                title = term.on_darkolivegreen("Grow Control")
                screen += term.move_xy(0,1) + term.center(title)
                title = "Started {} Uptime {}".format(start_dt_string,uptime)
                screen += term.move_xy(0,2) + term.center(title)

                screen += str(menuItems)
                print(screen)
        except KeyboardInterrupt:
            pass