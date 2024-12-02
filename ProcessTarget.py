from time import sleep, time
from random import seed, randint
import socket
import struct
import signal
import select


from RoutingTable import *
from RIPEntry import *


multicastPort = 520
multicastIP = '224.0.0.9'
    
def multicastListen(pipe, ipList):
    seed(time())
    sleep(randint(1,10))
    multicastPort = 520
    multicastIP = '224.0.0.9'

    socketList =[]

    for ip in ipList:
        sender = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, proto=17)
        sender.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sender.bind((ip[0], multicastPort))
        socketList.append(sender)
    receiver = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, proto =17)
    receiver.bind((multicastIP, multicastPort))
    for ip in ipList:
        r = struct.pack("=4s4s", socket.inet_aton(multicastIP), socket.inet_aton(ip[0]))
        receiver.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, r)
    socketList.append(receiver)

    while True:
        ready_to_read, _,_ = select.select(socketList,[],[], 0.1)
        for receiver in ready_to_read:
            data, s = receiver.recvfrom(1024)
            msg = messageToEntries(data)
            toSend = (msg, s[0])
            pipe.send(toSend)
                
def multicastSender(pipe, ipList):
    socketDict = dict()
    multicast = (multicastIP, multicastPort)

    for ip in ipList:
        sender = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, proto=17)
        sender.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sender.bind((ip[0], multicastPort))
        sender.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 1)
        sender.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_LOOP, 0)

        

        sender.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_IF, socket.inet_aton(ip[0]))
        socketDict[ip] = sender

    routingTable = RoutingTable()

    def sigUSR1(signum, frame):
        global routingTable
        print(routingTable)
        pass
    
    signal.signal(signal.SIGUSR1, sigUSR1)
    

    while True:
        if pipe.poll(0.05):
            message, source = pipe.recv()

            msgType = message[1][0]
            msgVersion = message[1][1]
            msgEntries = message[0]

            
            if msgType == Commands.REQUEST:
                selectedSocket = None
                for ip in socketDict:
                    if ip[0] == source:
                        selectedSocket = socketDict[ip]
                        break

                data = routingTable.toMessage(Commands.REQUEST, Versions.V2)
                selectedSocket.sendto(data, (source, multicastPort))
                
                
            
            if msgType == Commands.RESPONSE:
                # update the routing table accordingly
                pass
            
        # routing table check routes timers

        # routing table check timer
