import struct
from RIPEntry import * 

class Message:
    '''
    RIPEntries + header
    '''
    def __init__(self, command, version, RIPentries:list):
        self.command = command
        self.version = version
        self.entries = RIPentries
            
    


def messageToBytes(msg :Message):
    '''
    Converts a Message object to bytes to be sent over the network
    '''

    # B - unsigned char -> 1 octet
    # H - unsigned short -> 2 octeti
    # I - unsigned int -> 4 octeti        
    # dimensiune totala format mesaj RIPv2 = 24 octeti 
    
    ripArr = []
    group = struct.pack("!2BH", msg.command, msg.version, 0)
    ripArr.append(group)
    for entry in msg.entries:
        r = RIPtoBytes(entry)
        ripArr.append(r)


    return b''.join(ripArr)





def bytesToMessage(bytes:bytes):
    '''
    Given bytes it returns a Message object
    '''
    header = bytes[0:4]
    ripEntry = []
    unpacked_data = struct.unpack("!2BH", header)
    n = (len(bytes) - 4)//20
    
    for i in range(0,n):
        ent = bytes[4+i*20:4+(i+1)*20]
        ent = bytesToRIP(ent)
        ripEntry.append(ent)

    
    return Message(unpacked_data[0], unpacked_data[1], ripEntry)



