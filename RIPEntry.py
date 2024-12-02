import socket

class Commands:
    REQUEST = None
    RESPONSE = None

class Versions:
    V1 = None
    V2 = None

class RIPEntry:
    def __init__(self, AF_id=socket.AF_INET, ip='', subnet='', nextHop='', metric=0):
        self.AF_id = AF_id
        self.ip = ip
        self.subnet = subnet
        self.nextHop = nextHop
        self.metric = metric

