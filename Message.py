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
        self.subnet = subnet
        self.next_hop = next_hop
        self.metric = metric
            
    
    # de adaugat parametrii
    # ma gandesc daca pot sa fac mai eficient......
    @classmethod
    def with_ripEntry(cls, command, version, must_be_zero, ripEntry : RIPEntry):
        return cls(command, version, must_be_zero, 
                   ripEntry.address_family_identifier, 
                   ripEntry.route_tag, 
                   ripEntry.ipv4, 
                   ripEntry.subnet, 
                   ripEntry.next_hop, 
                   ripEntry.metric)
        
    def unpack_bytes(self, bytes):
        unpacked_data = struct.unpack('!2BH2H4I', bytes)
        self.command = unpacked_data[0]
        self.version = unpacked_data[1]
        self.must_be_zero = unpacked_data[2]
        self.address_family_identifier = unpacked_data[3]
        self.route_tag = unpacked_data[4]
        self.ipv4 = unpacked_data[5]
        self.subnet = unpacked_data[6]
        self.next_hop = unpacked_data[7]
        self.metric = unpacked_data[8]
        
        
    def pack_bytes(self):
        
        # B - unsigned char -> 1 octet
        # H - unsigned short -> 2 octeti
        # I - unsigned int -> 4 octeti        
        # dimensiune totala format mesaj RIPv2 = 24 octeti 
         
        return struct.pack('!2BH2H4I', 
                    self.command, # 1
                    self.version, # 1
                    self.must_be_zero, # 2
                    self.address_family_identifier, # 2
                    self.route_tag, # 2 
                    self.ipv4, # 4
                    self.subnet, # 4 
                    self.next_hop, # 4
                    self.metric) # 4  
        
    
# message = Message.with_ripEntry(1, 2, 0, RIPEntry(0x02, 0x00, 0x00000000, 0x00000000, 0x00000000, 0x00000000))
# message2 = Message(1, 2, 0, 0x02, 0x00, 0x00000000, 0x00000000, 0x00000000, 0x00000000)

# print(message.pack_bytes()) # b'\x01\x02\x00\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
# print(message2.pack_bytes()) # b'\x01\x02\x00\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'

# pare ok -_- 