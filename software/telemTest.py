import serial
from AbstractModel import HACS_Proxy
from AbstractModel import FakeWriter
import MAVLink.MAVLink as MAVLink
import time
import threading
import random

g_counter = 0

class myThread(threading.Thread):
    def __init__(self,com,mavlink):
        threading.Thread.__init__(self)
        self.mavlink = mavlink
        self.COM = com

    def run(self):
        while(True):
            n = self.COM.inWaiting()
            if(n != 0):
                bytes = self.COM.read(n)
                try:
                    msg_list = self.mavlink.parse_buffer(bytes)
                except:
                    continue
                if msg_list != None:
                    for msg in msg_list:
                        if (isinstance(msg, MAVLink.MAVLink_pfd_message)):
                            pass
                        elif (isinstance(msg, MAVLink.MAVLink_navd_message)):
                            pass
                        elif (isinstance(msg, MAVLink.MAVLink_magcal_message)):
                            pass
                        elif (isinstance(msg, MAVLink.MAVLink_systemid_message)):
                            pass
                        elif (isinstance(msg, MAVLink.MAVLink_syscmd_message)):
                            if (msg.cmd == HACS_Proxy.HACS_GND_CMD_GET_MODE):
                                print "mode" + str(msg.payload)
                            elif (msg.cmd == HACS_Proxy.HACS_GND_CMD_TELEM_TEST):
                                print "get:\t\t" + str(msg.payload & 0xFFFF)
            else:
                time.sleep(0.025)

# initialize Serial com
COM = serial.Serial(1,115200*2) # COM2
COM.flushInput() # flush input buffer

mavlink = MAVLink.MAVLink(FakeWriter(COM))

thread = myThread(COM, mavlink)
thread.start()

# retart the test
mavlink.syscmd_send(HACS_Proxy.HACS_GND_CMD_TELEM_TEST, 0xFFFFFFFF)

while(True):
    time.sleep(random.uniform(0.1,0.2))
    print "sending\t\t" + str(g_counter)
    mavlink.syscmd_send(HACS_Proxy.HACS_GND_CMD_TELEM_TEST, g_counter)
    g_counter += 1
