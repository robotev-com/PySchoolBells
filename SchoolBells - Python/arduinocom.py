from serial import *
import time

class Arduino:
    def __init__(self, comPort, baud):
        self.connected = False;  
        self.serial= Serial()
        self.serial.port = comPort
        self.serial.baudrate = baud
        self.serial.timeout = 10
        self.bellState = False
    def start_communication(self):
        print("Starting communication with Arduino...")
        try:
            self.serial.open()
        except SerialException as e:
            self.connected = False
            print ("Error Opening "+self.serial.port)
            return False
         
        self.connected = True
        return self.connected
    def stop_communication(self):
        if self.serial.isOpen():
            self.serial.close()
            self.connected = False
            print("Arduino communication closed...")
        else:
            print("No active connection")
    def ring_bell(self):
        if not self.connected:
            print ("Not connected to device")
            return
        self.serial.write(bytes('r', "ascii"))
        self.serial.flush() 
        self.bellState = True
    def stop_bell(self):
        if not self.connected:
            print ("Not connected to device")
            return
        self.serial.write(bytes('s', "ascii"))
        self.serial.flush()
        self.bellState = False
    def set_comport_str(self, comport_number):
        self.serial.port = "COM"+ str(comport_number)
    def get_comport_int(self):
        comport_str = self.serial.port
        comport_str = comport_str.replace("COM", "")
        comport = int(comport_str)
        return comport
