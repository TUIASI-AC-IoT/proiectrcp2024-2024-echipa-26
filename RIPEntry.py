import socket
import struct

class Commands:
    REQUEST = 1
    RESPONSE = 2

class Versions:
    V1 = 1
    V2 = 2

class RIPEntry:
    def __init__(self, AF_id=socket.AF_INET, ip='', subnet='', nextHop='', metric=0, routeTag=0):
        self.AF_id = AF_id
        self.ip = ip
        self.subnet = subnet
        self.nextHop = nextHop
        self.metric = metric
        self.routeTag = routeTag

    def __str__(self):
        return self.ip+self.nextHop

def RIPtoBytes(RIPent):
    arr =[]
    arr.append(struct.pack('!2H', RIPent.AF_id, RIPent.routeTag))

    arr.append(socket.inet_aton(RIPent.ip))
    arr.append(socket.inet_aton(RIPent.subnet))
    arr.append(socket.inet_aton(RIPent.nextHop))

    arr.append(struct.pack('!I', RIPent.metric))
    return b''.join(arr)
    
def bytesToRIP(bytes : bytes):

    unpacked_data = struct.unpack('!2H4I', bytes)
    address_family_identifier = unpacked_data[0]
    route_tag = unpacked_data[1]
    ipv4 = socket.inet_ntoa(unpacked_data[2].to_bytes(4))
    subnet = socket.inet_ntoa(unpacked_data[3].to_bytes(4))
    next_hop = socket.inet_ntoa(unpacked_data[4].to_bytes(4)) 
    metric = unpacked_data[5]
    return RIPEntry(AF_id=address_family_identifier, ip= ipv4, subnet= subnet, nextHop= next_hop, metric = metric, routeTag= route_tag)



