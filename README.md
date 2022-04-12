# BotathonS3Lighting
## What is this?
This is the code used for the lighting system during Botathon Season 3 for UNT Robotics. Using a configuration file, it allows users to easily customize certain settings and behaviors, such as the duration of the timer or the colors of the lights.
## What is necessary to run this?
1. First you need a Raspberry Pi or an equivalent system that can connect to the LED system. The Raspberry Pi and LEDs this program was tested with was a Raspberry Pi 4b and WS2812B lights.

    As long as the lights can use ``neopixel`` and are _RGB_ (as opposed to _RGBW_), then they should work fine.

2. Next you need to install a few libraries. ~If you're not using a Raspberry Pi, I am sorry for your loss.~

    Run:

    ```
    pip install rpi_ws281x adafruit-circuitpython-neopixel
    ```
    _Note: you may need to run with the ``sudo`` keyword and/or use ``pip3`` instead._

    If you do not have ``configparser`` and ``multiprocessing`` installed, install those as well.

3. A breadboard or a way to connect to GPIO pins is also helpful.


4. Make sure the config file ``led.cfg`` is placed in ``/home/pi/Documents/`` as that is where the program looks for it.


## How do I use this?

Edit the configuration file for what settings you want. The configuration file in the repository has comments that describe each value and key.

Run the program in Terminal or an IDE. The configuration settings will be printed prior to starting. In order to start, you have to press enter. While the timer is ongoing, you can enter the following for certain features:

_Inputs are case-sensitive_.
* `a ##` - Add ## seconds to the timer. 
    * Example: `a 130` which adds 130 seconds to the timer.
    * You can enter a negative amount as well.
* `p` - Pause the timer. This also changes the lighting.
* `g` - Change the lights to the goal lights. They flash once before slowly fading out. This pauses the timer.
* `v` - View the remaining time on the timer in seconds.

When the initial timer ends, you will be asked if you want to restart the timer (enter '0'), if there is a _Sudden Death_ (enter '1'), or to turn off the lights and exit the program (enter '2').

_Sudden Death_ will end upon either its timer end or when a goal is scored. Inputs are the same as the original timer's.

When _Sudden Death_ ends, you will be asked if you want to restart the timer (enter '0'), if there is a _Shoot-Out_ (enter '1'), or to turn off the lights and exit the program (enter '2').

_Shoot-Out_s do not have a timer. Even and odd numbered lights will change between _ShootOutOne_ and _ShootOutTwo_ color for the duration. Exit by pressing enter.

When _Shoot-Out_ mode ends, the program will wait until you press enter, upon which the process restarts.

### _Notes:_
* The inputs assume _AutoTerm_ in the configuration file is set to off. Inputs with _AutoTerm_ on is similar but without the timer restart option.
* You cannot end the Goal lighting sequence early. Any inputs pushed to the program are simply backlogged.
* There is a 3-second countdown before the timer restarts after being paused or when a goal is scored.

## Wiring/Installation of LEDs
_This was made for WS2812B LEDs specifically. However, WS2812 LEDs should be able to follow fine._

_Also this was made for Raspberry Pis, specifically the 4b model_

WS2812B LED light strips have 5 wires on each end.
1. A ground wire (black)
2. A data wire (green)
3. A positive wire (red)
4. Another ground wire (black)
5. Another positive wire (red)

Note that wires 1-3 are connected to a female/male port thingy (I do not know the technical term but that should be descriptive enough).

Wire 1 connects to any ground pin on the Raspberry Pi (e.g. pin 6).
Wire 2 connects to GPIO18 on the Raspberry Pi (pin 12).
Wire 3 connects to the 5v pin on the Raspberry Pi (pin 2).
- _Note_: If you're using a level-shifter, don't use the 5v pin. Use the according LV pin the level shifter requires.

Wire 4 and 5 are connected to an external power source. I used a AC100-240V to DC5V8A power source. 

__Note__: The lights will not be able to display proper colors (mainly white) towards the end of the LED strip. Add an additional power source to the other end to fix this issue.


