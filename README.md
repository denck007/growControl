# growControl
This project is meant to be a general purpose monitoring and control tool for gardening systems. It is being developed for hydroponics but could be used for any type of gardening.

For a hydroponic Kratky system with 2 tanks under the same light that uses the system to control the lights and has automatic ph dosing, the setup would look like:
-World 
  -Zone
    -Sensors (temp, humidity,light)
    -Controls (lights,fans,temperature)
    -Pot1 (Things things that share the same growing medium, the ph and water temp is the same for all items in a pot)
      - Sensors (liquid temp,ph)
      - Controls (ph and temp)
    -Pot2 (Things things that share the same growing medium, the ph and water temp is the same for all items in a pot)
      - Sensors (liquid temp,ph)
      - Controls (ph and temp)

