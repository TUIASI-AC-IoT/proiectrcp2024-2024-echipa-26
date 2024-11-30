from time import sleep, time
from random import seed, randint
import socket
import struct
import select
from functools import partial

import signal
def getSockets(ipList, send=True):
    '''
    Return a list of sockets configured to send/listen on the multicast address for each address in ipList
    '''
    socketList = []
    multicast_port = 520
    multicast_ip = '224.0.0.9'
    multicast = (multicast_ip, multicast_port)

    if send:
        for ip in ipList:
            sender = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM, proto=17)
            sender.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 1)
            sender.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_IF, socket.inet_aton(ip))
            sender.setblocking(False)
            socketList.append(sender)

    else:
        for ip in ipList:
            receiver = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, proto=17)
            r = struct.pack("=4s4s", socket.inet_aton(multicast_ip), socket.inet_aton(ip))
            receiver.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, r)
            #receiver.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            receiver.setblocking(False)
            receiver.bind((ip,multicast_port))
            socketList.append(receiver)

    return socketList

def sigusr1_handler(table, signum, frame):
    print(table)

def multicast_listener(pipe, ipList):
    seed(time())
    sleep(randint(1,10))

    #TODO
    # send req

    socketList = getSockets(ipList, False)

    while True:
        ready_to_read, _,_=select.select(socketList, [],[], 0.1)
        if len(ready_to_read)!=0:
            for socket in ready_to_read:
                #receive data, convert to strings or whatever (not bytes) and send it through the pipe
                data, s = socket.recvfrom(1024)
                pipe.send((data,s))
                


def multicast_sender(pipe, ipList):
    socketList = getSockets(ipList, True)
    
    multicast_port = 520
    multicast_ip = '224.0.0.9'
    multicast = (multicast_ip, multicast_port)
    
    #change data to print
    data_to_print=''
    signal.signal(signal.SIGUSR1, partial(sigusr1_handler, data_to_print))


    t = time()
    while True:
        if pipe.poll(0.1):
            data = pipe.recv()
            data_to_print = data_to_print+f'{data[0].decode()} from {data[1]}\n'
        if time()-t>30:
            for socket in socketList:
                socket.sendto(bytes('???', 'utf-8'), multicast)
            t=time()
        

    while True:
        if pipe.poll(0.05):
            #TODO
            #check msg type
            #if req send directly the table
            #if update, update the routing table
            pass
        #check timers
