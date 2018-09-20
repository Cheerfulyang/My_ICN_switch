import logging.config
logging.config.fileConfig('logging.conf')

from src import instantiate_ICNHandle,instantiate_UDPSender
from configure import Network_interface_PortName_List, Network_interface_IP_List
import argparse
import signal
import sys
import time
import traceback

logger = logging.getLogger('Boot')

def boot(Network_interface_PortName_List):
    instantiate_ICNHandle( Network_interface_PortName_List )
    instantiate_UDPSender( Network_interface_PortName_List )
    
def wait_exit(sleep_time):
    while True :
        time.sleep(sleep_time)
        
def CtrlCHandler(signum, frame):
    logger.info("5IGW receives a interrupt signal and begin to exit... ")
    calculate_packet_num()
    sys.exit()

if __name__ == "__main__" :
    signal.signal(signal.SIGINT, CtrlCHandler)
    try:
        boot(Network_interface_PortName_List)
        logger.info("LCD_ROUTE is running.")
    except Exception as e:
        print e
        print traceback.format_exc()
        sys.exit()
    wait_exit(2)    