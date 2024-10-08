from tkinter.filedialog import askopenfilename

from tkinter.ttk import *
from tkinter import *

import serial
import serial.tools.list_ports

from time import sleep, time

import binascii

class customSerial(serial.Serial):
    def __int__(self):
        super().__init__(self)
    def write(self, string_val):
        try:
            new_val = string_val.encode('ascii', 'ignore')
            if len(new_val)>1:
                if new_val[-1]!=b'\n':
                    new_val = new_val+b'\n'
        except:
            new_val = string_val

        serial.Serial.write(self, data=new_val)

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
    print("In select file callback")
    #Tk().withdraw() # we don't want a full GUI, so keep the root window from appearing
    filename = askopenfilename() # show an "Open" dialog box and return the path to the selected file
    print(filename)
    global file_status
    file_status["text"]=filename

def check_id_callback():
    print("In Check ID")
    try:
        global available_ports
        global port_selected
        port_name = available_ports[port_selected]
        print("Using port: "+ port_name)
        #arduinoSerialData = customSerial(port_name, 115200, timeout=.1)

        arduinoSerialData = customSerial()
        arduinoSerialData.port = port_name
        arduinoSerialData.baudrate = 115200
        arduinoSerialData.timeout = 1
        arduinoSerialData.setDTR(False)
        #arduinoSerialData.setRTS(False)
        arduinoSerialData.open()



    except:
        from tkinter import messagebox as tkMessageBox
        Tk().withdraw()
        tkMessageBox.showinfo("Failed to connect to Arduino","Failed to connect to Arduino. Did you select a port? Can Arduino IDE detect the device?")
        return

    device_id=""
    device_found = False
    # Set timeout time
    end = time() + 10
    while not device_id and time() < end:
        arduinoSerialData.write("do_check_id\n")
        sleep(1)
        data = arduinoSerialData.readline()[:-2] #the last bit gets rid of the new-line chars
        print(data)
        if data:
            if data==b"I received: do_check_id":
                print("Hit on: do_check_id")

                count=0

                while not device_id:
                    sleep(1)
                    data = arduinoSerialData.readline()[:-2]
                    print("Now showing: "+str(data))
                    if data:
                        if b"Device ID = " in data:
                            device_id=data
                            print("Device ID is: "+str(device_id))
                            device_found = True
                        else:
                            print("Response: "+str(data))

                    count=count+1
                    if(count>15):
                        device_id="Time's up"
    #Trigger terminate
    arduinoSerialData.write("terminate_connect")
    
    if not device_found:
        from tkinter import messagebox as tkMessageBox
        Tk().withdraw()
        tkMessageBox.showinfo("Connection Timeout","No Fipsy dected on device. Check wiring and connections.")
        return


def erase_device_callback():
    print("In Erase ID")
    try:
        global available_ports
        global port_selected
        port_name = available_ports[port_selected]
        print("Using port: "+ port_name)

        arduinoSerialData = customSerial()
        arduinoSerialData.port = port_name
        arduinoSerialData.baudrate = 115200
        arduinoSerialData.timeout = 1
        arduinoSerialData.setDTR(False)
        #arduinoSerialData.setRTS(False)
        arduinoSerialData.open()

    except:
        from tkinter import messagebox as tkMessageBox
        Tk().withdraw()
        tkMessageBox.showinfo("Failed to connect to Arduino","Failed to connect to Arduino. Did you select a port? Can Arduino IDE detect the device?")
        return

    device_id=""
    # Set end time
    end = time()+30
    erase_success = False
    arduinoSerialData.write("do_pass")
    arduinoSerialData.write("do_erase_device")
    while not erase_success and time() < end:
        sleep(1)
        data = arduinoSerialData.readline()[:-2] #the last bit gets rid of the new-line chars
        print(data)
        if data:
            if data==b"I received: do_erase_device":
                print( "Hit on: do_erase_device")

                count=0

                while not erase_success:
                    sleep(1)
                    data = arduinoSerialData.readline()[:-2]
                    print("Now showing: "+str(data))
                    if data:
                        if b"Device was successfully erased" in data:
                            erase_success = True
                            break
                        else:
                            print("Response: "+str(data))

                    count=count+1
                    if(count>15):
                        break
    #Trigger terminate
    arduinoSerialData.write("terminate_connect")

    if not erase_success:
        from tkinter import messagebox as tkMessageBox
        Tk().withdraw()
        tkMessageBox.showinfo("Failed to connect to Arduino","Failed to connect to Arduino. Did you select a port? Can Arduino IDE detect the device?")
        return



def program_device_callback():
    print("In Programming ID")
    try:
        global available_ports
        global port_selected
        port_name = available_ports[port_selected]
        print("Using port: "+ port_name)

        arduinoSerialData = customSerial()
        arduinoSerialData.port = port_name
        arduinoSerialData.baudrate = 115200
        arduinoSerialData.timeout = 1
        arduinoSerialData.setDTR(False)
        #arduinoSerialData.setRTS(False)
        arduinoSerialData.open()



    except:
        from tkinter import messagebox as tkMessageBox
        Tk().withdraw()
        tkMessageBox.showinfo("Failed to connect to Arduino","Failed to connect to Arduino. Did you select a port? Can Arduino IDE detect the device?")
        return

    global file_status
    filepath=str(file_status["text"])
    if not ".jed" in filepath and filepath[-4:] != ".jed":
        cast_alert("Select a valid .jed file")
    else:
        with open(filepath, "rb") as input_file:
            while True:
                print("Beginning file stream")
                arduinoSerialData.write("do_program_device")
                sleep(1)
                data = arduinoSerialData.readline()[:-2] #the last bit gets rid of the new-line chars
                if data:
                    if data==b"I received: do_program_device":
                        print("Hit on: do_program_device")

                        count=0

                        while True:
                            data = arduinoSerialData.readline()[:-2]
                            if data:
                                if data==b"check_JEDEC_file":
                                    print("Starting: check of JEDEC file")
                                    if(do_check_JEDEC_file(input_file,arduinoSerialData)):
                                        print("Successful check. Device programmed.")
                                    else:
                                        print("Failed JEDEC File check")
                                    return
                                if data==b"getc":
                                    count=count+1
                                    myChar=input_file.read(1)
                                    arduinoSerialData.write(myChar)
                                    print("Fetching a character: "+str(myChar))
                                    print("Showing count"+str(count))
                                elif data==b"end_file_connection" or data==b"end_connection":
                                    print("Received end of connection")
                                    return
                                else:
                                    print("Message received: "+str(data))


def do_check_JEDEC_file(input_file, arduinoSerialData):
    # Attempt to open the JEDEC file
    # A JEDEC file is a text file - we will only need to read text, and the end of line can be useful to us

    #Read the file characters until we find the starting STX (CTRL-B, 0x02)
    count=0
    key=""
    while(True):
        key = input_file.read(1)
        if (key!=b"\x02") and (key!=b''):
            pass
        else:
            break

    if key==b"":
        cast_alert("File format is not valid for JEDEC. L1")
        arduinoSerialData.write("failed_JEDEC_format")
        return False
    else:
        # Look for key characters until we find Q and the qualifier 'F' for fuse count
        # We assume this will come before the fuse table as it is needed to read the address
        while(True):
            # Look for Q
            key, input_file=JEDEC_SeekNextKeyChar(input_file, arduinoSerialData)
            if key:
                if key==b'Q':
                    # Get qualifier
                    keyq=input_file.read(1)
                    print("Looking at keyq of:"+str(keyq))
                    if keyq==b'F':
                        break
                    else:
                        #Ignore 'Q' characters that don't have the 'F' qualifier
                        pass
            else:
                #End of File
                cast_alert("File format is not valid for JEDEC. L2")
                arduinoSerialData.write("failed_JEDEC_format")
                return False

        # We really don't care about the fuse count, unless we want to use it to help verify this is the right device
        # But we need to know how may characters it has so we can read addresses in the fuse table
        # Go get that count of characters

        addr_digits=0

        while(True):
            key=input_file.read(1)
            if key==b'':
                cast_alert("File format is not valid for JEDEC. L3")
                arduinoSerialData.write("failed_JEDEC_format")
                return False
            if key!=b'*':
                addr_digits=addr_digits+1
            else:
                break

        # We just read a delimiter, so we are at the start of the next field
        # Look for the key character - this step is probably overkill here, but for completeness

        key, input_file=JEDEC_SeekNextNonWhitespace(input_file, arduinoSerialData)
        if key==b"":
            cast_alert("File format is not valid for JEDEC. L4")
            arduinoSerialData.write("failed_JEDEC_format")
            return False

        while(key!=b'E'):
            key, input_file = JEDEC_SeekNextKeyChar(input_file, arduinoSerialData)
            if not key:
                cast_alert("File format is not valid for JEDEC. L5")
                arduinoSerialData.write("failed_JEDEC_format")
                return False

        print("Doing Feature Row")
        featurerow=[0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00]  #10 bytes long
        # We are now at the feature row bits, pointed at the fuse data
        # Read the data into the local arrays
        for i in range(0,8):
            FuseByte, input_file, is_success = JEDEC_ReadFuseByte(input_file)
            if not is_success:
                cast_alert("File format is not valid for JEDEC. L6")
                arduinoSerialData.write("failed_JEDEC_format")
                return False
            featurerow[i]=FuseByte

        print("Grabbing feabits")

        feabits=[0x00,0x00,0x00,0x00] #4 bytes long
        for i in range(0,2):
            FuseByte, input_file,is_success = JEDEC_ReadFuseByte(input_file)
            if not is_success:
                cast_alert("File format is not valid for JEDEC. L7")
                arduinoSerialData.write("failed_JEDEC_format")
                return False
            feabits[i]=FuseByte

        # If the Slave SPI port is disabled, warn the user and exit. This needs to be enabled to reprogram the Fipsy
        # This check checks for a nessesary feature of SPI_SLAVE_PORT being enabled, but changing this one value
        # is not sufficient to enable the SPI port. This should be done from Lattice Diamond's Spreadsheet view to ensure success.

        #Turn bytes to type int, which in Python are able to do the bitwise & opperation
        #If the key bit is a 1 - then the & comparision will return 0, and fail - a sign that SPI_SLAVE_PORT is disabled
        SPI_SLAVE_PORT_hex = binascii.hexlify(feabits[1]).decode('ascii')
        SAFE_SPI_SLVE_PORT_to_ascii = "20"
        print("SPI safe hex: "+str(SAFE_SPI_SLVE_PORT_to_ascii)+ " and SPI_SLAVE_PORT hex: " + str(SPI_SLAVE_PORT_hex))
        print(str(featurerow))
        print(str(feabits))
        has_valid_SPI_SLAVE_PORT_ENABLE = SPI_SLAVE_PORT_hex == SAFE_SPI_SLVE_PORT_to_ascii

        # IN Python 2 it was - if (int(feabits[1].encode('hex'),8) & int('\x40'.encode('hex'),8)):
        # TODO: This might need an improvment in documentation
        if not has_valid_SPI_SLAVE_PORT_ENABLE:
            cast_alert("Failed to detect SPI_SLAVE_PORT enabled. Enable this in Lattice Diamond's spreadsheet view.")
            arduinoSerialData.write("failed_JEDEC_format")
            return False
        # Restart the file to the beginning
        input_file.seek(0)

        # Read the file characters until we find the starting STX (CTRL-B, 0x02)
        while(True):
            key = input_file.read(1)
            print("Key is:"+str(key))
            if (key!=b"\x02") and (key!=b''):
                pass
            else:
                break
        if key==b"":
            cast_alert("File format is not valid for JEDEC. L8")
            arduinoSerialData.write("failed_JEDEC_format")
            return False

        # Next look for the fuse table specifically
        while(True):
            key, input_file = JEDEC_SeekNextKeyChar(input_file, arduinoSerialData)
            if key==b'L' or key==b'':
                break
            else:
                pass


        # We are now at the fuse table and pointing to the starting address.
        # This address contains the same number of digits as the fuse count as previously found.
        # The documentation says it is followed by white space, but does not really guarantee what kind
        # of white space, so we must read off the address characters one at a time.
        # We do assume from the documentation that the first L key character found will contain the address zero,
        # and fuse data will start from the beginning of flash.  It is more work to translate and use the address,
        # so we don't want to bother if that is not the way it is suppose to be.  However, we can verify this address
        # is zero as expected and flag an error if it is something else.

        # Read the address and check that it is all zero
        # Note that any EOF would also drop out here

        for i in range(0,addr_digits):
            if input_file.read(1) != b'0':
                cast_alert("File format is not valid for JEDEC. L9")
                arduinoSerialData.write("failed_JEDEC_format")
                return False


        #cast_alert("Success so far")

        # The address is good and is zero, so clear the address in the device
        arduinoSerialData.write("clear_the_address")
        print("Casting: clear_the_address")
        data=""
        end = time() + 30
        has_cleared = False
        while True and time() < end:
            data = arduinoSerialData.readline()[:-2]
            print(data)
            if data and data==b"address_cleared":
                has_cleared = True
                break
            sleep(0.1)

        if not has_cleared:
            cast_alert("Programming Can't Complete. Timing Execution Error? Please try again.")
            return False


        #Make sure the consecutive write statements don't appear as one string
        sleep(0.1)

        # We are now pointed at the fuse data (link table, whatever you want to call it)
        # Proceed to write flash locations per page until the delimiter is reached.
        # The table should have an even set of pages in it, so if we get the delimiter or any other failure
        # in the middle of a page, that is a format error.  Unfortunately, exiting here will have the chip
        # in a bizarre state of partially programmed, but that should be an exceptional case.
        print("Casting: setup_increment_command")
        arduinoSerialData.write("setup_increment_command")
        while True:
            data = arduinoSerialData.readline()[:-2]
            if data and data==b"increment_declared":
                break

        transaction_data_chunks=[]

        FuseByte=''
        while FuseByte!='*':
            # Get the first byte and check that we are not at the delimiter
            FuseByte, input_file,is_success = JEDEC_ReadFuseByte(input_file)
            if not is_success:
                cast_alert("File format is not valid for JEDEC. L10")
                arduinoSerialData.write("failed_JEDEC_format")
                return False
            # If we did not get the delimiter, this should be a valid row
            if FuseByte !='*':
                # Attempt to collect the rest of the page
                chunk=[]
                chunk.append(FuseByte) #Add the first byte from above
                for i in range(1,16):
                    FuseByte, input_file,is_success = JEDEC_ReadFuseByte(input_file)
                    if not is_success:
                        cast_alert("File format is not valid for JEDEC. L11")
                        arduinoSerialData.write("failed_JEDEC_format")
                        return False
                    chunk.append(FuseByte)
                transaction_data_chunks.append(chunk)

        print("At chunking")
        count=1
        for chunk in transaction_data_chunks:
            arduinoSerialData.write("do_chunk")  #Arduino's Serial.readStringUntil('\n');  needs a newline character, or it will wait until timeout

            while True:
                print("Waiting for arduino")
                data = arduinoSerialData.readline()[:-2]
                if data and data==b"next_chunk":
                    print("At next_chunk")
                    print("At chunk: "+str(count)+" of "+str(len(transaction_data_chunks))+" - "+str(((count*1.0)/len(transaction_data_chunks))*100)+"%")
                    count=count+1
                    break
                if data and data==b"do_chunk_recieved":
                    print("do_chunk_recieved")
                    for sendbyte in chunk:
                        arduinoSerialData.write(sendbyte)
                        #sleep(0.2)
                        print("byte sent")

                    # The page is suppose to program in 200us, which is generally faster than we can send another command,
                    # but for completeness and for the benefit of porting this code, we setup a wait here.
                    # With a small chip this is not much of a burden, while other systems with a faster connection
                    # and a larger chip my want to check busy instead.

                    #sleep(1)

                else:
                    print("Incoming data: "+str(data))
        print("After Chunking")

        # Note that for our chip the JEDEC file seems to contain two blocks of data without easily located explanation.
        # The first is the configuration for the present design, and the second seems to be the remainder of the
        # configuration memory, as the address for the second block changes for each design.  There is no user flash
        # memory in this chip.  This remainder is always in a benign state, with another end flag of sorts at the
        # end (all 1's), which is never reached.  Considering all this, we ignore this second block of data.

        # Go find the key for our next thing of interest, the feature row fuses
        # We just read a delimiter, so we are at the start of the next field

        key, input_file = JEDEC_SeekNextNonWhitespace(input_file, arduinoSerialData)

        #if((key = JEDEC_SeekNextNonWhitespace()) == 0) EXIT_FILEFORMATERROR;

        if not key:
            cast_alert("File format is not valid for JEDEC. L12")
            arduinoSerialData.write("failed_JEDEC_format")
            return False

        #  Look for the key character
        while(key!=b'E'):
            key, input_file = JEDEC_SeekNextKeyChar(input_file, arduinoSerialData)
            if not key:
                cast_alert("File format is not valid for JEDEC. L13")
                arduinoSerialData.write("failed_JEDEC_format")
                return False

        # We are now at the feature row bits, pointed at the fuse data
        # Read the data into the local arrays

        #Get featurerow and feabits done above
        #for(i=0;i<8;i++) if(JEDEC_ReadFuseByte(&featurerow[i]) != 1) EXIT_FILEFORMATERROR;
        #for(i=0;i<2;i++) if(JEDEC_ReadFuseByte(&feabits[i]) != 1) EXIT_FILEFORMATERROR;


        # Call our routine to program these values
        # Note that this routine may alter some bits (see comments with routine)

        features_status = Fipsy_WriteFeatures(featurerow, feabits, arduinoSerialData)
        if not features_status:
            cast_alert("Failed to write device features")
            arduinoSerialData.write("failed_JEDEC_format")
            return False


        # Program the DONE bit (internal)
        # This effectively tells the SDM (self download mode) that it is allowed to run
        # and allows the device to enter user mode when loading is complete (ie done)
        arduinoSerialData.write("do_program_done")


        while True:
            data = arduinoSerialData.readline()[:-2]
            if data and data==b"do_program_done_complete":
                print("Do data done complete")
                break
            else:
                print("Message received: "+str(data))

        # Security and OTP bits would be programmed here, but we do not support them
        # They seem to operate similar to DONE, enabling or disabling certain features
        # DONE is all we need - enables user mode
        # Advanced user may also user an external 'DONE' pin to control entry into user mode,
        # but that will require additional study of feature settings and coding

        load_status = Fipsy_LoadConfiguration(arduinoSerialData);

        if not load_status:
            cast_alert("Failed to load configuration")
            arduinoSerialData.write("failed_JEDEC_format")
            return False

        # If we got here, all went ok, return success
        #Trigger terminate
        arduinoSerialData.write("terminate_connect")
        return True

"""
FIPSY_LOADCONFIGURATION loads the active configuration from flash as
it would on power up.  This can be completed at any time, but is only 
useful if there is a good configuration in flash.  It is usually called
after a configuration has been written so that the new configuration can
take effect.  This is separate from the configuration programming itself
so the user can decide when to do that.
"""
def Fipsy_LoadConfiguration(arduinoSerialData):
    arduinoSerialData.write("do_load_configuration")
    while True:
        data = arduinoSerialData.readline()[:-2]
        if data and data==b"do_load_configuration_complete":
            print("Load configuration complete")
            break
        else:
            print("Message received: "+str(data))
    return True

"""

/* 
*/

DWORD Fipsy_LoadConfiguration(void)
 {
  // All exported library functions get this check of hardware and arguments    
  if(!HWIsOpen) return(ErrorNotOpen());

  // Send command to load the configuration
  // Remember there are fewer operands for unknown reasons
  

  // Return success
  return(1);
 }

"""


"""
FIPSY_WRITEFEATURES writes 'feature row' and 'feabits' values to the
flash as prescribed in the arguments.  This is typically used in a call 
from the programming routine, but it is possible that we would want to 
do that separately.  The caveat is that this does not check for erased 
condition, so overwriting an existing set is a potential user error.

Also, this routine is for the Fipsy module, so the SPI must remain
available, and therefore this routine forces that condition and won't
let the caller change that setting. However, this appears to be a 
necessary but not sufficient condition, as the diamond software will 
also drop support for the pins in that case.

Note that most of the action here seems to be in the feabits.  What is 
being called the feature row here, as far as we can tell, contains other
information that may or may not apply to our chip or configuration, 
including various addresses and programmable codes.  So for it will 
usually be all 0.  The feabits contain the hardware control settings 
that concern us most.
 """

def Fipsy_WriteFeatures(featurerow, feabits, arduinoSerialData):
    if not featurerow or not feabits:
        return False

    # Send Feature Row
    arduinoSerialData.write("send_feature_bits")

    while True:
        data = arduinoSerialData.readline()[:-2]
        if data and data==b"received_send_feature_bits":
            for x in range(0,8):
                sendbyte=featurerow[x]
                print("Sending feature byte: "+str(sendbyte))
                arduinoSerialData.write(sendbyte)
            print("Feature bits sent")
            break
        else:
            print("Message received: "+str(data))

    # Send FeaBits
    arduinoSerialData.write("send_feabits")

    while True:
        data = arduinoSerialData.readline()[:-2]
        if data and data == b"received_send_feabits":
            for x in range(0,2):
                sendbyte=feabits[x]
                print("Sending feabits: "+str(sendbyte))
                arduinoSerialData.write(sendbyte)
            print("Feabits sent")
            break
        else:
            print("Message received: "+str(data))

    return True

    """
  // Command to write feature row    
  SPIBUFINIT;
  MachXO2_Command = MACHXO2_CMD_PROG_FEATURE;
  memcpy(pMachXO2_Data, FeatureRow, 8);
  MachXO2_SPITrans(12); 
 
  // Wait more than the time suggested as required to complete
  Sleep(2);

  
     
  // Return success
  return(1);
 }


    """


"""
JEDEC_SEEKNEXTKEYCHAR reads the specified file stream until the next key 
character has been read. The key character (ie key word) is the first 
character of a field (ie after the previous field's delimiter) after any 
white space.  Thus, in order to do this search, this function will also 
search for the start of the next field.  If we know we are at the start 
of a field already, then we should not use this routine but instead just 
look for the character.  This routine will find the next key character.

The key character found is returned by value.  If the end of the file 
is reached, or some other error occurs, a 0 is returned.
 """
def JEDEC_SeekNextKeyChar(input_file, arduinoSerialData):
    # Look for end of field, point to start of next field
    while(True):
        key=input_file.read(1)
        if key==b"":
            return False
        if key==b"*":
            break

    # Pull white space until an actual character is reached
    # This will be our key character

    key, input_file = JEDEC_SeekNextNonWhitespace(input_file, arduinoSerialData)

    return key, input_file

"""
JEDEC_SEEKNEXTNONWHITESPACE parses the file until it finds a character 
that is not white space as defined for a JEDEC file.  That character is 
returned if found.  If there is an error, a 0 is returned.

Note that the delimiter ('*') is also white space in this context.  This is
like a line terminator in a sense, so if we have not already read it, we 
don't want to now read it and return it.  This could happen if it is 
the first character in a file, or if a field ended with "**" or more.
These technically null fields should be ignored in this search.

So define white space as ' ', CR, LF, NULL, and '*' at least.  But in
reality we equally ignore any character less than space, which includes
most control characters, including the JEDEC file start and end STX/EOT.
 """
def JEDEC_SeekNextNonWhitespace(input_file, arduinoSerialData):
    while(True):
        key=input_file.read(1)
        if key==b"":
            return False, input_file
        if key<=b' ' or key==b'*' or key==b'\r' or key==b'\t' or key==b'\n' or key==b'\x0D' or key==b'\x0A' or key==b'\x2A' or key.isspace():
            pass
        else:
            #print("declaring a nonwhite character of: "+str(key) + str(type(key)) + str(len(key)))
            return key, input_file

    return key, input_file
 
"""
/* JEDEC_READFUSEbyte reads from the specified file stream until it has 
   collected eight binary characters and converts those characters to a byte
   to return by reference.  The value returned is 1 if this happened correctly,
   0 if an error was encountered, and '*' if the field has ended ('*' found).
   Generally, unless something is wrong with the file, the full byte will be
   collected or '*' will be returned.  Other white space is automatically removed.
   A return value of 0 can be interpreted as a format error.  A return value 
   of '*' means the caller should assume the file pointer now points to the 
   start of the next field.
   
   Note that anything other than 1,0,* characters can be considered white space.
   If a character is out of place or replaced, and it disrupts the count of 1s
   and 0s, then an error will eventually be found.  If the bad character is there
   without affecting the result, then it has no impact this way.  In a perfect
   file, the characters so removed are truly white space. 
*/

byte JEDEC_ReadFuseByte(byte *FuseByte)
 {
  char bstr[10];
  int ic;
  byte cnt = 0;
  
  // Default byte value
  *FuseByte = 0;
  
  // Read characters  
  do
   {
    // Get a character
    ic = fgetcharacter();
    if(ic == EOF) return(0);
    // Record valid characters
    if(ic == '0') bstr[cnt++] = '0';
    if(ic == '1') bstr[cnt++] = '1';    
    // If delimiter found, return it
    if(ic == '*') return('*');   
   }
  while(cnt < 8);
  
  // Convert the characters to binary
  // We could make this a loop, but it would just take more variables and time
  // This also allows us to easily adjust the bit order if it ever needs to be different
  if(bstr[0] == '1') *FuseByte += 128;
  if(bstr[1] == '1') *FuseByte += 64;
  if(bstr[2] == '1') *FuseByte += 32;
  if(bstr[3] == '1') *FuseByte += 16;
  if(bstr[4] == '1') *FuseByte += 8;
  if(bstr[5] == '1') *FuseByte += 4;
  if(bstr[6] == '1') *FuseByte += 2;
  if(bstr[7] == '1') *FuseByte += 1;
    JEDEC_ReadFuseByte
  // Return normal success
  return(1);
 }
"""
 
def JEDEC_ReadFuseByte(input_file):
    byteArray=[]
    FuseByte=0
    is_success=False
    print("doing fuse keys")
    while(len(byteArray)<8):
        key=input_file.read(1)
        if key==b"":
            is_success=False
            print("Returning EOF")
            return False, input_file, is_success
        # Record valid characters
        if key==b"0":
            byteArray.append('\x00')
        elif key==b"1":
            byteArray.append('\x01')
        # If delimiter found, return it
        elif key==b'*':
            print("Returning delimiter - *")
            is_success=True # This notes the end of a row
            return '*', input_file, is_success
        else:
            print("Looking at special key:"+str(key)+".")
            #return key, input_file, False
    
    print(byteArray)

    if byteArray[0]=='\x01':
        FuseByte= FuseByte+128
    if byteArray[1]=='\x01':
        FuseByte= FuseByte+64
    if byteArray[2]=='\x01':
        FuseByte= FuseByte+32
    if byteArray[3]=='\x01':
        FuseByte= FuseByte+16
    if byteArray[4]=='\x01':
        FuseByte= FuseByte+8
    if byteArray[5]=='\x01':
        FuseByte= FuseByte+4
    if byteArray[6]=='\x01':
        FuseByte= FuseByte+2
    if byteArray[7]=='\x01':
        FuseByte= FuseByte+1

    print("FuseByte After Collapse: "+str(FuseByte))

    #turn int to byte character
    FuseByte=bytes([FuseByte])
    is_success=True
    return FuseByte, input_file, is_success

# on change dropdown value
def change_dropdown(*args):
    global tkvar
    global port_selected
    port_selected=tkvar.get()
    print( tkvar.get() )

def cast_alert(text):
    from tkinter import messagebox as tkMessageBox
    Tk().withdraw()
    tkMessageBox.showinfo("Alert",text)
    return

if __name__ == "__main__":
    file_status="No file selected."
    port_selected=""
    tkvar=""
    available_ports=""
    do_run()