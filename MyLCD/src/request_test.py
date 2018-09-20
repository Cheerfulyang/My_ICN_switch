import socket
from Queue import Queue  
import struct
import ICN_data as pkt
import os

eth_132 = [0x00,0x0c,0x29,0xbe,0x4a,0xe6]

eth_130 = [0x00,0x0c,0x29,0x89,0xaf,0x38]

ip_130 = [0xc0, 0xa8, 0x87, 0x82]
ip_132 = [192, 168, 135, 132]

HOST0='192.168.135.130'
HOST1='192.168.135.132'
PORT=9999
interface = "eth1"
RAW_PORT = 0X00

s = socket(socket.AF_PACKET, socket.SOCK_RAW)
s.bind((HOST0,RAW_PORT))
while True:
    data = b''
    for i in eth_132:
        data += struct.pack("!B", i)
    for i in eth_130:
        data += struct.pack("!B", i)
    data += struct.pack("!H", 0x0800)
    
    data += struct.pack("!12B", 0)
    
    for i in ip_130:
        data += struct.pack("!B", i)
    for i in ip_132:
        data += struct.pack("!B", i)
        
    data += struct.pack("!8B", 0)
        
        
    data+= struct.pack("!HHBBBB", 100, 0x0064, 0x00, 0X01, 0X01, 0X00 )
    name = "mytext.txt"
    name_len = len(name)
    data+= struct.pack("!H%us"%name_len, name_len, name)
    s.send(data)
    print("send over")
    
    
    ss = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    ss.bind((HOST0,PORT))

    res = ss.recvfrom(2048)
    print res
    break

s.close()
