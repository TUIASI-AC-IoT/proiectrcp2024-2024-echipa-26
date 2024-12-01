import struct
from RIPEntry import *


class Message:
    '''
    RIPEntry + header
    '''
    def __init__(self, command, version, must_be_zero, address_family_identifier, route_tag, ipv4, subnet, next_hop, metric):
        self.command = command
        self.version = version
        self.must_be_zero = must_be_zero
        self.address_family_identifier = address_family_identifier
        self.route_tag = route_tag
        self.ipv4 = ipv4
        self.subnet =  subnet
        self.next_hop = next_hop
        self.metric = metric

        

    #de adaugat parametrii
    def __init__(self, ripEntry):
        pass

    def __init__(self, bytes):
        self.command = struct.unpack('=2BH2H4I', bytes)[0]
        self.version = struct.unpack('=2BH2H4I', bytes)[1]
        self.must_be_zero = struct.unpack('=2BH2H4I', bytes)[2]
        self.address_family_identifier = struct.unpack('=2BH2H4I', bytes)[3]
        self.route_tag = struct.unpack('=2BH2H4I', bytes)[4]
        self.ipv4 = struct.unpack('=2BH2H4I', bytes)[5]
        self.subnet = struct.unpack('=2BH2H4I', bytes)[6]
        self.next_hop = struct.unpack('=2BH2H4I', bytes)[7]
        self.metric = struct.unpack('=2BH2H4I', bytes)[8]
        
        
    def to_bytes(self):
        '''
         B - unsigned char -> 1 octet
         H - unsigned short -> 2 octeti
         I - unsigned int -> 4 octeti
         
         dimensiune totala format mesaj RIPv2 = 24 octeti 
        '''
        return struct.pack('=2BH2H4I', 
                    self.command, # 1
                    self.version, # 1
                    self.must_be_zero, # 2
                    self.address_family_identifier, # 2
                    self.route_tag, # 2 
                    self.ipv4, # 4
                    self.subnet, # 4 
                    self.next_hop, # 4
                    self.metric) # 4        