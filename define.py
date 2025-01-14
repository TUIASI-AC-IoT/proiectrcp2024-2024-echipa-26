import signal
from multiprocessing.managers import BaseManager
import logging
from os import environ

multicastPort = 520
multicastIP = '224.0.0.9'
IP_PKTINFO = 8
multicast = (multicastIP, multicastPort)

class Commands:
    REQUEST = 1
    RESPONSE = 2

class Versions:
    V1 = 1
    V2 = 2

INF = int(environ['INF'])       

class Flags:
    CHANGED = 1
    UNCHANGED = 0
    

UPDATE_SIGNAL = signal.SIGUSR1
TRIGGER_UPDATE_SIGNAL = signal.SIGUSR2


logger = logging.getLogger('log')
logger.setLevel(logging.DEBUG)
file = logging.FileHandler('log')
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file.setFormatter(formatter)
logger.addHandler(file)

class MyManager(BaseManager):
    pass