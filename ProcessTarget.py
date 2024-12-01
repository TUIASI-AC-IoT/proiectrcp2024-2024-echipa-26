from time import sleep, time
from random import seed, randint
import socket
import struct
import signal

from Message import *

from RoutingTable import *



    

def multicastListen(pipe, ipList):
    seed(time())
    sleep(randint(1,10))
    multicastPort = 520
    multicastIP = '224.0.0.9'
    
    #de mutat trimis-ul de request catre sender?
    for ip in ipList:
        sender = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, proto=17)
        sender.bind((ip, multicastPort))
        sender.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 1)
        sender.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_LOOP, 0)
        sender.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_IF, socket.inet_aton(ip))
        #build message
        sender.sendall()
        sender.close()
        #send req

    pipe.send(0)

    
    receiver = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, proto =17)
    receiver.bind((multicastIP, multicastPort))
    for ip in ipList:
        r = struct.pack("=4s4s", socket.inet_aton(multicastIP), socket.inet_aton(ip))
        receiver.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, r)

    while True:
        data, s = receiver.recvfrom(1024)
        msg = toMessage(data)
        toSend = (msg, s[0])
        #s - tuplu s[0]-adresa ip si s[1]-portul
        pipe.send(toSend)
                


def multicastSender(pipe, ipList):
    socketList = []

    multicastPort = 520
    multicastIP = '224.0.0.9'
    multicast = (multicastIP, multicastPort)

    # astept ca listener-ul sa trimita request-urile (nu pot face bind la adresele ip pe mai multe sockets)
    pipe.recv()

    for ip in ipList:
        sender = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, proto=17)
        sender.bind((ip, multicastPort))
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
            # message e obiect MESSAGE
            # source e adresa ip de la care provine mesajul
            message, source = pipe.recv()

            if message.command == None:#valoare pt request in loc de None
                # send routing table directly
                pass
            
            if message.command == None: #valoare pt response
                # update the routing table accordingly
                pass
            
        #routing table check routes timers

        #routing table check timer
