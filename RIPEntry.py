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




# poate te ajuta (e imp pt attachHeader)
def entryToBytes(entry:RIPEntry)->bytes:
    #TODO
    pass

def bytesToEntry(bytes:bytes)->RIPEntry:
    #TODO
    pass


#intoarce o tupla de forma (list of rip entries, list comanda si versiune)
def messageToEntries(bytes:bytes):
    '''
    Takes a RIP message and converts it to a list of entries.
    '''
    #TODO
    pass


def entriesToMessage(command, version, entryList):
    pass

# de verificat daca e ok asa cu Commands si Versions
def attachHeader(command:Commands , version: Versions, entryList: list):
    #TODO
    pass




