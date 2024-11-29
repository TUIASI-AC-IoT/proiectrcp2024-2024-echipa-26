import struct

class Message:
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

    