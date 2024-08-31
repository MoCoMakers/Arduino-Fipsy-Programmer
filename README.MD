# Getting Started

### Install Python 3.1+
Install the requirements, you will need tk for the GUI<br>
`pip install -r requirements.txt`

### Install Arduino IDE
Once loaded, plugin your Arduino, and load 'Arduino_Programmer/Arduino_Programmer.ino' - then upload this. Notice that you can override pin numbers SS, DATAOUT, DATAIN, and SPICLOCK

# Notes
The GUI in FileChooser.py selects a port and .jed file to send to an Arduino connected by USB.

The Arduino code is under development, but is based off of a working example for the Raspberry PI.
The biggest difference will be that the Raspberry Pi code uses linux libraries, and we are only using Arduino libraries and compatible code.

