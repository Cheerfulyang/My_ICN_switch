import SocketServer as socketserver
import threading
from Queue import Queue  
import time



Server_Address = ("192.168.135.131", 9999)

class MyUDPHandler(socketserver.BaseRequestHandler):
    def handle(self):
        msg,socket = self.request
        print msg    
        print socket
        print self.client_address 
        
        UDP_string = str(self.request[0])
        server_socket  = self.request[1]
        Icn_Type = struct.unpack('!B', UDP_string[4:5])[0]
        request_string = UDP_string[8:]
        #Interest and Data Packets are forwarded directly to the ICN
        if Icn_Type == 48:   #"0x30"
            self.handle_requestICNData(UDP_string)
        if Icn_Type == 64:
            self.handle_reponseData(UDP_string)
        if Icn_Type == 0:
            pass

class MyUDPThread(socketserver.ThreadingMixIn, socketserver.UDPServer):
    allow_reuse_address = True

class ComeIn:
    def __init__(self, server_address):
        global q 
        q = Queue()
        self.server = MyUDPThread(server_address, MyUDPHandler)
        self.server_thread = threading.Thread(target=self.server.serve_forever)
        self.server_thread.setDaemon(True)
        self.server_thread.start()
        '''
        self.send_data = forwardPacket('SendPacket' , q)
        self.send_data.setDaemon(True)
        self.send_data.start()
        '''
        
def wait_exit(sleep_time):
    while True :
        time.sleep(sleep_time)

global UDPServer
UDPServer = ComeIn( Server_Address )

wait_exit(2) 

