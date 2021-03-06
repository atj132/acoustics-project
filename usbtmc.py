

import os

class UsbTmcDriver:
    """Simple implementation of a USBTMC device driver, in the style of visa.h"""

    def __init__(self, device):
        self.device = device
        self.FILE = os.open(device, os.O_RDWR)

        # TODO: Test that the file opened

    def write(self, command):
        os.write(self.FILE, command.encode());

    def read(self, length = 4000):
        return os.read(self.FILE,length)

    def getName(self):
        self.write("*IDN?")
        return  os.read(self.FILE,300) #self.read(300)

    def sendReset(self):
        self.write("*RST")

def getDeviceList():
    dirList=os.listdir("/dev")
    result=list()

    for fname in dirList:
        if(fname.startswith("usbtmc")):
            result.append("/dev/" + fname)

    return result



