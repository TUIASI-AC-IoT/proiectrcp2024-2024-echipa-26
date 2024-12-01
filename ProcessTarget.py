from time import sleep, time
from random import seed, randint
import socket
import struct
import select
from functools import partial
import signal

from RoutingTable import *



    

def multicastListen(pipe, ipList):
    seed(time())
    sleep(randint(1,10))

    for ip in ipList:
        sender = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, proto=17)
        sender.bind((ip, 520))
        sender.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 1)
        sender.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_LOOP, 0)
        sender.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_IF, socket.inet_aton(ip))
        #build message
        sender.sendall()
        sender.close()
    
    #send req
    #pipe.send(0)?
    #build messages with requests (the ip == self?)

    multicastPort = 520
    multicastIP = '224.0.0.9'
    receiver = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, proto =17)
    receiver.bind((multicastIP, multicastPort))
    for ip in ipList:
        r = struct.pack("=4s4s", socket.inet_aton(multicastIP), socket.inet_aton(ip))
        receiver.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, r)

    while True:
        data, s = receiver.recvfrom(1024)
        #data->clasa message
        #pipe.send(OBIECT message)
                


def multicastSender(pipe, ipList):
    socketList = []

    multicast_port = 520
    multicast_ip = '224.0.0.9'
    multicast = (multicast_ip, multicast_port)

    # astept ca listener-ul sa trimita request (nu pot face bind la adresele ip pe mai multe sockets)
    pipe.recv()

    for ip in ipList:
        sender = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, proto=17)
        sender.bind((ip, multicast_port))
        sender.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 1)
        sender.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_LOOP, 0)
        sender.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_IF, socket.inet_aton(ip))
        socketList.append(sender)

    routingTable = RoutingTable()

    def sigUSR1(signum, frame):
        global routingTable
        print(routingTable)
        pass
    
    signal.signal(signal.SIGUSR1, sigUSR1)
    

    while True:
        if pipe.poll(0.05):
            #message e obiect MESSAGE
            message = pipe.recv()

            if message.command == None:#valoare pt request in loc de None
                # send routing table directly
                pass
            
            if message.command == None: #valoare pt response
                # update the routing table accordingly
                pass
            
        #routing table check routes timers

        #routing table check timer
