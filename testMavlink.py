import customMavlinkv10
import serial, time

mavlink = customMavlinkv10.MAVLink(open("stupid.txt", 'w+')) # create the protocol handling class

ser = serial.Serial(2,115200)
tlast = time.time()

# parsing loop
while(True):
	n = ser.inWaiting() # returns the number of bytes available
	if(n != 0):
		s = ser.read(n)
		msg = mavlink.parse_char(s)

		if isinstance(msg, customMavlinkv10.MAVLink_navd_message):
			print time.time()-tlast, msg.temp
			tlast = time.time()