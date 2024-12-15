import multiprocessing
import multiprocessing.managers
import multiprocessing.process

from RIPEntry import *
from random import randint
from time import sleep
from Timer import *
from os import environ, listdir
import select
multicastPort = 520
multicastIP = '224.0.0.9'
def listen(ipList):
    socketList =[]
    for ip in ipList:
        sender = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, proto=17)
        sender.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sender.bind((ip[0], multicastPort))
        socketList.append(sender)
    
    rec = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, proto=17)
    rec.bind((multicastIP, multicastPort))

    for ip in ipList:
        r = struct.pack("=4s4s", socket.inet_aton(multicastIP), socket.inet_aton(ip[0]))
        rec.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, r)

    socketList.append(rec)


    
    while True:
        ready_to_read, _,_ = select.select(socketList,[],[], 0.1)
        for receiver in ready_to_read:
            data, s = receiver.recvfrom(1024)
            print(f'am primit {data.decode()} de la {str(s)} pe socket-ul {str(receiver.getsockname())}')
            
def send(ipList):
    sleep(randint(1,5))
    socketList = []
    multicast = (multicastIP, multicastPort)

    for ip in ipList:
        sender = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, proto=17)
        sender.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sender.bind((ip[0], multicastPort))
        sender.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 1)
        sender.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_LOOP, 0)
        sender.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_IF, socket.inet_aton(ip[0]))
        nullEntry = RIPEntry(0,'0.0.0.0','0.0.0.0','0.0.0.0',16,0)
        req = bytes('multicast', 'ascii')
        sender.sendto(req, multicast)
        print(f'am trimis multicast pe {sender.getsockname()}')
        socketList.append(sender)
    
    socketList[0].sendto(bytes('normal', 'ascii'), ('192.168.1.1', 520))
    print('Am trimis normal')
    
    
    for i in socketList:
        i.close()

def main():
    ipList = [] # lista de tuple
    ID = environ['ID']
    path = f'/home/tc/pr/cfg/r{ID}'
    for config in listdir(path):
        configPath = path+f'/{config}'
        file = open(configPath)
        lines = file.readlines()
        ipList.append((lines[2][3:-1],lines[3][7:-1]))
        
    p1 = multiprocessing.Process(target=listen, args=(ipList,))
    p2 = multiprocessing.Process(target=send, args=(ipList,))
    
    p1.start()
    p2.start()
    
    p1.join()
    p2.join()
    
    

if __name__ =="__main__":
    main()