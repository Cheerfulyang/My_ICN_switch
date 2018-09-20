import socket
import struct
import logging

logger = logging.getLogger('ICN_data') 

_PAD = b'\x00'


ICN_MAP = {
    "Version"  :     0x0064,
    "Head_length" :  0x000a,
    "ICN_Type" :     [0x00, 0x01],
    "Cache_Type" :   [0x00, 0x01],
    "LCD_Tag" :      [0x00, 0x01],
    "MCU_Tag" :      [0x00, 0x01],
    "Name_length":   0x0002
}

def check(data):
    _sum=0
    for i in range(0,len(data),4):
        val = int(data[i:i+4],16)
        _sum = _sum + val
        _sum = _sum & 0xffffffff

    _sum = (_sum >> 16) + (_sum & 0xffff)
    if _sum > 65535:
        _sum = (_sum >> 16) + (_sum & 0xffff)

    return 65535-_sum


class EtherHeader:
    def __init__(self, data):
        self.dmac = 0
        self.smac = 0
        self.ethertype = 0
        self.set_DMAC(data[0:6])
        self.set_SMAC(data[6:12])
        self.set_ethertype(data[12:])
    
    def set_DMAC(self, data):
        self.dmac = struct.unpack("!6s", data)[0]
    def set_SMAC(self, data):
        self.smac = struct.unpack("!6s", data)[0]
    def set_ethertype(self, data):
        self.ethertype = struct.unpack("!H", data)[0]
        
    def packed(self):
        packed = b""
        packed += struct.pack("!6s", self.smac)
        packed += struct.pack("!6s", self.dmac)
        packed += struct.pack("!H",  self.ethertype)
        return packed 
    
class IPHeader:
    def __init__(self, data):
        self.before_checksum = 0
        self.checksum = 0
        self.srcIP = 0
        self.dstIP = 0
        self.sipstr = 0
        self.dstipstr = 0
        self.set_before_checksum(data[0:10])
        self.set_srcIP(data[12:16])
        self.set_dstIP(data[16:])

    def printIP(self):
        print("srcIP: %s dstIP: %s" %(self.sipstr, self.dstipstr))
    def set_before_checksum(self, data):
        self.before_checksum = struct.unpack("!5H", data)[0]
    def set_srcIP(self, data):
        self.srcIP = struct.unpack("!2H", data)[0]
        self.sipstr = socket.inet_ntoa(struct.unpack("!4s", data)[0])
    def set_dstIP(self, data):
        self.dstIP = struct.unpack("!2H", data)[0]
        self.dipstr = socket.inet_ntoa(struct.unpack("!4s", data)[0])
        
    def set_checksum(self):
        hdstr = ''
        for i in self.before_checksum:
            hdstr += '%04x'%i
        hdstr += '%04x'%0
        for i in self.dstIP:
                hdstr += '%04x'%i
        for i in self.srcIP:
                hdstr += '%04x'%i
        print hdstr
        self.checksum = check(hdstr)   
        
    def packed(self):
        packed = b""
        self.set_checksum
        packed += struct.pack("!5H", self.before_checksum)
        packed += struct.pack("!H", self.checksum)
        packed += struct.pack("!2H",  self.dstIP)
        packed += struct.pack("!2H",  self.srcIP)
        return packed
        
class UDPHeader:
    def __init__(self, data, sip, dip):
        self.srcPort = 0
        self.dstPort = 0
        self.payload_length = 0
        self.checksum = 0
        self.set_srcPort(data[0:2])
        self.set_dstPort(data[2:4])
        self.set_payload_length(data[4:6])
        self.srcIP = sip
        self.dstIP = dip
        #self.set_checksum(self.sip, self.dip)
        
    def set_srcPort(self, data):
        self.srcIP = struct.unpack("!H", data)[0]
    def set_dstPort(self, data):
        self.set_dstIP = struct.unpack("!H", data)[0]
    def set_payload_length(self, data):
        self.payload_length = struct.unpack("!H", data)[0]
        
    def set_checksum(self, srcIP, dstIP):
        udp_hdstr = ''
        for i in dstIP:
            udp_hdstr += '%04x'%i
        for i in srcIP:
            udp_hdstr += '%04x'%i
        udp_hdstr += '0011'
        udp_hdstr += '%04x'%self.payload_length
        self.checksum = check(udp_hdstr)   
        
    def packed(self):
        packed = b""
        packed += struct.pack("!H", self.dstPort)
        packed += struct.pack("!H", self.srcPort)
        packed += struct.pack("!H",  self.payload_length)
        packed += struct.pack("!H",  self.checksum)
        return packed

class ICNHeader:
    def __init__(self, data):
        self.icn_version = 0
        self.total_len = 0
        self.icn_type = 0
        self.cache_type = 0
        self.LCD_Tag = 0
        self.MCU_Tag = 0
        self.Name_length = 0
        self.content_name = ''
        self.content = ''
        if data is not None :
            self.parse(data)
    def parse(self, data):
        raw = b""
        
        if not isinstance(data, bytes) :
            logger.debug("the type of the raw data is not bytes type %s" %(str(data)))
            for i in xrange(0, len(data)/2):
                value = int(data[i*2:i*2+2],16)    
                raw += struct.pack("!B", value) 
        else :
            raw = data
        
        raw_len = len(raw)
        if raw_len < 10 :
            logger.info('receive an packet data, which is too short to parse header: data len %u' % (raw_len) )
            return
        
        self.icn_version = struct.unpack('!H', raw[0:2])[0]
        if self.icn_version != ICN_MAP["Version"] :
            logger.info('ICN packet version %u is not correct, should be %u' % (self.icn_version, ICN_MAP["Version"]) )
            return
        
        self.total_len = struct.unpack('!H', raw[2:4])[0]
        logger.debug("total_len %d, raw_len %d" %(self.total_len, raw_len))
        #assert self.total_len == raw_len
        
        self.icn_type = struct.unpack('!B', raw[4:5])[0]
        self.cache_type = struct.unpack('!B', raw[5:6])[0]
        self.LCD_Tag = struct.unpack('!B', raw[6:7])[0]
        self.MCU_Tag = struct.unpack('!B', raw[7:8])[0]
        self.Name_length = struct.unpack('!H', raw[8:10])[0]
        logger.debug("len(data[10:]) : %d" %len(data[10:]))
        self.content_name =  struct.unpack("!%ds"%self.Name_length, data[10: 10+self.Name_length])[0]
        if data[10+self.Name_length:] is not None:
            self.content = data[10+self.Name_length:]
        
    def packed(self):
        pkt = b''
        pkt += struct.pack("!HHBBBBH", self.icn_version, self.total_len, self.icn_type, self.cache_type, \
                              self.LCD_Tag, self.MCU_Tag, self.Name_length)
        pkt += self.content_name
        return pkt

class Ethpacket:
    def __init__(self, data):
        self.ethHeader = EtherHeader(data[0:14])
        self.ipHeader = IPHeader(data[14:34])
        self.udpHeader = UDPHeader(data[34:42], self.ipHeader.srcIP, self.ipHeader.dstIP)
        self.icnHeader = ICNHeader(data[42:])
    
    def packed(self):
        pkt = b''
        pkt += self.ethHeader.packed()
        pkt += self.ipHeader.packed()
        pkt += self.udpHeader.packed()
        pkt += self.icnHeader.packed()
        return pkt
    

