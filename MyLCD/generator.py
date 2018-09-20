from socket import *

HOST0='192.168.135.130'
HOST1='192.168.135.131'
PORT=9999

s = socket(AF_INET,SOCK_DGRAM)
s.bind((HOST0,PORT))
while True:
    message = raw_input('send message:>>')
    s.sendto(message, (HOST1,PORT))
    data = s.recv(1024)
    print data
s.close()
