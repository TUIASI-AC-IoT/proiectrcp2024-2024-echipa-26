import struct



class Message:
    '''
    RIPEntry + header
    '''
    def __init__(self, command=0, version=0, must_be_zero=0, address_family_identifier=0, route_tag=0, ipv4=0, subnet=0, next_hop=0, metric=0):
        self.command = command
        self.version = version
        self.must_be_zero = must_be_zero
        self.address_family_identifier = address_family_identifier
        self.route_tag = route_tag
        self.ipv4 = ipv4
        self.subnet = subnet
        self.next_hop = next_hop
        self.metric = metric
            
    def __str__(self):
        for eticheta , val in vars(self).items():
            print(f'{eticheta} : {val}')
            
    

def toBytes(msg :Message):
    '''
    Converts a Message object to bytes to be sent over the network
    '''

    # B - unsigned char -> 1 octet
    # H - unsigned short -> 2 octeti
    # I - unsigned int -> 4 octeti        
    # dimensiune totala format mesaj RIPv2 = 24 octeti 
    return struct.pack('!2BH2H4I', 
                    msg.command, # 1
                    msg.version, # 1
                    msg.must_be_zero, # 2
                    msg.address_family_identifier, # 2
                    msg.route_tag, # 2 
                    msg.ipv4, # 4
                    msg.subnet, # 4 
                    msg.next_hop, # 4
                    msg.metric) # 4  


def toMessage(bytes:bytes):
    '''
    Given bytes it returns a Message object
    '''

    unpacked_data = struct.unpack('!2BH2H4I', bytes)
    command = unpacked_data[0]
    version = unpacked_data[1]
    must_be_zero = unpacked_data[2]
    address_family_identifier = unpacked_data[3]
    route_tag = unpacked_data[4]
    ipv4 = unpacked_data[5]
    subnet = unpacked_data[6]
    next_hop = unpacked_data[7]
    metric = unpacked_data[8]

    return Message(command, version,must_be_zero, address_family_identifier, route_tag, ipv4,subnet,next_hop, metric)





# TEST !!!!
#message = Message.with_ripEntry(1, 2, 0, RIPEntry(0x02, 0x00, 0x00000000, 0x00000000, 0x00000000, 0x00000000))
#mesaj_packed = message.pack_bytes() # mesajul impachetat
#message.__str__() # afisez sa vad etichetele si valorile
#print(mesaj_packed) # vad cum arata mesajul impachetat

#message2 = Message(0, 0, 0, 0, 0, 0, 0, 0, 0)
#message2.unpack_bytes(mesaj_packed)
#message2.__str__()


