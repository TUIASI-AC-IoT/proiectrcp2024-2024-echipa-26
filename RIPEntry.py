import socket
import struct

class Commands:
    REQUEST = 1
    RESPONSE = 2

class Versions:
    V1 = 1
    V2 = 2

class RIPEntry:
    def __init__(self, AF_id=socket.AF_INET, ip='0.0.0.0', subnet='0.0.0.0', nextHop='0.0.0.0', metric=0, routeTag=0):
        self.AF_id = AF_id
        self.ip = ip
        self.subnet = subnet
        self.nextHop = nextHop
        self.metric = metric
        self.routeTag = routeTag

    def __eq__(self, other):
        return (self.AF_id == other.AF_id and 
                self.ip == other.ip and 
                self.subnet == other.subnet and 
                self.nextHop == other.nextHop and 
                self.metric == other.metric and 
                self.routeTag == other.routeTag)
    
    def __hash__(self):
        return hash((self.AF_id, self.ip, self.subnet, self.nextHop, self.metric,self.routeTag))

    def __str__(self):
        return f'To: {self.ip} {self.subnet}: {self.nextHop}, cost: {self.metric}'

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
    ipv4 = socket.inet_ntoa(unpacked_data[2].to_bytes(4, 'big'))
    subnet = socket.inet_ntoa(unpacked_data[3].to_bytes(4, 'big'))
    next_hop = socket.inet_ntoa(unpacked_data[4].to_bytes(4,'big')) 
    metric = unpacked_data[5]
    return RIPEntry(AF_id=address_family_identifier, ip= ipv4, subnet= subnet, nextHop= next_hop, metric = metric, routeTag= route_tag)



