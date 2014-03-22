# This module handles flight data inputs and generate useful outpus for
# the GUI module to function.

import math
import random
import threading
import time
import serial

class DataInput(object):
    def __init__(self):
        # For roll: left-down is positive; For Pitch: forward-upward is positive.
        # For pitch: range should be between -pi/2 and pi/2 (think of
        # spherical coordinates!!!!)
        self.readings = {"temperature":0,"heading":0,"pressure":0,"roll":0,
                         "pitch":0,"voltage":0,"mAh":0,"current":0,"GPS":(0.0,0.0)}
        
        # For simulation purposes
        self.pitchUp = True
        self.speedUp = True
        
        # initialize Serial com
        #self.COM = serial.Serial(1,9600) # COM2
        #self.COM.flushInput() # flush input buffer
        
        self.altitude = 0
        self.altitudeOffset = 0
        self.batt_capacity = 2200    # default battery capacity 2200 mAh
        self.volt_last = 0
        self.curr_last = 0
        self.roll_last = 0
        self.pitch_last = 0
        self.pressure_last = 0
        self.timeLast = time.time()
        
        self.EN_ALT_OFFSET = False
        self.firstSample = True
        self.exitFlag = False
        thread = myThread(self)
        thread.start()
    
    def updateReadings(self):
        try:
            line = self.COM.readline()
            line = line.split(';')
            
            self.readings["temperature"] = eval("0x"+line[0]) / 10.0
            
            self.readings["heading"] = eval("0x"+line[1])
            
            pressureTemp = eval("0x"+line[2])
            
            rollTemp = eval("0x"+line[3])
            if rollTemp & 0x8000 == 0x8000:
                rollTemp = (~rollTemp + 1) & 0xFFFF
                rollTemp = -rollTemp
            pitchTemp = eval("0x"+line[4])
            if pitchTemp & 0x8000 == 0x8000:
                pitchTemp = (~pitchTemp + 1) & 0xFFFF
                pitchTemp = -pitchTemp
            if (self.firstSample):
                self.roll_last = rollTemp
                self.pitch_last = pitchTemp
                self.pressure_last = pressureTemp
            else:
                rollTemp = 0.5 * rollTemp + 0.5 * self.roll_last
                pitchTemp = 0.5 * pitchTemp + 0.5 * self.pitch_last
                pressureTemp = 0.05 * pressureTemp + 0.95 * self.pressure_last
                self.pressure_last = pressureTemp
                self.roll_last = rollTemp
                self.pitch_last = pitchTemp
                self.readings["pressure"] = pressureTemp
                self.readings["roll"] = rollTemp / 100.0
                self.readings["pitch"] = pitchTemp / 100.0
    
            voltTemp = eval("0x"+line[5]) / 1000.0
            voltTemp = voltTemp * 30100.0 / 10010.0     # Ohm's Law. 20.09kohm and 10.01kohm in series
            voltTemp += 0.02              # correct system error
            currTemp = eval("0x"+line[6])
            # calculate mAh
            timeNow = time.time()
            self.readings["mAh"] += currTemp * (timeNow - self.timeLast) / 3600.0
            self.timeLast = timeNow
            currTemp /= 1000.0
            if (self.firstSample):
                self.volt_last = voltTemp
                self.curr_last = currTemp
                self.firstSample = False
            else:
                # apply low pass filter to voltage and current sensing
                voltTemp = 0.05 * voltTemp + 0.95 * self.volt_last
                currTemp = 0.2 * currTemp + 0.8 * self.curr_last
                self.volt_last = voltTemp
                self.curr_last = currTemp
                self.readings["voltage"] = voltTemp
                self.readings["current"] = currTemp
            self.altitude = self.calcAltitude() - self.altitudeOffset
        except:
            print "invalid data"
    
    def calcAltitude(self,p0=102300.0):
        return (int(44330*(1-(self.readings["pressure"]/p0)**(1/5.255)))
                if self.readings["pressure"] > 0 else 0)
    
    def simulateInputs(self):
        randNum = random.randint(0, 100)
        
        if self.pitchUp:
            self.readings["pitch"] += 1
            if (self.readings["pitch"] == 90):
                self.pitchUp = False
                self.readings["roll"] += 180
        else:
            self.readings["pitch"] -= 1
            if (self.readings["pitch"] == -90):
                self.pitchUp = True
                self.readings["roll"] += 180
            
        self.readings["roll"] += 1
        if(self.readings["roll"] >= 180): self.readings["roll"] -= 360
        
        self.readings["heading"] += 1
        if self.readings["heading"] == 360: self.readings["heading"] = 0
        
        self.readings["mAh"] += 2
        if self.readings["mAh"] >= 2200: self.readings["mAh"] = 0
        
        if self.speedUp:
            self.readings["current"] += 1
            if self.readings["current"] >= 20:
                self.readings["current"] == 19
                self.speedUp = False
        else:
            self.readings["current"] -= 1
            if self.readings["current"] <= 0:
                self.readings["current"] == 1
                self.speedUp = True

class myThread(threading.Thread):
    def __init__(self,GroundStation):
        self.gndStation = GroundStation
        threading.Thread.__init__(self)
        
    def run(self):
        while(not self.gndStation.exitFlag):
            time.sleep(0.04)
            #self.gndStation.simulateInputs()
            #if(self.gndStation.COM.inWaiting() != 0):
            #    self.gndStation.updateReadings()
