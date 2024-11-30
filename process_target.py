from time import sleep, time
from random import seed, randint
import socket
import struct
import select
from functools import partial
import signal




def sigusr1_handler(table, signum, frame):
    print(table)

def multicast_listener(pipe, ipList):
    seed(time())
    sleep(randint(1,10))

    #TODO
    # send req

    multicastPort = 520
    multicastIP = '224.0.0.9'
    receiver = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, proto =17)
    receiver.bind((multicastIP, multicastPort))
    for ip in ipList:
        r = struct.pack("=4s4s", socket.inet_aton(multicastIP), socket.inet_aton(ip))
        receiver.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, r)

    while True:
        data, s = receiver.recvfrom(1024)
        sendTo = data.decode()+" from "+str(s[0])+" "+str(s[1])
        pipe.send(sendTo)
                


def multicast_sender(pipe, ipList):
    socketcketList = []

    multicast_port = 520
    multicast_ip = '224.0.0.9'
    multicast = (multicast_ip, multicast_port)


    for ip in ipList:
        sender = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, proto=17)
        sender.bind((ip, multicast_port))
        sender.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 1)
        sender.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_IF, socket.inet_aton(ip))


    #change data to print
    data_to_print=''
    signal.signal(signal.SIGUSR1, partial(sigusr1_handler, data_to_print))


    t = time()
    while True:
        if pipe.poll(0.1):
            data = pipe.recv()
            data_to_print = data_to_print+f'{data[0].decode()} from {data[1]}\n'
        if time()-t>30:
            for sock in socketcketList:
                sock.sendto(bytes('???', 'utf-8'), multicast)
                print('sent')
            t=time()
        

    while True:
        if pipe.poll(0.05):
            #TODO
            #check msg type
            #if req send directly the table
            #if update, update the routing table
            pass
        #check timers
