from time import sleep, time
from random import seed, randint
import socket
import struct
import signal
import select
from typing import List,Tuple, Dict


from RIPEntry import *
from Message import *
from Timer import *

multicastPort = 520
multicastIP = '224.0.0.9'

multicast = (multicastIP, multicastPort)
class Signals:
    SEND_ENTIRE_TABLE = 0
    TRIGERRED_UPDATE = 1
 
def multicastListen(pipe,IPSubnetList):
    
    socketList =[]

    # entries, timeout, garbage, flags = table
    
    sockDict=dict()
    for ip in IPSubnetList:
        simpleReceiver = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, proto=17)
        simpleReceiver.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        simpleReceiver.bind((ip[0], multicastPort))
        socketList.append(simpleReceiver)
        sockDict[simpleReceiver]=ip[0]
    
    

    for ip in IPSubnetList:
        multicastReceiver = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, proto=17)
        multicastReceiver.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        multicastReceiver.bind((multicastIP, multicastPort))
        r = struct.pack("=4s4s", socket.inet_aton(multicastIP), socket.inet_aton(ip[0]))
        multicastReceiver.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, r)
        socketList.append(multicastReceiver)
        sockDict[multicastReceiver] = ip[0]


    
    while True:
        ready_to_read, _,_ = select.select(socketList,[],[], 0.1)
        for receiver in ready_to_read:
            data, sender = receiver.recvfrom(1024)
            msg = bytesToMessage(data)
            pipe.send((msg, sender, (sockDict[receiver], multicastPort)))
            
            continue
            
            
            
            if entriesMsg[0].ip == '0.0.0.0':
                pipe.send([Signals.SEND_ENTIRE_TABLE, sender])
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




class Table:
    def __init__(self, IPSubnetList:List[Tuple[str]], timeout=180, garbage=120,update=30):
        self.entriesFrom = dict()
        self.timeout = dict()
        self.garbage = dict()
        self.flags = dict()
        
        self.entriesFrom['0.0.0.0'] = dict()
        self.timeout['0.0.0.0'] = dict()
        self.garbage['0.0.0.0'] = dict()
        self.flags['0.0.0.0'] = dict()
        
        #structura unui dictionar este de tipul:
        #map< ip de la cine am primit pachetul, map<ip destinatie, ripEntry> >
        
        
        self.timeoutValue = timeout
        self.garbageValue = garbage
        self.updateValue = update
        
        self.update = Timer(update)
        self.triggerTimer = None
        
        
        for ip, subnet in IPSubnetList:
            entry = RIPEntry(ip=ip,subnet=subnet, nextHop=ip)
            self.entriesFrom['0.0.0.0'][ip] = entry
            self.timeout['0.0.0.0'][ip] = Timer(timeout)
            self.garbage['0.0.0.0'][ip]=Timer(garbage)
            self.flags['0.0.0.0'][ip] = Flags.UNCHANGED
            
    def answerRequest(self, entriesMsg:List[RIPEntry], sender:tuple, sock:socket.socket):
        
        if len(entriesMsg) == 0:
            return
        if len(entriesMsg) == 1 and entriesMsg[0].AF_id == 0 and entriesMsg[0].metric == INF:
            print(f'am primit req pt tot de la {str(sender)} trimit pe {str(sock.getsockname())}')
            toBeSent = []
            for neighbour in self.entriesFrom:
                for dest in self.entriesFrom[neighbour]:
                    toBeSent.append(self.entriesFrom[neighbour][dest])
            m = Message(Commands.RESPONSE, Versions.V2, toBeSent)
            b = messageToBytes(m)
            sock.sendto(b,sender)
            return
        for entry in entriesMsg:
            #NOT IMPLEMENTED
            #NOT NEEDED (only for debug)
            return
              
    def doIHaveTheRouteTo(self, IP):
        for neighbour in self.entriesFrom:
            if IP in self.entriesFrom[neighbour]:
                return True
        return False
    
    def triggerUpdate(self):
        if self.triggerTimer is None:
            self.triggerTimer = Timer(randint(1,5))
            self.triggerTimer.activate()
            
    def answerResponse(self, entries:List[RIPEntry], sender:tuple):
        for entry in entries:
            if entry.ip in ['0.0.0.0', '127.0.0.1']:
                #log error
                pass
            if entry.metric<1 or entry.metric>INF:
                #log error
                pass
            
            #must be deleted after split horizon works
            if entry.nextHop in self.entriesFrom['0.0.0.0']:
                continue
            
            neighbour = sender[0]
            entry.metric = int(min(entry.metric+1, INF))
            entry.nextHop = neighbour
            old = self.doIHaveTheRouteTo(entry.ip)
            # TO BE REVISED
            if old:
                myEntry = self.entriesFrom[neighbour][entry.ip]
                
                if myEntry.nextHop == neighbour:
                    
                    self.timeout[neighbour][entry.ip].reset()
                    if myEntry.metric!=entry.metric:
                        self.entriesFrom[neighbour][entry.ip] = entry
                        self.flags[neighbour][entry.ip] = Flags.CHANGED
                        self.triggerUpdate()
                        if entry.metric == INF:
                            self.garbage[neighbour][entry.ip].activate()
                            self.timeout[neighbour][entry.ip].deactivate()
                else:
                    if myEntry.metric>entry.metric:
                        self.entriesFrom[neighbour][entry.ip]=entry
                        self.flags[neighbour][entry.ip]=Flags.CHANGED
                        self.timeout[neighbour][entry.ip].reset()
                        self.triggerUpdate()
                
                
                
            else:
                # New route
                if sender[0] not in self.entriesFrom:
                    self.entriesFrom[neighbour] = dict()
                    self.timeout[neighbour] = dict()
                    self.garbage[neighbour] = dict()
                    self.flags[neighbour] = dict()
                self.entriesFrom[neighbour][entry.ip] = entry
                self.timeout[neighbour][entry.ip] = Timer(self.timeoutValue)
                self.timeout[neighbour][entry.ip].activate()
                self.garbage[neighbour][entry.ip]=Timer(self.garbageValue)
                self.flags[neighbour][entry.ip]=Flags.CHANGED
                self.triggerUpdate()                
                
    def sendTriggerUpdate(self, sockets:List[socket.socket], interfaces:Dict[str,str]):
        '''
        Sends the triggered update
        '''
        changedRoutes = []
        for neighbour in self.entriesFrom:
            for dest in self.entriesFrom[neighbour]:
                if self.flags[neighbour][dest] == Flags.CHANGED:
                    changedRoutes.append(self.entriesFrom[neighbour][dest])
        
        for s in sockets:
            splitHorizon = []
            myIP = s.getsockname()[0]
            for entry in changedRoutes:
                #if interfaces[myIP] != entry.nextHop:
                splitHorizon.append(entry)
            if len(splitHorizon)==0:
                continue
            
            while len(splitHorizon)>0:
                m = Message(Commands.RESPONSE, Versions.V2, splitHorizon[:25])
                b = messageToBytes(m)
                s.sendto(b, multicast)
                splitHorizon = splitHorizon[25:]
        
        
        for neighbour in self.entriesFrom:
            for dest in self.entriesFrom[neighbour]:
                self.flags[neighbour][dest]=Flags.UNCHANGED
                
    def sendUpdate(self, sockets:List[socket.socket], interfaces:Dict[str,str]):
        '''
        Sends an update
        '''
        for s in sockets:
            splitHorizon = []
            myIP = s.getsockname()[0]
            for neighbour in self.entriesFrom:
                for dest in self.entriesFrom[neighbour]:
                    #if self.entriesFrom[neighbour][dest].nextHop != interfaces[myIP]:
                    splitHorizon.append(self.entriesFrom[neighbour][dest])
                    
                    
            if len(splitHorizon)==0:
                continue
            
            while len(splitHorizon)>0:
                m = Message(Commands.RESPONSE, Versions.V2, splitHorizon[:25])
                b = messageToBytes(m)
                s.sendto(b, multicast)
                splitHorizon = splitHorizon[25:]
            
    def checkTimeout(self):
        for neighbour in self.timeout:
            for dest in self.timeout[neighbour]:
                if self.timeout[neighbour][dest].tick():
                    self.entriesFrom[neighbour][dest].setMetric(INF)
                    self.timeout[neighbour][dest].deactivate()
                    self.garbage[neighbour][dest].activate()
                    self.flags[neighbour][dest] = Flags.CHANGED
                    self.triggerUpdate()
                    
    def checkGarbage(self):
        for neighbour in self.garbage:
            for dest in list(self.garbage[neighbour].keys()):
                if self.garbage[neighbour][dest].tick():
                    del self.garbage[neighbour][dest]
                    del self.entriesFrom[neighbour][dest]
                    del self.timeout[neighbour][dest]
                    del self.flags[neighbour][dest]
    
    def checkTimer(self,sockets:List[socket.socket], interfaces:Dict[str,str]):
        if self.update.tick():
            self.triggerTimer = None
            self.sendUpdate(sockets, interfaces)
            self.update.reset()
    
    def checkTriggerUpdate(self, sockets:List[socket.socket], interfaces:Dict[str,str]):
        if self.triggerTimer is not None and self.triggerTimer.tick():
            self.triggerTimer =None
            self.sendTriggerUpdate(sockets, interfaces)
    
    def getAllEntries(self)->List[RIPEntry]:
        ret = []
        for neighbour in self.entriesFrom:
            for dest in self.entriesFrom[neighbour]:
                ret.append(self.entriesFrom[neighbour][dest])
        return ret


def multicastSender(pipe, IPSubnetList):
    seed(time)
    sleep(randint(1,10))
    
    table = Table(IPSubnetList)
    interfaces = dict()
    
    def usr1(a,b):
        f = open('table.txt', 'w')
        f.write(str(interfaces))
        entries = table.getAllEntries()
        for i in entries:
            f.write(str(entries[i]))
            f.write("\n\n")
            
        
        f.close()
    signal.signal(signal.SIGUSR1, usr1)
    
    socketList = []
    multicast = (multicastIP, multicastPort)

    for ip in IPSubnetList:
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
    
    
    while True:
        if pipe.poll(0.1):
            message, sender, sock = pipe.recv()
            if sock[0]!=multicastIP:
                interfaces[sock[0]] = sender[0]
            senderIP, senderPort = sender
            if message.command == Commands.REQUEST:
                table.answerRequest(message.entries, sender, socketList[0])
            if message.command == Commands.RESPONSE:
                if senderPort != multicastPort:
                    continue
                table.answerResponse(message.entries, sender)
        
        table.checkTimeout()
        table.checkGarbage()
        table.checkTimer(socketList, interfaces)
        table.checkTriggerUpdate(socketList, interfaces)
        
    
def multicastSenderOld(pipe,IPSubnetList):
    
    
   #if sigint close all sockets
    
    
    #entries, timeout, garbage, flags = table
    
    seed(time())
    
    sleep(randint(1,10))
        

    entries = dict()
    timeout = dict()
    garbage = dict()
    flags = dict()
    #interfaces = dict()
    
    tabel = Table(IPSubnetList)
    
    def usr1(a,b):
        f = open('table.txt', 'w')
        for i in entries:
            f.write(str(entries[i]))
            f.write("\n\n")
        f.close()
    signal.signal(signal.SIGUSR1, usr1)
    
    for ip in IPSubnetList:
        e = RIPEntry(ip=ip[0], subnet=ip[1], nextHop=ip[0], metric=0)
        entries[ip[0]] = e
        flags[ip[0]] = Flags.UNCHANGED
        timeout[ip[0]] = Timer(120)
        garbage[ip[0]] = Timer(180)
        
    # entries       =   map<ip_dest     ,   RIPEntry>
    # timeout       =   map<ip_dest     ,   Timer>
    # garbage       =   map<ip_dest     ,   Timer>
    # flags         =   map<ip_dest     ,   flags>
    # interfaces va fi folosit pentru split horizon
    # interfaces    =   map<ip_vecin    ,   my_ip>
    
    

    socketList = []
    multicast = (multicastIP, multicastPort)

    for ip in IPSubnetList:
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
                    
                    for ip in IPSubnetList:
                        # de adaugat si comparatia cu subnet
                        if ip[0] == entry.ip:
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
                        timeout[entry.ip] = Timer(120)
                        timeout[entry.ip].activate()
                        garbage[entry.ip] = Timer(180)
                        flags[entry.ip] = Flags.CHANGED
                        if triggeredUpdate is None:
                            triggeredUpdate = Timer(randint(1,5))
                            triggeredUpdate.activate()
                        
                    else:
                        
                        print('entry vechi')
                        if senderIP == entries[entry.ip].nextHop:
                            timeout[entry.ip].reset()
                            
                            if entry.metric!=entries[entry.ip].getMetric():
                                pass
                            continue
                        
                        if entry.metric != entries[entry.ip].getMetric() and entry.metric<entries[entry.ip].metric:
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
                    
                    
                    
                    
                    
                    
def listen(pipe, ipList, table, manager):
    socketList =[]

    entries, flags, timeout, garbage = table
    
    
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

            command = msg.command
            entriesMsg = msg.entries
            
            if command == Commands.REQUEST:
                if len(entriesMsg) == 0:
                    continue
                if len(entriesMsg) == 1 and entriesMsg[0].AF_id == 0 and entriesMsg[0].metric == INF:
                    print(f'am primit req pt tot de la {str(sender)} trimit pe {str(socketList[0].getsockname())}')
                    m = Message(Commands.RESPONSE, Versions.V2, list(entries.values()))
                    b = messageToBytes(m)
                    #TODO:!! send all table to..
                    pipe.send()
                    #socketList[0].sendto(b,sender)
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
                            print('Ignored')
                            mine = True
                            break
                    if mine:
                        continue
                    
                    entry.metric = int(min(entry.metric+1, INF))
                    if entry.ip not in entries and entry.metric != INF:
                        
                        print(f'Entry nou cu metrica {entry.metric}')
                        e = manager.RIPEntry()
                        
                        entry.nextHop = senderIP
                        e.generateFrom(entry)
                        entries[entry.ip]= e
                        timeout[entry.ip] = manager.Timer(40)
                        timeout[entry.ip].activate()
                        garbage[entry.ip] = manager.Timer(30)
                        flags[entry.ip] = Flags.CHANGED
                        #TODO: send trgg update event
                        #pipe.send(..)
                        
                    else:
                        
                        print('Entry vechi')
                        if entry.metric != entries[entry.ip].getMetric():
                            print('Se schimba entry vechi')
                            entries[entry.ip].setMetric(entry.metric)
                            entries[entry.ip].setNextHop(senderIP)
                            flags[entry.ip] = Flags.CHANGED
                            if triggeredUpdate is None:
                                triggeredUpdate = Timer(randint(1,5))
                                triggeredUpdate.activate()
                                #TODO: send trgg update event
                                #pipe.send(..)
                            if entry.metric == INF:
                                garbage[entry.ip].activate()
                            else:
                                timeout[entry.ip].reset()
            