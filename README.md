# growControl
This project is meant to be a general purpose monitoring and control tool for gardening systems. It is being developed for hydroponics but could be used for any type of gardening.

For a hydroponic Kratky system with 2 tanks under the same light that uses the system to control the lights and has automatic ph dosing, the setup would look like:
* World 
  * Zone
    * Sensors (temp, humidity,light)
    * Controls (lights,fans,temperature)
    * Pot1 (Things things that share the same growing medium, the ph and water temp is the same for all items in a pot)
      * Sensors (liquid temp,ph)
      * Controls (ph and temp)
    * Pot2 (Things things that share the same growing medium, the ph and water temp is the same for all items in a pot)
      * Sensors (liquid temp,ph)
      * Controls (ph and temp)

## Description
When the World object is created it creates all of the GrowObjects described in the setup.json file. The objects are created based on the "type" property. This type property must be implemented in the <Sensors/Environments/Controls> and included in the ImplementedGrowObjects dict at the bottom of the corresponding file. 

The main loop is run every World.main_loop_min_time (as set in the setup.json file). The main loop will be run AT MOST this often, but may be longer based on the duration of taking measurements, running controls, exporting data, etc.

When the loop runs it will run world.update() which runs the update() function on every GrowObject (all GrowObjects have this, but it may not do anything). It just updates the internal state of objects and does not report anything. The world.run_controls() function is then run which runs the run_controls() method of any object that has the property directly_controllable set to True. 

The world.report_data() method is then run which queries all devices to report their current state. Currently this is done by seeing if the object has the attribute "value", and if it does then reporting a dict that is defined in the GrowObject.py file. This is probably not the best way to do this and will likely change. The key part of this is when a Control type object is run, it may never be in a state to report out the control it is running (the ph pumps for example). So when a control object is run, it will report its action to the world.data dict and the action will be reflected in the next world.report_data() call. The world.data dict will then be cleared after the data is saved.

## Reporting Data
A major goal of this project is to report out data in an easy to access format of the end user's choosing.



# TODO
* Change how data is reported when report_data is called in world
  * Currently it reports the data stored in "value" for any object that has that attribute
  * Would like it to call a report_data method on the objects which would allow more control over what is reported. It would also allow multi purpose sensors like temperature and humidity sensors to be on the same chip
* Implement World.Save(). Will need to create world.data, and implement the reporting functionality in the Controls objects. 
* Report raw, filtered, and unit converted data for sensors (for ph want the last voltage read, the smoothed ph reading, and the raw ph reading). 