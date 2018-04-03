from Tkinter import Tk
from tkFileDialog import askopenfilename
from ttk import *
from Tkinter import *

import serial
import serial.tools.list_ports

from time import sleep


def do_run():
	root = Tk()
	root.title("Arduino JEDEC Programmer - MoCo Makers")
	 
	# Add a grid
	mainframe = Frame(root)
	mainframe.grid(column=0,row=0, sticky=(N,W,E,S) )
	mainframe.columnconfigure(0, weight = 1)
	mainframe.rowconfigure(0, weight = 1)
	mainframe.pack(pady = 100, padx = 100)

	#self.bbutton= Button(root, text="Browse", command=self.browsecsv)

	 
	# Create a Tkinter variable
	global tkvar
	tkvar = StringVar(root)
	 
	# Dictionary with options
	usb_ports=serial.tools.list_ports.comports()
	
	global available_ports
	available_ports={}

	for port in usb_ports:
		human_name=str(port)
		port_name=port.device
		available_ports[human_name]=port_name


	choices = available_ports.keys()
	if choices:
		tkvar.set("Select a port") # set the default option
	else:
		choices=["None Detected. Please re-open program."]
		
	
	
	port_label = Label(mainframe, text="Choose the USB Port").grid(row = 1, column=1)
	
	popupMenu = OptionMenu(mainframe, tkvar, *choices)
	popupMenu.grid(row = 2, column =1)
	
	select_file_button = Button(mainframe, text="Select your file", fg="black", command=select_file_callback)
	select_file_button.grid(row=3, column=1)
	
	global file_status
	file_status = Label(mainframe, text="No file selected.")
	file_status.grid(row=4, column=1)
	#status.pack()
	
	
	check_id_button = Button(mainframe, text="Check Device ID", fg="black", command=check_id_callback)
	check_id_button.grid(row=5, column=1)
	
	erase_device_button = Button(mainframe, text="Erase Device", fg="black", command=erase_device_callback)
	erase_device_button.grid(row=5, column=2)
	
	program_device_button = Button(mainframe, text="Program Device", fg="black", command=program_device_callback)
	program_device_button.grid(row=5, column=3)
	
	
	# link function to change dropdown
	tkvar.trace('w', change_dropdown)
	root.mainloop()
	
def select_file_callback():
	print "In select file callback"
	#Tk().withdraw() # we don't want a full GUI, so keep the root window from appearing
	filename = askopenfilename() # show an "Open" dialog box and return the path to the selected file
	print(filename)
	global file_status
	file_status["text"]=filename
	
def check_id_callback():
	print "In Check ID"
	try:
		global available_ports
		global port_selected
		port_name = available_ports[port_selected]
		print "Using port: "+ port_name
		#arduinoSerialData = serial.Serial(port_name, 115200, timeout=.1)
		
		arduinoSerialData = serial.Serial()
		arduinoSerialData.port = port_name
		arduinoSerialData.baudrate = 115200
		arduinoSerialData.timeout = 1
		arduinoSerialData.setDTR(False)
		#arduinoSerialData.setRTS(False)
		arduinoSerialData.open()
		
		
		
	except:
		import tkMessageBox
		Tk().withdraw()
		tkMessageBox.showinfo("Failed to connect to Arduino","Failed to connect to Arduino. Did you select a port? Can Arduino IDE detect the device?")
		return
		
	device_id=""
	while not device_id:
		arduinoSerialData.write("do_check_id")
		sleep(1)
		data = arduinoSerialData.readline()[:-2] #the last bit gets rid of the new-line chars
		if data:
			if data=="I received: do_check_id":
				print "Hit on: do_check_id"
				
				while not device_id:
					sleep(1)
					data = arduinoSerialData.readline()[:-2]
					print "Now showing: "+data
					if data:
						device_id=data
						print "Device ID is: "+device_id
					
	
def erase_device_callback():
	print "In erase device"
	
def program_device_callback():
	print "In program device"

 
# on change dropdown value
def change_dropdown(*args):
	global tkvar
	global port_selected
	port_selected=tkvar.get()
	print( tkvar.get() )
	

if __name__ == "__main__":
	file_status="No file selected."
	port_selected=""
	tkvar=""
	available_ports=""
	do_run()