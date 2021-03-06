'''
MAVLink protocol implementation (auto-generated by mavgen.py)

Generated from: hacs.xml

Note: this file has been auto-generated. DO NOT EDIT
'''

import struct, array, time, json, os, sys, platform

from mavcrc import x25crc

WIRE_PROTOCOL_VERSION = "1.0"
DIALECT = "MAVLink"

native_supported = platform.system() != 'Windows' # Not yet supported on other dialects
native_force = 'MAVNATIVE_FORCE' in os.environ # Will force use of native code regardless of what client app wants
native_testing = 'MAVNATIVE_TESTING' in os.environ # Will force both native and legacy code to be used and their results compared

if native_supported:
    try:
        import mavnative
    except ImportError:
        print("ERROR LOADING MAVNATIVE - falling back to python implementation")
        native_supported = False

# some base types from mavlink_types.h
MAVLINK_TYPE_CHAR     = 0
MAVLINK_TYPE_UINT8_T  = 1
MAVLINK_TYPE_INT8_T   = 2
MAVLINK_TYPE_UINT16_T = 3
MAVLINK_TYPE_INT16_T  = 4
MAVLINK_TYPE_UINT32_T = 5
MAVLINK_TYPE_INT32_T  = 6
MAVLINK_TYPE_UINT64_T = 7
MAVLINK_TYPE_INT64_T  = 8
MAVLINK_TYPE_FLOAT    = 9
MAVLINK_TYPE_DOUBLE   = 10


class MAVLink_header(object):
    '''MAVLink message header'''
    def __init__(self, msgId, mlen=0, seq=0, srcSystem=0, srcComponent=0):
        self.mlen = mlen
        self.seq = seq
        self.srcSystem = srcSystem
        self.srcComponent = srcComponent
        self.msgId = msgId

    def pack(self):
        return struct.pack('BBBBBB', 254, self.mlen, self.seq,
                          self.srcSystem, self.srcComponent, self.msgId)

class MAVLink_message(object):
    '''base MAVLink message class'''
    def __init__(self, msgId, name):
        self._header     = MAVLink_header(msgId)
        self._payload    = None
        self._msgbuf     = None
        self._crc        = None
        self._fieldnames = []
        self._type       = name

    def get_msgbuf(self):
        if isinstance(self._msgbuf, bytearray):
            return self._msgbuf
        return bytearray(self._msgbuf)

    def get_header(self):
        return self._header

    def get_payload(self):
        return self._payload

    def get_crc(self):
        return self._crc

    def get_fieldnames(self):
        return self._fieldnames

    def get_type(self):
        return self._type

    def get_msgId(self):
        return self._header.msgId

    def get_srcSystem(self):
        return self._header.srcSystem

    def get_srcComponent(self):
        return self._header.srcComponent

    def get_seq(self):
        return self._header.seq

    def __str__(self):
        ret = '%s {' % self._type
        for a in self._fieldnames:
            v = getattr(self, a)
            ret += '%s : %s, ' % (a, v)
        ret = ret[0:-2] + '}'
        return ret

    def __ne__(self, other):
        return not self.__eq__(other)

    def __eq__(self, other):
        if other == None:
            return False

        if self.get_type() != other.get_type():
            return False

        # We do not compare CRC because native code doesn't provide it
        #if self.get_crc() != other.get_crc():
        #    return False

        if self.get_seq() != other.get_seq():
            return False

        if self.get_srcSystem() != other.get_srcSystem():
            return False            

        if self.get_srcComponent() != other.get_srcComponent():
            return False   
            
        for a in self._fieldnames:
            if getattr(self, a) != getattr(other, a):
                return False

        return True

    def to_dict(self):
        d = dict({})
        d['mavpackettype'] = self._type
        for a in self._fieldnames:
          d[a] = getattr(self, a)
        return d

    def to_json(self):
        return json.dumps(self.to_dict())

    def pack(self, mav, crc_extra, payload):
        self._payload = payload
        self._header  = MAVLink_header(self._header.msgId, len(payload), mav.seq,
                                       mav.srcSystem, mav.srcComponent)
        self._msgbuf = self._header.pack() + payload
        crc = x25crc(self._msgbuf[1:])
        if True: # using CRC extra
            crc.accumulate_str(chr(crc_extra))
        self._crc = crc.crc
        self._msgbuf += struct.pack('<H', self._crc)
        return self._msgbuf


# enums

class EnumEntry(object):
    def __init__(self, name, description):
        self.name = name
        self.description = description
        self.param = {}
        
enums = {}

# message IDs
MAVLINK_MSG_ID_BAD_DATA = -1
MAVLINK_MSG_ID_PFD = 150
MAVLINK_MSG_ID_NAVD = 151
MAVLINK_MSG_ID_SYSTEMID = 152
MAVLINK_MSG_ID_MAGCAL = 153
MAVLINK_MSG_ID_SYSSTATE = 154
MAVLINK_MSG_ID_SYSCMD = 155
MAVLINK_MSG_ID_MAGCALRESULT = 156

class MAVLink_pfd_message(MAVLink_message):
        '''
        This message encodes data needed for the GroundStation Primary
        Flight Display. Should be sent at 20Hz.
        '''
        id = MAVLINK_MSG_ID_PFD
        name = 'PFD'
        fieldnames = ['roll', 'pitch', 'yaw', 'altitude', 'airspeed', 'battI']
        ordered_fieldnames = [ 'roll', 'pitch', 'yaw', 'altitude', 'airspeed', 'battI' ]
        format = '<hhhhhh'
        native_format = bytearray('<hhhhhh', 'ascii')
        orders = [0, 1, 2, 3, 4, 5]
        lengths = [1, 1, 1, 1, 1, 1]
        array_lengths = [0, 0, 0, 0, 0, 0]
        crc_extra = 6

        def __init__(self, roll, pitch, yaw, altitude, airspeed, battI):
                MAVLink_message.__init__(self, MAVLink_pfd_message.id, MAVLink_pfd_message.name)
                self._fieldnames = MAVLink_pfd_message.fieldnames
                self.roll = roll
                self.pitch = pitch
                self.yaw = yaw
                self.altitude = altitude
                self.airspeed = airspeed
                self.battI = battI

        def pack(self, mav):
                return MAVLink_message.pack(self, mav, 6, struct.pack('<hhhhhh', self.roll, self.pitch, self.yaw, self.altitude, self.airspeed, self.battI))

class MAVLink_navd_message(MAVLink_message):
        '''
        This message encodes data needed for the GroundStation
        Navigation Display. Should be sent at 5Hz.
        '''
        id = MAVLINK_MSG_ID_NAVD
        name = 'NAVD'
        fieldnames = ['battV', 'temp', 'latitude', 'longitude', 'course', 'groundspeed']
        ordered_fieldnames = [ 'latitude', 'longitude', 'battV', 'temp', 'course', 'groundspeed' ]
        format = '<iihhHH'
        native_format = bytearray('<iihhHH', 'ascii')
        orders = [2, 3, 0, 1, 4, 5]
        lengths = [1, 1, 1, 1, 1, 1]
        array_lengths = [0, 0, 0, 0, 0, 0]
        crc_extra = 109

        def __init__(self, battV, temp, latitude, longitude, course, groundspeed):
                MAVLink_message.__init__(self, MAVLink_navd_message.id, MAVLink_navd_message.name)
                self._fieldnames = MAVLink_navd_message.fieldnames
                self.battV = battV
                self.temp = temp
                self.latitude = latitude
                self.longitude = longitude
                self.course = course
                self.groundspeed = groundspeed

        def pack(self, mav):
                return MAVLink_message.pack(self, mav, 109, struct.pack('<iihhHH', self.latitude, self.longitude, self.battV, self.temp, self.course, self.groundspeed))

class MAVLink_systemid_message(MAVLink_message):
        '''
        This message encodes all the data needed for System
        Identification.
        '''
        id = MAVLINK_MSG_ID_SYSTEMID
        name = 'SYSTEMID'
        fieldnames = ['timestamp', 'u_a', 'u_e', 'u_r', 'ax', 'ay', 'az', 'roll', 'pitch', 'yaw', 'p', 'q', 'r']
        ordered_fieldnames = [ 'timestamp', 'u_a', 'u_e', 'u_r', 'ax', 'ay', 'az', 'roll', 'pitch', 'yaw', 'p', 'q', 'r' ]
        format = '<Ihhhhhhhhhhhh'
        native_format = bytearray('<Ihhhhhhhhhhhh', 'ascii')
        orders = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
        lengths = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
        array_lengths = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        crc_extra = 217

        def __init__(self, timestamp, u_a, u_e, u_r, ax, ay, az, roll, pitch, yaw, p, q, r):
                MAVLink_message.__init__(self, MAVLink_systemid_message.id, MAVLink_systemid_message.name)
                self._fieldnames = MAVLink_systemid_message.fieldnames
                self.timestamp = timestamp
                self.u_a = u_a
                self.u_e = u_e
                self.u_r = u_r
                self.ax = ax
                self.ay = ay
                self.az = az
                self.roll = roll
                self.pitch = pitch
                self.yaw = yaw
                self.p = p
                self.q = q
                self.r = r

        def pack(self, mav):
                return MAVLink_message.pack(self, mav, 217, struct.pack('<Ihhhhhhhhhhhh', self.timestamp, self.u_a, self.u_e, self.u_r, self.ax, self.ay, self.az, self.roll, self.pitch, self.yaw, self.p, self.q, self.r))

class MAVLink_magcal_message(MAVLink_message):
        '''
        This message encodes raw magnetometer data.
        '''
        id = MAVLINK_MSG_ID_MAGCAL
        name = 'MAGCAL'
        fieldnames = ['mx', 'my', 'mz']
        ordered_fieldnames = [ 'mx', 'my', 'mz' ]
        format = '<hhh'
        native_format = bytearray('<hhh', 'ascii')
        orders = [0, 1, 2]
        lengths = [1, 1, 1]
        array_lengths = [0, 0, 0]
        crc_extra = 75

        def __init__(self, mx, my, mz):
                MAVLink_message.__init__(self, MAVLink_magcal_message.id, MAVLink_magcal_message.name)
                self._fieldnames = MAVLink_magcal_message.fieldnames
                self.mx = mx
                self.my = my
                self.mz = mz

        def pack(self, mav):
                return MAVLink_message.pack(self, mav, 75, struct.pack('<hhh', self.mx, self.my, self.mz))

class MAVLink_sysstate_message(MAVLink_message):
        '''
        This message encodes the current system status.
        '''
        id = MAVLINK_MSG_ID_SYSSTATE
        name = 'SYSSTATE'
        fieldnames = ['mode']
        ordered_fieldnames = [ 'mode' ]
        format = '<B'
        native_format = bytearray('<B', 'ascii')
        orders = [0]
        lengths = [1]
        array_lengths = [0]
        crc_extra = 196

        def __init__(self, mode):
                MAVLink_message.__init__(self, MAVLink_sysstate_message.id, MAVLink_sysstate_message.name)
                self._fieldnames = MAVLink_sysstate_message.fieldnames
                self.mode = mode

        def pack(self, mav):
                return MAVLink_message.pack(self, mav, 196, struct.pack('<B', self.mode))

class MAVLink_syscmd_message(MAVLink_message):
        '''
        This message encodes commands sent by the ground station.
        '''
        id = MAVLINK_MSG_ID_SYSCMD
        name = 'SYSCMD'
        fieldnames = ['cmd', 'payload']
        ordered_fieldnames = [ 'payload', 'cmd' ]
        format = '<IB'
        native_format = bytearray('<IB', 'ascii')
        orders = [1, 0]
        lengths = [1, 1]
        array_lengths = [0, 0]
        crc_extra = 109

        def __init__(self, cmd, payload):
                MAVLink_message.__init__(self, MAVLink_syscmd_message.id, MAVLink_syscmd_message.name)
                self._fieldnames = MAVLink_syscmd_message.fieldnames
                self.cmd = cmd
                self.payload = payload

        def pack(self, mav):
                return MAVLink_message.pack(self, mav, 109, struct.pack('<IB', self.payload, self.cmd))

class MAVLink_magcalresult_message(MAVLink_message):
        '''
        This message encodes magnetometer calibration results.
        '''
        id = MAVLINK_MSG_ID_MAGCALRESULT
        name = 'MAGCALRESULT'
        fieldnames = ['B_field', 'hard_iron', 'soft_iron']
        ordered_fieldnames = [ 'B_field', 'hard_iron', 'soft_iron' ]
        format = '<f3f9f'
        native_format = bytearray('<fff', 'ascii')
        orders = [0, 1, 2]
        lengths = [1, 3, 9]
        array_lengths = [0, 3, 9]
        crc_extra = 96

        def __init__(self, B_field, hard_iron, soft_iron):
                MAVLink_message.__init__(self, MAVLink_magcalresult_message.id, MAVLink_magcalresult_message.name)
                self._fieldnames = MAVLink_magcalresult_message.fieldnames
                self.B_field = B_field
                self.hard_iron = hard_iron
                self.soft_iron = soft_iron

        def pack(self, mav):
                return MAVLink_message.pack(self, mav, 96, struct.pack('<f3f9f', self.B_field, self.hard_iron[0], self.hard_iron[1], self.hard_iron[2], self.soft_iron[0], self.soft_iron[1], self.soft_iron[2], self.soft_iron[3], self.soft_iron[4], self.soft_iron[5], self.soft_iron[6], self.soft_iron[7], self.soft_iron[8]))


mavlink_map = {
        MAVLINK_MSG_ID_PFD : MAVLink_pfd_message,
        MAVLINK_MSG_ID_NAVD : MAVLink_navd_message,
        MAVLINK_MSG_ID_SYSTEMID : MAVLink_systemid_message,
        MAVLINK_MSG_ID_MAGCAL : MAVLink_magcal_message,
        MAVLINK_MSG_ID_SYSSTATE : MAVLink_sysstate_message,
        MAVLINK_MSG_ID_SYSCMD : MAVLink_syscmd_message,
        MAVLINK_MSG_ID_MAGCALRESULT : MAVLink_magcalresult_message,
}

class MAVError(Exception):
        '''MAVLink error class'''
        def __init__(self, msg):
            Exception.__init__(self, msg)
            self.message = msg

class MAVString(str):
        '''NUL terminated string'''
        def __init__(self, s):
                str.__init__(self)
        def __str__(self):
            i = self.find(chr(0))
            if i == -1:
                return self[:]
            return self[0:i]

class MAVLink_bad_data(MAVLink_message):
        '''
        a piece of bad data in a mavlink stream
        '''
        def __init__(self, data, reason):
                MAVLink_message.__init__(self, MAVLINK_MSG_ID_BAD_DATA, 'BAD_DATA')
                self._fieldnames = ['data', 'reason']
                self.data = data
                self.reason = reason
                self._msgbuf = data

        def __str__(self):
            '''Override the __str__ function from MAVLink_messages because non-printable characters are common in to be the reason for this message to exist.'''
            return '%s {%s, data:%s}' % (self._type, self.reason, [('%x' % ord(i) if isinstance(i, str) else '%x' % i) for i in self.data])

class MAVLink(object):
        '''MAVLink protocol handling class'''
        def __init__(self, file, srcSystem=0, srcComponent=0, use_native=False):
                self.seq = 0
                self.file = file
                self.srcSystem = srcSystem
                self.srcComponent = srcComponent
                self.callback = None
                self.callback_args = None
                self.callback_kwargs = None
                self.send_callback = None
                self.send_callback_args = None
                self.send_callback_kwargs = None
                self.buf = bytearray()
                self.expected_length = 8
                self.have_prefix_error = False
                self.robust_parsing = False
                self.protocol_marker = 254
                self.little_endian = True
                self.crc_extra = True
                self.sort_fields = True
                self.total_packets_sent = 0
                self.total_bytes_sent = 0
                self.total_packets_received = 0
                self.total_bytes_received = 0
                self.total_receive_errors = 0
                self.startup_time = time.time()
                if native_supported and (use_native or native_testing or native_force):
                    print("NOTE: mavnative is currently beta-test code")
                    self.native = mavnative.NativeConnection(MAVLink_message, mavlink_map)
                else:
                    self.native = None
                if native_testing:
                    self.test_buf = bytearray()

        def set_callback(self, callback, *args, **kwargs):
            self.callback = callback
            self.callback_args = args
            self.callback_kwargs = kwargs

        def set_send_callback(self, callback, *args, **kwargs):
            self.send_callback = callback
            self.send_callback_args = args
            self.send_callback_kwargs = kwargs

        def send(self, mavmsg):
                '''send a MAVLink message'''
                buf = mavmsg.pack(self)
                self.file.write(buf)
                self.seq = (self.seq + 1) % 256
                self.total_packets_sent += 1
                self.total_bytes_sent += len(buf)
                if self.send_callback:
                    self.send_callback(mavmsg, *self.send_callback_args, **self.send_callback_kwargs)

        def bytes_needed(self):
            '''return number of bytes needed for next parsing stage'''
            if self.native:
                ret = self.native.expected_length - len(self.buf)
            else:
                ret = self.expected_length - len(self.buf)
            
            if ret <= 0:
                return 1
            return ret

        def __parse_char_native(self, c):
            '''this method exists only to see in profiling results'''
            m = self.native.parse_chars(c)
            return m

        def __callbacks(self, msg):
            '''this method exists only to make profiling results easier to read'''
            if self.callback:
                self.callback(msg, *self.callback_args, **self.callback_kwargs)

        def parse_char(self, c):
            '''input some data bytes, possibly returning a new message'''
            self.buf.extend(c)

            self.total_bytes_received += len(c)

            if self.native:
                if native_testing:
                    self.test_buf.extend(c)
                    m = self.__parse_char_native(self.test_buf)
                    m2 = self.__parse_char_legacy()
                    if m2 != m:
                        print("Native: %s\nLegacy: %s\n" % (m, m2))
                        raise Exception('Native vs. Legacy mismatch')
                else:
                    m = self.__parse_char_native(self.buf)
            else:
                m = self.__parse_char_legacy()

            if m != None:
                self.total_packets_received += 1
                self.__callbacks(m)

            return m

        def __parse_char_legacy(self):
            '''input some data bytes, possibly returning a new message (uses no native code)'''
            if len(self.buf) >= 1 and self.buf[0] != 254:
                magic = self.buf[0]
                self.buf = self.buf[1:]
                if self.robust_parsing:
                    m = MAVLink_bad_data(chr(magic), "Bad prefix")
                    self.expected_length = 8
                    self.total_receive_errors += 1
                    return m
                if self.have_prefix_error:
                    return None
                self.have_prefix_error = True
                self.total_receive_errors += 1
                raise MAVError("invalid MAVLink prefix '%s'" % magic)
            self.have_prefix_error = False
            if len(self.buf) >= 2:
                if sys.version_info[0] < 3:
                    (magic, self.expected_length) = struct.unpack('BB', str(self.buf[0:2])) # bytearrays are not supported in py 2.7.3
                else:
                    (magic, self.expected_length) = struct.unpack('BB', self.buf[0:2])
                self.expected_length += 8
            if self.expected_length >= 8 and len(self.buf) >= self.expected_length:
                mbuf = array.array('B', self.buf[0:self.expected_length])
                self.buf = self.buf[self.expected_length:]
                self.expected_length = 8
                if self.robust_parsing:
                    try:
                        m = self.decode(mbuf)
                    except MAVError as reason:
                        m = MAVLink_bad_data(mbuf, reason.message)
                        self.total_receive_errors += 1
                else:
                    m = self.decode(mbuf)
                return m
            return None

        def parse_buffer(self, s):
            '''input some data bytes, possibly returning a list of new messages'''
            m = self.parse_char(s)
            if m is None:
                return None
            ret = [m]
            while True:
                m = self.parse_char("")
                if m is None:
                    return ret
                ret.append(m)
            return ret

        def decode(self, msgbuf):
                '''decode a buffer as a MAVLink message'''
                # decode the header
                try:
                    magic, mlen, seq, srcSystem, srcComponent, msgId = struct.unpack('cBBBBB', msgbuf[:6])
                except struct.error as emsg:
                    raise MAVError('Unable to unpack MAVLink header: %s' % emsg)
                if ord(magic) != 254:
                    raise MAVError("invalid MAVLink prefix '%s'" % magic)
                if mlen != len(msgbuf)-8:
                    raise MAVError('invalid MAVLink message length. Got %u expected %u, msgId=%u' % (len(msgbuf)-8, mlen, msgId))

                if not msgId in mavlink_map:
                    raise MAVError('unknown MAVLink message ID %u' % msgId)

                # decode the payload
                type = mavlink_map[msgId]
                fmt = type.format
                order_map = type.orders
                len_map = type.lengths
                crc_extra = type.crc_extra

                # decode the checksum
                try:
                    crc, = struct.unpack('<H', msgbuf[-2:])
                except struct.error as emsg:
                    raise MAVError('Unable to unpack MAVLink CRC: %s' % emsg)
                crcbuf = msgbuf[1:-2]
                if True: # using CRC extra
                    crcbuf.append(crc_extra)
                crc2 = x25crc(crcbuf)
                if crc != crc2.crc:
                    raise MAVError('invalid MAVLink CRC in msgID %u 0x%04x should be 0x%04x' % (msgId, crc, crc2.crc))

                try:
                    t = struct.unpack(fmt, msgbuf[6:-2])
                except struct.error as emsg:
                    raise MAVError('Unable to unpack MAVLink payload type=%s fmt=%s payloadLength=%u: %s' % (
                        type, fmt, len(msgbuf[6:-2]), emsg))

                tlist = list(t)
                # handle sorted fields
                if True:
                    t = tlist[:]
                    if sum(len_map) == len(len_map):
                        # message has no arrays in it
                        for i in range(0, len(tlist)):
                            tlist[i] = t[order_map[i]]
                    else:
                        # message has some arrays
                        tlist = []
                        for i in range(0, len(order_map)):
                            order = order_map[i]
                            L = len_map[order]
                            tip = sum(len_map[:order])
                            field = t[tip]
                            if L == 1 or isinstance(field, str):
                                tlist.append(field)
                            else:
                                tlist.append(t[tip:(tip + L)])

                # terminate any strings
                for i in range(0, len(tlist)):
                    if isinstance(tlist[i], str):
                        tlist[i] = str(MAVString(tlist[i]))
                t = tuple(tlist)
                # construct the message object
                try:
                    m = type(*t)
                except Exception as emsg:
                    raise MAVError('Unable to instantiate MAVLink message of type %s : %s' % (type, emsg))
                m._msgbuf = msgbuf
                m._payload = msgbuf[6:-2]
                m._crc = crc
                m._header = MAVLink_header(msgId, mlen, seq, srcSystem, srcComponent)
                return m
        def pfd_encode(self, roll, pitch, yaw, altitude, airspeed, battI):
                '''
                This message encodes data needed for the GroundStation Primary Flight
                Display. Should be sent at 20Hz.

                roll                      : Roll angle in 0.01 degrees. Positive means rolling CW (right down). (int16_t)
                pitch                     : Pitch angle in 0.01 degrees. Positive means pitching up. (int16_t)
                yaw                       : Yaw angle (magnetic heading) in 0.01 degrees. Positive means yawing CW (turn to the right). (int16_t)
                altitude                  : altitude (AGL) in meters. (int16_t)
                airspeed                  : airspeed in 0.1 m/s. (int16_t)
                battI                     : Battery current in 0.01 A. (int16_t)

                '''
                return MAVLink_pfd_message(roll, pitch, yaw, altitude, airspeed, battI)

        def pfd_send(self, roll, pitch, yaw, altitude, airspeed, battI):
                '''
                This message encodes data needed for the GroundStation Primary Flight
                Display. Should be sent at 20Hz.

                roll                      : Roll angle in 0.01 degrees. Positive means rolling CW (right down). (int16_t)
                pitch                     : Pitch angle in 0.01 degrees. Positive means pitching up. (int16_t)
                yaw                       : Yaw angle (magnetic heading) in 0.01 degrees. Positive means yawing CW (turn to the right). (int16_t)
                altitude                  : altitude (AGL) in meters. (int16_t)
                airspeed                  : airspeed in 0.1 m/s. (int16_t)
                battI                     : Battery current in 0.01 A. (int16_t)

                '''
                return self.send(self.pfd_encode(roll, pitch, yaw, altitude, airspeed, battI))

        def navd_encode(self, battV, temp, latitude, longitude, course, groundspeed):
                '''
                This message encodes data needed for the GroundStation Navigation
                Display. Should be sent at 5Hz.

                battV                     : Battery voltage in 0.01 Volt. (int16_t)
                temp                      : Cabin Temperature in 0.1 Celcius. (int16_t)
                latitude                  : Latitude (WGS84), in 10^-7 degrees. (int32_t)
                longitude                 : Longitude (WGS84), in 10^-7 degrees. (int32_t)
                course                    : Course heading in 0.01 degrees. (uint16_t)
                groundspeed               : groundspeed in 0.01 m/s. (uint16_t)

                '''
                return MAVLink_navd_message(battV, temp, latitude, longitude, course, groundspeed)

        def navd_send(self, battV, temp, latitude, longitude, course, groundspeed):
                '''
                This message encodes data needed for the GroundStation Navigation
                Display. Should be sent at 5Hz.

                battV                     : Battery voltage in 0.01 Volt. (int16_t)
                temp                      : Cabin Temperature in 0.1 Celcius. (int16_t)
                latitude                  : Latitude (WGS84), in 10^-7 degrees. (int32_t)
                longitude                 : Longitude (WGS84), in 10^-7 degrees. (int32_t)
                course                    : Course heading in 0.01 degrees. (uint16_t)
                groundspeed               : groundspeed in 0.01 m/s. (uint16_t)

                '''
                return self.send(self.navd_encode(battV, temp, latitude, longitude, course, groundspeed))

        def systemid_encode(self, timestamp, u_a, u_e, u_r, ax, ay, az, roll, pitch, yaw, p, q, r):
                '''
                This message encodes all the data needed for System Identification.

                timestamp                 : Ticks elapsed since the system has started. (uint32_t)
                u_a                       : Aileron control input in raw PWM value. Positive means right wing down. (int16_t)
                u_e                       : Elevator control input in raw PWM value. Positive means pitching up. (int16_t)
                u_r                       : Rudder control input in raw PWM value. Positive means turning to the right. (int16_t)
                ax                        : Acceleration on the body x-axis in 0.01g. Positive front. (int16_t)
                ay                        : Acceleration on the body y-axis in 0.01g. Positive right. (int16_t)
                az                        : Acceleration on the body z-axis in 0.01g. Positive down. (int16_t)
                roll                      : Roll angle in 0.01 degrees. Positive means rolling CW (right down). (int16_t)
                pitch                     : Pitch angle in 0.01 degrees. Positive means pitching up. (int16_t)
                yaw                       : Yaw angle (magnetic heading) in 0.01 degrees. Positive means yawing CW (turn to the right). (int16_t)
                p                         : Roll rate in 0.1 deg/s. Same sign-convention as roll angle. (int16_t)
                q                         : Pitch rate in 0.1 deg/s. Same sign-convention as pitch angle. (int16_t)
                r                         : Yaw rate in 0.1 deg/s. Same sign-convention as yaw angle. (int16_t)

                '''
                return MAVLink_systemid_message(timestamp, u_a, u_e, u_r, ax, ay, az, roll, pitch, yaw, p, q, r)

        def systemid_send(self, timestamp, u_a, u_e, u_r, ax, ay, az, roll, pitch, yaw, p, q, r):
                '''
                This message encodes all the data needed for System Identification.

                timestamp                 : Ticks elapsed since the system has started. (uint32_t)
                u_a                       : Aileron control input in raw PWM value. Positive means right wing down. (int16_t)
                u_e                       : Elevator control input in raw PWM value. Positive means pitching up. (int16_t)
                u_r                       : Rudder control input in raw PWM value. Positive means turning to the right. (int16_t)
                ax                        : Acceleration on the body x-axis in 0.01g. Positive front. (int16_t)
                ay                        : Acceleration on the body y-axis in 0.01g. Positive right. (int16_t)
                az                        : Acceleration on the body z-axis in 0.01g. Positive down. (int16_t)
                roll                      : Roll angle in 0.01 degrees. Positive means rolling CW (right down). (int16_t)
                pitch                     : Pitch angle in 0.01 degrees. Positive means pitching up. (int16_t)
                yaw                       : Yaw angle (magnetic heading) in 0.01 degrees. Positive means yawing CW (turn to the right). (int16_t)
                p                         : Roll rate in 0.1 deg/s. Same sign-convention as roll angle. (int16_t)
                q                         : Pitch rate in 0.1 deg/s. Same sign-convention as pitch angle. (int16_t)
                r                         : Yaw rate in 0.1 deg/s. Same sign-convention as yaw angle. (int16_t)

                '''
                return self.send(self.systemid_encode(timestamp, u_a, u_e, u_r, ax, ay, az, roll, pitch, yaw, p, q, r))

        def magcal_encode(self, mx, my, mz):
                '''
                This message encodes raw magnetometer data.

                mx                        : Magnetometer raw X reading (int16_t)
                my                        : Magnetometer raw Y reading (int16_t)
                mz                        : Magnetometer raw Z reading (int16_t)

                '''
                return MAVLink_magcal_message(mx, my, mz)

        def magcal_send(self, mx, my, mz):
                '''
                This message encodes raw magnetometer data.

                mx                        : Magnetometer raw X reading (int16_t)
                my                        : Magnetometer raw Y reading (int16_t)
                mz                        : Magnetometer raw Z reading (int16_t)

                '''
                return self.send(self.magcal_encode(mx, my, mz))

        def sysstate_encode(self, mode):
                '''
                This message encodes the current system status.

                mode                      : Current mode of the HACS system (uint8_t)

                '''
                return MAVLink_sysstate_message(mode)

        def sysstate_send(self, mode):
                '''
                This message encodes the current system status.

                mode                      : Current mode of the HACS system (uint8_t)

                '''
                return self.send(self.sysstate_encode(mode))

        def syscmd_encode(self, cmd, payload):
                '''
                This message encodes commands sent by the ground station.

                cmd                       : A set of well-knwon commands (uint8_t)
                payload                   : Optional command payload (uint32_t)

                '''
                return MAVLink_syscmd_message(cmd, payload)

        def syscmd_send(self, cmd, payload):
                '''
                This message encodes commands sent by the ground station.

                cmd                       : A set of well-knwon commands (uint8_t)
                payload                   : Optional command payload (uint32_t)

                '''
                return self.send(self.syscmd_encode(cmd, payload))

        def magcalresult_encode(self, B_field, hard_iron, soft_iron):
                '''
                This message encodes magnetometer calibration results.

                B_field                   : radius of the calibrated sphere (float)
                hard_iron                 : hard iron offsets (float)
                soft_iron                 : soft iron matrix (W_inverted) (float)

                '''
                return MAVLink_magcalresult_message(B_field, hard_iron, soft_iron)

        def magcalresult_send(self, B_field, hard_iron, soft_iron):
                '''
                This message encodes magnetometer calibration results.

                B_field                   : radius of the calibrated sphere (float)
                hard_iron                 : hard iron offsets (float)
                soft_iron                 : soft iron matrix (W_inverted) (float)

                '''
                return self.send(self.magcalresult_encode(B_field, hard_iron, soft_iron))

