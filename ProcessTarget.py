from time import sleep, time
from random import seed, randint
import socket
import struct
import signal
import select

from RIPEntry import *
from Message import *

multicastPort = 520
multicastIP = '224.0.0.9'
    
def multicastListen(pipe, ipList):
    
    socketList =[]

    #sockets pt raspunsuri trimise direct
    for ip in ipList:
        sender = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, proto=17)
        sender.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sender.bind((ip[0], multicastPort))
        socketList.append(sender)
    
    receiver = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, proto=17)
    receiver.bind((multicastIP, multicastPort))

    for ip in ipList:
        r = struct.pack("=4s4s", socket.inet_aton(multicastIP), socket.inet_aton(ip[0]))
        receiver.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, r)

    socketList.append(receiver)


    
    while True:
        ready_to_read, _,_ = select.select(socketList,[],[], 0.1)
        for receiver in ready_to_read:
            data, s = receiver.recvfrom(1024)
            msg = bytesToMessage(data)
            toSend = (msg, s[0])
            pipe.send(toSend)












def multicastSender(pipe, ipList):
    seed(time())
    
    sleep(randint(1,10))

    table = set()

    for ip in ipList:
        r = RIPEntry(ip = ip[0], subnet =ip[1], nextHop =ip[0], metric=0)
        table.add(r)


    socketDict = []
    multicast = (multicastIP, multicastPort)

    for ip in ipList:
        sender = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, proto=17)
        sender.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sender.bind((ip[0], multicastPort))
        sender.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 1)
        sender.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_LOOP, 0)
        sender.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_IF, socket.inet_aton(ip[0]))
        req = Message(Commands.REQUEST, Versions.V2, table)
        req = messageToBytes(req)
        sender.sendto(req, multicast)
        socketDict.append(sender)

    


    
    def sigUSR1(signum, frame):
        
        for i in table:
            print(i)
        pass
    
    signal.signal(signal.SIGUSR1, sigUSR1)
    
    t = time()
    while True:
        if pipe.poll(0.05):
            message, source = pipe.recv()
            
            

            
            if message.command == Commands.REQUEST:
                data = Message(Commands.RESPONSE, Versions.V2, table)
                data = messageToBytes(data)
                print('Am primit req de la:'+str(source))
                socketDict[0].sendto(data,(source, 520) )

                
                
            
            if message.command == Commands.RESPONSE:
                for i in message.entries:
                    table.add(i)
        
        # routing table check routes timers

        # routing table check timer
        
        if time()-t>30:
            for socketC in socketDict:
                msg = Message(Commands.RESPONSE, Versions.V2, table)
                msg = messageToBytes(msg)
                socketC.sendto(msg, multicast)
            t=time()
