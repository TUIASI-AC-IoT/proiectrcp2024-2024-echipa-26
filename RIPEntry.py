import socket
import struct



class RIPEntry:
    def __init__(self, AF_id=int(socket.AF_INET), ip='0.0.0.0', subnet='0.0.0.0', nextHop='0.0.0.0', metric=0, routeTag=0, other=None):
        if other is not None:
            self.AF_id = int(other.getAF_id())
            self.ip = other.getIP()
            self.subnet=other.getSubnet()
            self.nextHop=other.getNextHop()
            self.metric = other.getMetric()
            self.routeTag = other.getRT()
        else:
            if not isinstance(AF_id, int):
                raise(TypeError())
            
            if not isinstance(ip, str):
                raise(TypeError())
            
            if not isinstance(subnet, str):
                raise(TypeError())
            
            if not isinstance(nextHop, str):
                raise(TypeError())
            
            if not isinstance(metric, int):
                raise(TypeError())
            
            if not isinstance(routeTag, int):
                raise(TypeError())
            
            
            self.AF_id = int(AF_id)
            self.ip = ip
            self.subnet = subnet
            self.nextHop = nextHop
            self.metric = metric
            self.routeTag = routeTag
    
    
    
    def getAF_id(self)->int:
        return int(self.AF_id)
    def setAF_id(self, id):
        self.AF_id = int(id)
        
    def getIP(self):
        return self.ip
    def setIP(self, IP):
        self.ip=IP
        
    def getSubnet(self):
        return self.subnet
    def setSubnet(self, subnet):
        self.subnet = subnet
        
    def getNextHop(self):
        return self.nextHop
    def setNextHop(self, nextHop):
        self.nextHop = nextHop
        
    def getMetric(self):
        return self.metric
    def setMetric(self, metric):
        self.metric = metric
        
    def getRT(self):
        return self.routeTag
    def setRT(self, routeTag):
        self.routeTag = routeTag
    
    def __eq__(self, other):
        return (self.AF_id == other.AF_id and 
                self.ip == other.ip and 
                self.subnet == other.subnet and 
                self.nextHop == other.nextHop and 
                self.metric == other.metric and 
                self.routeTag == other.routeTag)
    
    def copy(self, other):
        self.AF_id = other.getAF_id()
        self.ip = other.getIP()
        self.subnet=other.getSubnet()
        self.nextHop=other.getNextHop()
        self.metric = other.getMetric()
        self.routeTag = other.getRT()
    
    def __hash__(self):
        return hash((self.AF_id, self.ip, self.subnet, self.nextHop, self.metric,self.routeTag))

    def __str__(self):
        return f'AF_id: {self.AF_id}\n'+f'IP: {self.ip}\n'+f'Subnet: {self.subnet}\n'+f'NextHop: {self.nextHop}\n'+f'Metric: {self.metric}\n'+f'Route Tag: {self.routeTag}'

def RIPtoBytes(RIPent:RIPEntry)->bytes:
    '''
    Converts a RIP entry to bytes.
    '''
    arr =[]
    arr.append(struct.pack('!2H', RIPent.getAF_id(), RIPent.getRT()))

    arr.append(socket.inet_aton(RIPent.getIP()))
    arr.append(socket.inet_aton(RIPent.getSubnet()))
    arr.append(socket.inet_aton(RIPent.getNextHop()))

    arr.append(struct.pack('!I', RIPent.getMetric()))
    return b''.join(arr)
    
def bytesToRIP(bytes : bytes)->RIPEntry:
    '''
    Converts bytes to a RIP entry.
    '''
    unpacked_data = struct.unpack('!2H4I', bytes)
    address_family_identifier = int(unpacked_data[0])
    route_tag = int(unpacked_data[1])
    ipv4 = socket.inet_ntoa(unpacked_data[2].to_bytes(4, 'big'))
    subnet = socket.inet_ntoa(unpacked_data[3].to_bytes(4, 'big'))
    next_hop = socket.inet_ntoa(unpacked_data[4].to_bytes(4,'big')) 
    metric = int(unpacked_data[5])
    return RIPEntry(AF_id=address_family_identifier, ip= ipv4, subnet= subnet, nextHop= next_hop, metric = metric, routeTag= route_tag)
