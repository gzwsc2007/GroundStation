# This module handles flight data inputs and generate useful outpus for
# the GUI module to function.

import math
import random
import threading
import time
import os
import serial
import pickle
import copy

import customMavlinkv10


class DataInput(object):
    def __init__(self):
        # path of the script being run
        self.cwd = os.path.dirname(os.path.abspath(__file__))

        # For roll: left-down is positive; For Pitch: forward-upward is positive.
        # For pitch: range should be between -pi/2 and pi/2 (think of
        # spherical coordinates!!!!)
        self.data = {
                    # 25 Hz data
                    "roll":0.0, # [-180, 180) degrees, positive is CCW
                    "pitch":0.0, # [-90, 90) degrees, positive is upward
                    "yaw":0.0, # [0, 360) degrees
                    "altitude":0, # meters
                    "airspeed":0, # m/s
                    # 5 Hz data
                    "battV":0.0, # Volt (0.01 accuracy)
                    "battI":0.0, # Amp (0.01 accuracy)
                    "temperature":0.0, # Celcius (0.1 accruacy)
                    "latitude":0.0, # degrees (10^-7 deg accuracy), positive is N
                    "longitude":0.0, # degrees (10^-7 deg accuracy), positive is E
                    "course":0, # [0, 360) degrees
                    "groundspeed":0, # m/s
                    # local data
                    "mAh":0
                    }
        
        # A list of beacon coordinates. 
        # These beacons will be displayed on the Navigation Display
        self.beaconCoords = [] # beacon GPS coords: (long, lat) tuples
        self.beacons = [] # converted format of beacons: [name, dir, distance] sub-lists

        # For simulation purposes
        self.pitchUp = True
        self.rollRight = True
        self.speedUp = True
        
        # initialize Serial com
        #self.COM = serial.Serial(2,115200) # COM3
        #self.COM.flushInput() # flush input buffer
        
        self.altitude = 0
        self.altitudeOffset = 0
        self.aspdOffset = 0
        self.batt_capacity = 2200    # default battery capacity 2200 mAh
        self.volt_last = 0
        self.curr_last = 0
        self.roll_last = 0
        self.pitch_last = 0
        self.timeLast = time.time()
        
        self.EN_ALT_OFFSET = False # enable relative altitude mode
        self.LPF = True # enable local Low-Pass-Filter
        self.first5HzSample = True
        self.first25HzSample = True
        self.exitFlag = False
        self.logEnable = False
        thread = myThread(self)
        thread.start()
    
    # update the beacons list based on current position & heading of the aircraft
    # Source: www.movable-type.co.uk/scripts/latlong.html
    def updateBeacons(self):
        lat0, lon0 = math.radians(self.data["latitude"]), math.radians(self.data["longitude"])
        
        i = 0
        for coord in self.beaconCoords:
            # calculate distance
            lat, lon = math.radians(coord[1]), math.radians(coord[0])
            dlat = math.radians(coord[1] - self.data["latitude"])
            dlon = math.radians(coord[0] - self.data["longitude"])
            a = (math.sin(dlat / 2.0)) ** 2 + math.cos(lat0) * math.cos(lat) * ((math.sin(dlon / 2.0)) ** 2)
            c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
            d = 6375000 * c # earth's mean radius is 6371 km

            # calculate bearing (forward azimuth)
            y = math.sin(lon - lon0) * math.cos(lat)
            x = math.cos(lat0) * math.sin(lat) - math.sin(lat0) * math.cos(lat) * math.cos(lon - lon0)
            brng = math.degrees(math.atan2(y, x))
            brng = (brng + 360) % 360

            dbrng = brng - self.data["course"]

            self.beacons[i][1] = (dbrng + 360) % 360
            self.beacons[i][2] = abs(d)

            i += 1

    def update25HzData(self, PFDStruct):
        rollTemp = PFDStruct.roll # in 0.01 deg
        pitchTemp = PFDStruct.pitch # in 0.01 deg
        yawTemp = PFDStruct.yaw # in 0.01 deg
        altitudeTemp = PFDStruct.altitude
        airspeedTemp = PFDStruct.airspeed

        # apply local Low-Pass-Filter if necessary
        if (self.LPF):
            if (self.first25HzSample):
                self.roll_last = rollTemp
                self.pitch_last = pitchTemp
                self.yaw_last = yawTemp
                self.airspeed_last = airspeedTemp
                self.altitude_last = altitudeTemp
                self.first25HzSample = False
            else:
                rollTemp = 0.5 * rollTemp + 0.5 * self.roll_last
                pitchTemp = 0.5 * pitchTemp + 0.5 * self.pitch_last
                yawTemp = 0.5 * yawTemp + 0.5 * self.yaw_last
                yawTemp = 0.01 * self.data["course"] + 0.99 * yawTemp
                airspeedTemp = 0.15 * airspeedTemp + 0.85 * self.airspeed_last
                altitudeTemp = 0.25 * altitudeTemp + 0.75 * self.altitude_last

                self.roll_last = rollTemp
                self.pitch_last = pitchTemp
                self.yaw_last = yawTemp
                self.airspeed_last = airspeedTemp
                self.altitude_last = altitudeTemp

        self.data["roll"] = rollTemp / 100.0
        self.data["pitch"] = pitchTemp / 100.0
        self.data["yaw"] = yawTemp / 100.0
        if self.data["yaw"] < 0: self.data["yaw"] += 360.0
        self.data["altitude"] = altitudeTemp - self.altitudeOffset
        self.altitude = altitudeTemp
        self.data["airspeed"] = airspeedTemp / 10.0 - self.aspdOffset
    
    def update5HzData(self, NavDStruct):
        voltTemp = NavDStruct.battV / 100.0 + 0.07 # system error
        currTemp = NavDStruct.battI / 100.0

        if (self.LPF):
            if (self.first5HzSample):
                self.volt_last = voltTemp
                self.curr_last = currTemp
                self.first5HzSample = False
            else:
                # apply low pass filter to voltage and current sensing
                voltTemp = 0.2 * voltTemp + 0.8 * self.volt_last
                currTemp = 0.5 * currTemp + 0.5 * self.curr_last
                self.curr_last = currTemp
                self.volt_last = voltTemp
        
        self.data["battV"] = voltTemp
        self.data["battI"] = currTemp # instantaneous current
        self.data["temperature"] = float(NavDStruct.temp) / 10.0
        self.data["latitude"] = float(NavDStruct.latitude) / 10000000.0
        self.data["longitude"] = float(NavDStruct.longitude) / 10000000.0
        self.data["course"] = float(NavDStruct.course) / 100.0
        self.data["groundspeed"] = float(NavDStruct.groundspeed) / 100.0

    def simulateInputs(self):
        randNum = random.randint(0, 100)
        
        if self.pitchUp:
            self.data["pitch"] += 0.5
            if (self.data["pitch"] >= 45):
                self.pitchUp = False
                #self.data["roll"] += 180
        else:
            self.data["pitch"] -= 0.5
            if (self.data["pitch"] <= -45):
                self.pitchUp = True
                #self.data["roll"] += 180
        
        if self.rollRight:  
            self.data["roll"] += 0.5
            if(self.data["roll"] >= 45): self.rollRight = False#self.data["roll"] -= 360
        else:
            self.data["roll"] -= 0.5
            if(self.data["roll"] <= -45): self.rollRight = True
        
        self.data["yaw"] += 1
        if self.data["yaw"] == 360: self.data["yaw"] = 0
        self.data["course"] = self.data["yaw"]
        
        if self.speedUp:
            self.data["battI"] += 1
            if self.data["battI"] >= 20:
                self.data["battI"] == 19
                self.speedUp = False
        else:
            self.data["battI"] -= 1
            if self.data["battI"] <= 0:
                self.data["battI"] == 1
                self.speedUp = True

        self.data["groundspeed"] = self.data["battI"]
        self.data["altitude"] += 1
        self.data["airspeed"] += 0.1

        self.data["latitude"] += 0.000001
        #self.data["longitude"] += 0.0000005

    def startLogging(self):
        self.logList = []
        self.logEnable = True
        self.lastLogTime = time.time()

    def stopLogging(self):
        self.logEnable = False
        f = open("log.pkl", "w+")
        pickle.dump(self.logList, f)

    def doLog(self):
        if (self.logEnable):
            tnow = time.time()
            if (tnow - self.lastLogTime >= 2000.0):
                self.logList.append((tnow, copy.deepcopy(self.data)))
                self.lastLogTime = tnow

class myThread(threading.Thread):
    def __init__(self,parent):
        self.parent = parent
        threading.Thread.__init__(self)
        # create the protocol handling class
        self.mavlink = customMavlinkv10.MAVLink(open("mavlinkDummy.txt", 'w+')) 
        
    def run(self):
        while(not self.parent.exitFlag):
            time.sleep(0.04)
            self.parent.simulateInputs()
            self.parent.updateBeacons()
            '''
            n = self.parent.COM.inWaiting()
            if(n != 0):
                bytes = self.parent.COM.read(n)
                msg_list = self.mavlink.parse_buffer(bytes)
                if msg_list != None:
                    for msg in msg_list:
                        if (isinstance(msg, customMavlinkv10.MAVLink_pfd_message)):
                            self.parent.update25HzData(msg)
                        elif (isinstance(msg, customMavlinkv10.MAVLink_navd_message)):
                            self.parent.update5HzData(msg)
                            self.parent.updateBeacons()
            else:
                time.sleep(0.05)
            '''
            self.parent.doLog()
            