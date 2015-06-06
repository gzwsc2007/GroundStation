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

import MAVLink.MAVLink as MAVLink

class HACS_Proxy(object):
    HACS_GND_CMD_SET_MODE = 0
    HACS_GND_CMD_GET_MODE = 1

    HACS_MODE_MANUAL = 0
    HACS_MODE_MANUAL_WITH_SAS = 1
    HACS_MODE_AUTOPILOT = 2
    HACS_MODE_SYSTEM_IDENTIFICATION = 3
    HACS_MODE_MAG_CAL = 4


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
                    "mAh":0,
                    "verticalspeed":0
                    }

        # A list of beacon coordinates.
        # These beacons will be displayed on the Navigation Display
        self.homeCoordRad = (0, 0) # (long, lat) tuple
        self.homeCoordDeg = (0, 0)
        self.homeBearing = 0 # heading of the ground station
        self.beaconCoords = [(0, 0)] # beacon GPS coords: (long, lat) tuples. index 0 is the craft position
        self.beacons = [["Craft", 0, 0]] # converted format of beacons: [name, dir, distance] sub-lists

        # For simulation purposes
        self.pitchUp = True
        self.rollRight = True
        self.speedUp = True

        # initialize Serial com
        self.COM = serial.Serial(1,115200*2) # COM2
        self.COM.flushInput() # flush input buffer

        # initialize MAVLink protocol
        self.mavlink = MAVLink.MAVLink(self.COM)

        self.altitude = 0
        self.altitudeOffset = 0
        self.aspdOffset = 0
        self.batt_capacity = 5000    # default battery capacity 5000 mAh
        self.volt_last = 0
        self.curr_last = 0
        self.roll_last = 0
        self.pitch_last = 0
        self.vs_last = 0
        self.timeLast = 0

        self.EN_ALT_OFFSET = False # enable relative altitude mode
        self.LPF = True # enable local Low-Pass-Filter
        self.first5HzSample = True
        self.first25HzSample = True
        self.exitFlag = False
        self.logEnable = False

        thread = myThread(self, self.mavlink)
        thread.start()

    # update the beacons list based on current position & heading of the aircraft
    # Source: www.movable-type.co.uk/scripts/latlong.html
    def updateBeacons(self):
        lon0, lat0 = self.homeCoordRad
        self.beaconCoords[0] = (self.data["longitude"], self.data["latitude"])

        i = 0
        for coord in self.beaconCoords:
            # calculate distance
            lat, lon = math.radians(coord[1]), math.radians(coord[0])
            dlat = math.radians(coord[1] - self.homeCoordDeg[1])
            dlon = math.radians(coord[0] - self.homeCoordDeg[0])
            a = (math.sin(dlat / 2.0)) ** 2 + math.cos(lat0) * math.cos(lat) * ((math.sin(dlon / 2.0)) ** 2)
            c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
            d = 6375000 * c # earth's mean radius is 6371 km

            # calculate bearing (forward azimuth)
            y = math.sin(lon - lon0) * math.cos(lat)
            x = math.cos(lat0) * math.sin(lat) - math.sin(lat0) * math.cos(lat) * math.cos(lon - lon0)
            brng = math.degrees(math.atan2(y, x))
            brng = (brng + 360) % 360

            dbrng = brng - self.homeBearing

            self.beacons[i][1] = (dbrng + 360) % 360
            self.beacons[i][2] = abs(d)

            i += 1

    def update25HzData(self, PFDStruct):
        rollTemp = PFDStruct.roll # in 0.01 deg
        pitchTemp = PFDStruct.pitch # in 0.01 deg
        yawTemp = PFDStruct.yaw # in 0.01 deg
        altitudeTemp = PFDStruct.altitude / 10.0
        airspeedTemp = PFDStruct.airspeed
        currTemp = PFDStruct.battI / 10.0

        # apply local Low-Pass-Filter if necessary
        if (self.LPF):
            if (self.first25HzSample):
                self.roll_last = rollTemp
                self.pitch_last = pitchTemp
                self.yaw_last = yawTemp
                self.airspeed_last = airspeedTemp
                self.altitude_last = altitudeTemp
                self.curr_last = currTemp
                self.timeLast = time.time()
                self.first25HzSample = False
            else:
                rollTemp = 0.5 * rollTemp + 0.5 * self.roll_last
                pitchTemp = 0.5 * pitchTemp + 0.5 * self.pitch_last
                yawTemp = 0.5 * yawTemp + 0.5 * self.yaw_last
                yawTemp = 0.01 * self.data["course"] + 0.99 * yawTemp
                airspeedTemp = 0.15 * airspeedTemp + 0.85 * self.airspeed_last
                altitudeTemp = 0.15 * altitudeTemp + 0.85 * self.altitude_last
                currTemp = 0.1 * currTemp + 0.9 * self.curr_last

                self.curr_last = currTemp
                self.roll_last = rollTemp
                self.pitch_last = pitchTemp
                self.yaw_last = yawTemp
                self.airspeed_last = airspeedTemp

        self.data["roll"] = rollTemp / 100.0
        self.data["pitch"] = pitchTemp / 100.0
        self.data["yaw"] = yawTemp / 100.0
        if self.data["yaw"] < 0: self.data["yaw"] += 360.0
        self.data["altitude"] = altitudeTemp - self.altitudeOffset
        self.altitude = altitudeTemp
        self.data["airspeed"] = airspeedTemp / 10.0 - self.aspdOffset
        self.data["battI"] = currTemp

        tnow = time.time()
        self.data["mAh"] += currTemp * (tnow - self.timeLast) * 0.2777778
        if tnow != self.timeLast:
            vsTemp = (altitudeTemp - self.altitude_last) / (tnow - self.timeLast)
            if abs(vsTemp - self.vs_last) > 2: vsTemp *= 0.1
            self.data["verticalspeed"] = vsTemp * 0.05 + self.vs_last * 0.95
            self.vs_last = self.data["verticalspeed"]
            self.timeLast = tnow

        self.altitude_last = altitudeTemp


    def update5HzData(self, NavDStruct):
        voltTemp = NavDStruct.battV / 100.0 + 0.07 # system error

        if (self.LPF):
            if (self.first5HzSample):
                self.volt_last = voltTemp
                self.first5HzSample = False
            else:
                # apply low pass filter to voltage and current sensing
                voltTemp = 0.2 * voltTemp + 0.8 * self.volt_last
                self.volt_last = voltTemp

        self.data["battV"] = voltTemp
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
        self.data["verticalspeed"] = -5.0

    def startLogging(self):
        print "start logging"
        self.logList = []
        self.logEnable = True
        self.lastLogTime = time.time()

    def stopLogging(self):
        print "stop logging. List length: ",
        print len(self.logList)
        self.logEnable = False
        f = open("log_%s.pkl"%time.strftime("%Y-%m-%d_%H_%M_%S"), "w+")
        pickle.dump(self.logList, f)

    def startMagCal(self):
        self.mavlink.syscmd_send(HACS_Proxy.HACS_GND_CMD_SET_MODE, HACS_Proxy.HACS_MODE_MAG_CAL)

    def stopMagCal(self):
        self.mavlink.syscmd_send(HACS_Proxy.HACS_GND_CMD_SET_MODE, HACS_Proxy.HACS_MODE_MANUAL)

    def doLog(self):
        if (self.logEnable):
            tnow = time.time()
            if (tnow - self.lastLogTime >= 0.05):
                self.logList.append((tnow, copy.deepcopy(self.data)))
                self.lastLogTime = tnow

class myThread(threading.Thread):
    def __init__(self,parent,mavlink):
        self.parent = parent
        threading.Thread.__init__(self)
        # create the protocol handling class
        self.mavlink = mavlink
        #self.replayList = pickle.load(open("../flight_log/log_2014-07-02_11_26_39.pkl","r"))

    def doReplay(self):
        length = len(self.replayList)
        dictLen = len(self.parent.data)
        self.homeCoordDeg = self.replayList[0][1]["longitude"], self.replayList[0][1]["latitude"]
        self.homeCoordRad = math.radians(self.homeCoordDeg[0]), math.radians(self.homeCoordDeg[1])

        for index in xrange(length-1):
            d = self.replayList[index][1]
            self.parent.data["roll"] = d["roll"]
            self.parent.data["pitch"] = d["pitch"]
            self.parent.data["yaw"] = d["yaw"]
            self.parent.data["altitude"] = d["altitude"]
            self.parent.data["airspeed"] = d["airspeed"]
            self.parent.data["battV"] = d["battV"]
            self.parent.data["battI"] = d["battI"]
            self.parent.data["temperature"] = d["temperature"]
            self.parent.data["latitude"] = d["latitude"]
            self.parent.data["longitude"] = d["longitude"]
            self.parent.data["course"] = d["course"]
            self.parent.data["groundspeed"] = d["groundspeed"]
            self.parent.data["mAh"] = d["mAh"]
            self.parent.data["verticalspeed"] = d["verticalspeed"]

            nextWaitTime = self.replayList[index+1][0] - self.replayList[index][0]
            self.parent.updateBeacons()

            time.sleep(nextWaitTime)
            if (self.parent.exitFlag): break

    def run(self):
#        tLast = time.time()
        while(not self.parent.exitFlag):
            # uncomment the following to enable simulation
            #time.sleep(0.04)
            #self.parent.simulateInputs()
            #self.parent.updateBeacons()

            n = self.parent.COM.inWaiting()
            if(n != 0):
                bytes = self.parent.COM.read(n)
                msg_list = self.mavlink.parse_buffer(bytes)
                if msg_list != None:
                    for msg in msg_list:
                        if (isinstance(msg, MAVLink.MAVLink_pfd_message)):
#                            tNow = time.time()
#                            print tNow - tLast
#                            tLast = tNow
                            self.parent.update25HzData(msg)
                        elif (isinstance(msg, MAVLink.MAVLink_navd_message)):
                            self.parent.update5HzData(msg)
                            self.parent.updateBeacons()
                        elif (isinstance(msg, MAVLink.MAVLink_magcal_message)):
                            print "%d %d %d"%(msg.mx,msg.my,msg.mz)
            else:
                time.sleep(0.025)

            self.parent.doLog()

            #self.doReplay()