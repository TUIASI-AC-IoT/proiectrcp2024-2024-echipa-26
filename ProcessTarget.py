from time import sleep, time
from random import seed, randint
import socket
import struct
import signal
import select

from RIPEntry import *
from Message import *
from Timer import *

multicastPort = 520
multicastIP = '224.0.0.9'


class Signals:
    SEND_ENTIRE_TABLE = 0
    TRIGERRED_UPDATE = 1
 
def multicastListen(pipe,ipList):
    
    socketList =[]

    # entries, timeout, garbage, flags = table
    
    
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
            msg = bytesToMessage(data)
            pipe.send((msg, s, receiver.getsockname()))
            
            continue
            
            
            
            if entriesMsg[0].ip == '0.0.0.0':
                pipe.send([Signals.SEND_ENTIRE_TABLE, s])
            else:
                table, interfaces = getValues(queue)
                entries, timeout, garbage, flags = table
                for ent in entriesMsg:
                    entries[ent.ip] = RIPEntry().generateFrom(ent)
                table=(entries, timeout, garbage, flags)
                putValues(queue, (table, interfaces))
            print('AM PROCESAT CE AM PRIMIT')
            myIP = receiver.getsockname()[0]
            if myIP != multicastIP:
                interfaces[senderIP] = myIP
            
            
                        
                    
            
            
                            
                    
                        
                        
                    
                
            
            
                
            



INF = 16
class Flags:
    CHANGED = 1
    UNCHANGED = 0





def multicastSender(pipe,ipList):
    
    
   #if sigint close all sockets
    
    
    #entries, timeout, garbage, flags = table
    
    seed(time())
    
    sleep(randint(1,10))
        

    entries = dict()
    timeout = dict()
    garbage = dict()
    flags = dict()
    #interfaces = dict()
    
    def usr1(a,b):
        f = open('table.txt', 'w')
        for i in entries:
            f.write(str(entries[i]))
            f.write("\n\n")
        f.close()
    signal.signal(signal.SIGUSR1, usr1)
    
    for ip in ipList:
        e = RIPEntry(ip=ip[0], subnet=ip[1], nextHop=ip[0], metric=0)
        entries[ip[0]] = e
        flags[ip[0]] = Flags.UNCHANGED
        timeout[ip[0]] = Timer(40)
        garbage[ip[0]] = Timer(30)
        
    # entries       =   map<ip_dest     ,   RIPEntry>
    # timeout       =   map<ip_dest     ,   Timer>
    # garbage       =   map<ip_dest     ,   Timer>
    # flags         =   map<ip_dest     ,   flags>
    # interfaces va fi folosit pentru split horizon
    # interfaces    =   map<ip_vecin    ,   my_ip>
    
    

    socketList = []
    multicast = (multicastIP, multicastPort)

    for ip in ipList:
        sender = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, proto=17)
        sender.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sender.bind((ip[0], multicastPort))
        sender.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 1)
        sender.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_LOOP, 0)
        sender.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_IF, socket.inet_aton(ip[0]))
        nullEntry = RIPEntry(0,'0.0.0.0','0.0.0.0','0.0.0.0',INF,0)
        req = Message(Commands.REQUEST, Versions.V2, [nullEntry])
        req = messageToBytes(req)
        sender.sendto(req, multicast)
        socketList.append(sender)

    



    
    timer =Timer(30)
    timer.activate()
    triggeredUpdate = None
    while True:
        if pipe.poll(0.1):
            message, sender, sock = pipe.recv()
            print(f'msg primit de la {str(sender)} pe sock {str(sock)}')
            # if sock[0] != multicastIP:
            #     interfaces[sock[0]] = sender[0]
            #     print(interfaces)
            
            
            command = message.command
            entriesMsg = message.entries
            
            if command == Commands.REQUEST:
                if len(entriesMsg) == 0:
                    continue
                if len(entriesMsg) == 1 and entriesMsg[0].AF_id == 0 and entriesMsg[0].metric == INF:
                    print(f'am primit req pt tot de la {str(sender)} trimit pe {str(socketList[0].getsockname())}')
                    m = Message(Commands.RESPONSE, Versions.V2, list(entries.values()))
                    b = messageToBytes(m)
                    socketList[0].sendto(b,sender)
                    continue
                for entry in entriesMsg:
                    # ???
                    break
            
            senderPort= sender[1]
            senderIP=sender[0]
            if command == Commands.RESPONSE:
                print(f'am primit {len(entriesMsg)} entries de la {senderIP}')
                if senderPort != multicastPort:
                    continue
                for entry in entriesMsg:
                    if entry.metric > INF:
                        # log
                        continue
                    
                    if entry.ip == '0.0.0.0' or entry.ip == '127.0.0.1':
                        # log
                        continue
                    
                    mine = False
                    
                    for ip in ipList:
                        # de adaugat si comparatia cu subnet
                        if ip[0] == entry.nextHop:
                            print('wtf')
                            mine = True
                            break
                    if mine:
                        continue
                    
                    entry.metric = int(min(entry.metric+1, INF))
                    if entry.ip not in entries and entry.metric != INF:
                        
                        print(f'entry nou cu metrica{entry.metric}')
                        entry.nextHop = senderIP
                        entries[entry.ip]= entry
                        timeout[entry.ip] = Timer(40)
                        timeout[entry.ip].activate()
                        garbage[entry.ip] = Timer(30)
                        flags[entry.ip] = Flags.CHANGED
                        if triggeredUpdate is None:
                            triggeredUpdate = Timer(randint(1,5))
                            triggeredUpdate.activate()
                        
                    else:
                        
                        print('entry vechi')
                        if entry.metric != entries[entry.ip].getMetric():
                            print('se schimba entry vechi')
                            entries[entry.ip].setMetric(entry.metric)
                            entries[entry.ip].setNextHop(senderIP)
                            flags[entry.ip] = Flags.CHANGED
                            if triggeredUpdate is None:
                                triggeredUpdate = Timer(randint(1,5))
                                triggeredUpdate.activate()
                            if entry.metric == INF:
                                garbage[entry.ip].activate()
                            else:
                                timeout[entry.ip].reset()
            
            
        for key in entries:
            if timeout[key].tick():
                entries[key].setMetric(INF)
                flags[key]=Flags.CHANGED
                timeout[key].deactivate()
                garbage[key].activate()
                if triggeredUpdate is None:
                    triggeredUpdate = Timer(randint(1,5))
                    triggeredUpdate.activate()
                
        for key in list(garbage.keys()):
            if garbage[key].tick():
                del timeout[key]
                del entries[key]
                del flags[key]
                del garbage[key]
                
        if timer.tick():
            triggeredUpdate = None
            #generate message and send it multicast
            for s in socketList:
                # myIP = s.getsockname()[0]
                # if myIP not in interfaces:
                #     continue
                # receiverIP = interfaces[myIP]
                splitHorizon = []
                for key in entries.keys():
                    # if entries[key].nextHop != receiverIP:   
                    splitHorizon.append(entries[key])
                m = Message(command=Commands.RESPONSE, version=Versions.V2,RIPentries=splitHorizon)
                b = messageToBytes(m)
                s.sendto(b, multicast)
                print(f'am trimis catre  {len(splitHorizon)} update')

            timer.reset()
            
        if triggeredUpdate is not None:
            if triggeredUpdate.tick():
                triggeredUpdate = None
                toBeSent = []
                for dest in entries.keys():
                    if flags[dest] == Flags.CHANGED:
                        toBeSent.append(entries[dest])
                        flags[dest]=Flags.UNCHANGED
                
                for s in socketList:
                    # myIP = s.getsockname()[0]
                    # if myIP not in interfaces:
                    #     continue
                    # receiverIP = interfaces[myIP]
                    splitHorizon = []
                    for key in entries.keys():
                        # if entries[key].nextHop != receiverIP:   
                        splitHorizon.append(entries[key])
                    m = Message(Commands.RESPONSE, Versions.V2, splitHorizon)
                    b = messageToBytes(m)
                    print(f'am trimis catre  {len(splitHorizon)} trg update')
                    s.sendto(b, multicast) 