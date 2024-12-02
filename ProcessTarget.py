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
    multicastPort = 520
    multicastIP = '224.0.0.9'
    socketList =[]

    #sockets pt raspunsuri trimise direct
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
            data,s = receiver.recvfrom(1024)
            key = receiver.getsockname()[0]
            msg = data.decode('ascii')
            toSend = (msg, s[0], key)
            pipe.send(toSend)

    while True:
        ready_to_read, _,_ = select.select(socketList,[],[], 0.1)
        for receiver in ready_to_read:
            data, s = receiver.recvfrom(1024)
            key = receiver.getsockname()[0]
            msg = bytesToMessage(data)
            toSend = (msg, s[0],key)
            pipe.send(toSend)












def multicastSender(pipe, ipList):
    seed(time())
    sleep(randint(1,10))


    socketDict = dict()
    multicast = (multicastIP, multicastPort)

    for ip in ipList:
        sender = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, proto=17)
        sender.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sender.bind((ip[0], multicastPort))
        sender.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 1)
        sender.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_LOOP, 0)
        sender.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_IF, socket.inet_aton(ip[0]))
        #TODO: build a request and send it
        req = bytes('Hello', 'ascii')
        sender.sendto(req, multicast)
        socketDict[ip[0]] = sender

    


    routingTable = ''
    def sigUSR1(signum, frame):
        global routingTable
        print(routingTable)
        pass
    
    signal.signal(signal.SIGUSR1, sigUSR1)
    
    t = time()
    while True:
        if pipe.poll(0.05):
            message, source, key = pipe.recv()
            if message == 'Hello':
                socketDict[key].sendto(bytes('REQ RESPONSE', 'ascii'), source)
            routingTable= routingTable+f'MSG:{message} from {source} to {key}'
            

            
            # if message.command == Commands.REQUEST:
            #     data = None # build a message from the routing table
            #     socketDict[key].sendto(data, source)
                
                
            
            # if message.command == Commands.RESPONSE:
            #     # update the routing table accordingly
            #     pass
        
        # routing table check routes timers

        # routing table check timer
        i = 0
        if time()-t>30:
            for socket in socketDict.items():
                msg = bytes(f'i', 'ascii')
                socket.sendto(msg, multicast)
            i+=1
            t=time()
