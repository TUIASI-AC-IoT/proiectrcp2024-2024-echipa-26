import multiprocessing
from typing import Dict,List, Tuple
import socket
from os import kill
import sys
import struct
import select
from random import randint, seed
from time import sleep, time
from traceback import format_exc


from define import *
from Timer import Timer
from RIPEntry import RIPEntry
from SharedTable import SharedTable
from Message import *
from CLI import CLI




class Router:
    '''
    Class for simulating a router.
    '''
    def __init__(self, IPSubnetList:List[Tuple[str,str]], timeoutVals:Dict[str,int], garbageVals:Dict[str,int],metricVals:Dict[str,int], update=30)->None:
        '''
        Constructs the table and sockets.
        '''
    
        MyManager.register('Timer', Timer, exposed=[
                            'getTimeout','setTimeout',
                            'setBaseTimeout', 'getBaseTimeout',
                            'getTimer',
                            'activate', 'deactivate',
                            'tick', 'isWorking', 'reset'
                            ]
                           )
        MyManager.register('RIPEntry', RIPEntry, exposed=[
                                    'getAF_id', 'setAF_id', 
                                    'getIP', 'setIP', 
                                    'getSubnet', 'setSubnet', 
                                    'getNextHop', 'setNextHop', 
                                    'getMetric', 'setMetric', 
                                    'getRT', 'setRT', 
                                    '__eq__', 'copy', '__hash__', '__str__']
                        )
        self.manager = multiprocessing.Manager()
        self.objectManager = MyManager()
        self.objectManager.start()
        
        
        
        self.table = SharedTable(IPSubnetList, timeoutVals, garbageVals, metricVals)  
        self.senderInterface = self.manager.dict()
        self.interfaceSender = self.manager.dict()
        
        
        self.listenSockets = dict()
        self.sendSockets = dict()
        
        
        self.update = self.objectManager.Timer(update)
        self.triggeredUpdate = self.objectManager.Timer(randint(1,5))
        
        
        s, l =multiprocessing.Pipe()
        
        self.listenProcess = multiprocessing.Process(target=self.listen, args=(l,))
        self.sendProcess = multiprocessing.Process(target=self.send, args=(s,))
        self.timeCheckerProcess = multiprocessing.Process(target=self.checkTimers)
        
        
        
        
        for IP, _ in IPSubnetList:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, proto=socket.IPPROTO_UDP)
            sock.bind((IP, multicastPort))
        
            mreq = struct.pack("4s4s", socket.inet_aton(multicastIP), socket.inet_aton(IP))
            sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
            sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_IF, socket.inet_aton(IP))
            sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 1)
            sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_LOOP, 0)
            sock.setsockopt(socket.IPPROTO_IP, IP_PKTINFO, 1)
            self.listenSockets[IP] = sock
            self.sendSockets[IP] = sock
            
        multicastReceiver = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, proto=socket.IPPROTO_UDP)
        multicastReceiver.bind((multicastIP, multicastPort))
        for IP, _ in IPSubnetList:
            mreq = struct.pack("4s4s", socket.inet_aton(multicastIP), socket.inet_aton(IP))
            multicastReceiver.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
            multicastReceiver.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_IF, socket.inet_aton(IP))
            multicastReceiver.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 1)
            multicastReceiver.setsockopt(socket.IPPROTO_IP, IP_PKTINFO, 1)
            multicastReceiver.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_LOOP, 0)
            
        self.listenSockets[multicastIP] = multicastReceiver
         
    def start(self)->None:
        '''
        Starts the sender, receiver, timer checker and the main process initializes the CLI.
        '''
        
        
        self.sendProcess.start()
        self.listenProcess.start()
        self.timeCheckerProcess.start()
        
        self.update.activate()
        self.cli()
        
    def setTimeout(self, timeout:float, myIP:str)->None:
        '''
        Sets the timeout value for the table entries that came from neighbourIP.
        '''
        if myIP in list(self.interfaceSender.keys()):
            self.table.setTimeout(timeout, myIP, self.interfaceSender[myIP])
        else:
            self.table.setTimeout(timeout, myIP, '0.0.0.0')
    
    def setGarbage(self, garbage:float, myIP:str)->None:
        '''
        Sets the garbage value for the table entries that came from neighbourIP.
        '''
        if myIP in list(self.interfaceSender.keys()):
            self.table.setGarbage(garbage, myIP, self.interfaceSender[myIP])
        else:
            self.table.setGarbage(garbage, myIP, '0.0.0.0')
    
    def setMetric(self, metric:int, myIP:str)->None:
        '''
        Updates the metric value for the table entries that came from neighbourIP.
        '''
        if myIP in list(self.interfaceSender.keys()):
            self.table.setMetric(metric, myIP, self.interfaceSender[myIP])
        else:
            self.table.setMetric(metric, myIP, '0.0.0.0')
    
    def setUpdate(self,update:float)->None:
        '''
        Changes the update timer.
        '''
        self.update.setTimeout(update)
        self.update.setBaseTimeout(update)
    
    def getTimeout(self, myIP:str):
        return self.table.getTimeout(myIP)
    def getGarbage(self, myIP:str):
        return self.table.getGarbage(myIP)
    def getMetric(self, myIP:str):
        return self.table.getMetric(myIP)
    
    
    def getUpdate(self):
        return self.update.getBaseTimeout()
    
    def join(self)->None:
        '''
        All the processes are joined.
        '''
        self.sendProcess.join()
        self.listenProcess.join()
        self.timeCheckerProcess.join()
        
        
    def closeManagers(self)->None:
        '''
        Shuts down all the managers used.
        '''
        self.table.cleanup()
        self.manager.shutdown()
        self.objectManager.shutdown()
    def closeSockets(self)->None:
        '''
        Closes the used sockets.
        '''
        for i in self.listenSockets:
            self.listenSockets[i].close()
    def shutdown(self)->None:
        '''
        Shuts down the managers and sockets.
        '''
        if self.sendProcess.is_alive():
            kill(self.sendProcess.pid, signal.SIGTERM)
        if self.listenProcess.is_alive():
            kill(self.listenProcess.pid, signal.SIGTERM)
        if self.timeCheckerProcess.is_alive():
            kill(self.timeCheckerProcess.pid, signal.SIGTERM)
        self.closeManagers()
        self.closeSockets()
    
    
                
    def manageTimers(self)->None:
        '''
        Method for checking timers and acting accordingly.
        '''
        self.table.checkGarbage()
        self.table.checkTimeout()
        
        if self.update.tick():
            self.triggeredUpdate.deactivate()
            self.update.reset(random=True, val=5)
            
            kill(self.sendProcess.pid, UPDATE_SIGNAL)
        elif self.triggeredUpdate.tick():
            
            kill(self.sendProcess.pid, TRIGGER_UPDATE_SIGNAL)
            
    
    
    def cli(self)->None:
        '''
        CLI method. Runs in a separate process.
        '''
        def triggerUpdate(a,b):
            if self.sendProcess.is_alive():
                kill(self.sendProcess.pid, TRIGGER_UPDATE_SIGNAL)
        signal.signal(TRIGGER_UPDATE_SIGNAL, triggerUpdate)
        
        CLI(self)
        
        
        
        self.shutdown()
        self.join()
        
    
    
    
    def listen(self, pipe)->None:
        '''
        Listen the sockets and responds to all types of messages. Runs in a separate process.
        '''
        try:
            def sigterm(a,b):
                pipe.close()
                sys.exit(0)
                
            signal.signal(signal.SIGTERM, sigterm)
            
            socketList = list(self.listenSockets.values())
            while True:
                ready_to_read, _,_ = select.select(socketList,[],[], 0.1)
                for receiver in ready_to_read:
                    msg, ancdata, _, addr = receiver.recvmsg(1024,1024)
                    dest_ip = None
                    for cmsg_level, cmsg_type, cmsg_data in ancdata:
                        if cmsg_level == socket.IPPROTO_IP and cmsg_type == IP_PKTINFO:
                            _, spec_dst, _ = struct.unpack('I4s4s', cmsg_data[:12])
                            dest_ip = socket.inet_ntoa(spec_dst)
                            break
                    msg = bytesToMessage(msg)
                    
                    if dest_ip == '10.0.2.15':
                        logger.error(f"msg for eth0 from {receiver.getsockname()}")
                        continue
                    
                    self.interfaceSender[dest_ip] = addr[0]
                    self.senderInterface[addr[0]] = dest_ip
                    
                    
                    if msg.command == Commands.REQUEST:
                        pipe.send((msg, addr))
                    if msg.command == Commands.RESPONSE:
                        self.table.answerResponse(addr, msg, self.senderInterface[addr[0]])
                        logger.debug(f'Ans response from {addr}, {len(msg.entries)} entries.')
        except BaseException as e:
            logger.error(format_exc())
            pipe.close()
            sys.exit(-1)
    
    def send(self, pipe)->None:
        '''
        Answer requests, triggered updates and updates. Runs in a separate process.
        '''
        try:
            def triggeredUpdate(a,b):
                if self.triggeredUpdate.isWorking() and self.triggeredUpdate.tick():
                    
                    changed = self.table.getAllChangedEntries()
                    
                    
                    for s in list(self.sendSockets.values()):
                        myIP = s.getsockname()[0]
                        splitHorizon = []
                        
                        if myIP not in list(self.interfaceSender.keys()):
                            continue
                        
                        for entry in changed:
                            if entry.getNextHop() != self.interfaceSender[myIP]:
                                splitHorizon.append(entry)
                        
                        while len(splitHorizon)>25:
                            m = Message(Commands.RESPONSE, Versions.V2, splitHorizon[:25])
                            b = messageToBytes(m)
                            s.sendto(b,multicast)
                            logger.debug(f'Trigger update using socket {myIP}. Sent {len(m.entries)}. Receiver should be: {self.interfaceSender[myIP]}')
                            splitHorizon = splitHorizon[25:]
                        m = Message(Commands.RESPONSE, Versions.V2, splitHorizon[:25])
                        b = messageToBytes(m)
                        s.sendto(b, multicast)
                        logger.debug(f'Trigger update using socket {myIP}. Sent {len(m.entries)}. Receiver should be: {self.interfaceSender[myIP]}')
                            
                    
                    self.triggeredUpdate.deactivate()      
                else:
                    
                    self.triggeredUpdate.setTimeout(randint(1,5))
                    self.triggeredUpdate.activate()
                
            def update(a,b):
                entries = self.table.getAllEntries()
                self.table.setFlagsUnchanged()
                for s in list(self.sendSockets.values()):
                    myIP = s.getsockname()[0]
                    splitHorizon = []
                    
                    
                    
                    if myIP not in list(self.interfaceSender.keys()):
                        logger.debug(f'Could not find {myIP} in {list(self.interfaceSender.keys())}')
                        continue
                    
                    for entry in entries:
                        if entry.getNextHop()!=self.interfaceSender[myIP]:
                            splitHorizon.append(entry)
                
                    while len(splitHorizon)>25:
                        m = Message(Commands.RESPONSE, Versions.V2, splitHorizon[:25])
                        m = messageToBytes(m)
                        s.sendto(m, multicast)
                        splitHorizon = splitHorizon[:25]
                        logger.debug(f'Update using socket {myIP}. Sent {len(m.entries)}. Receiver should be: {self.interfaceSender[myIP]}')
                    m = Message(Commands.RESPONSE, Versions.V2, splitHorizon[:25])
                    b = messageToBytes(m)
                    s.sendto(b, multicast)
                    logger.debug(f'Update using socket {myIP}. Sent {len(m.entries)}. Receiver should be: {self.interfaceSender[myIP]}')

                                        
            
            def sigterm(a,b):
                pipe.close()
                sys.exit(0)          
            
            signal.signal(signal.SIGTERM, sigterm)
            signal.signal(TRIGGER_UPDATE_SIGNAL, triggeredUpdate)
            signal.signal(UPDATE_SIGNAL, update)
            
            seed(time())
            sleep(randint(1,10))
            
            for sock in list(self.sendSockets.values()):
                null = RIPEntry(metric=INF, AF_id=0)
                req = Message(Commands.REQUEST, Versions.V2, [null])
                req = messageToBytes(req)
                sock.sendto(req, multicast)
                
                
            while True:
                if pipe.poll(0.1):
                    req, sender = pipe.recv()
                    m = self.table.answerRequest(req)
                    b = messageToBytes(m)
                    logger.debug(f'Sent {len(m.entries)} entries as a response to a request from {sender}.')
                    self.sendSockets[self.senderInterface[sender[0]]].sendto(b,sender)
                    
        except BaseException as e:
            logger.error(format_exc())
            pipe.close()
            sys.exit(-1)
                
                
    def checkTimers(self)->None:
        '''
        Method that checks the timers constantly. Runs in a separate process.
        '''
        try:
            def sigterm(a,b):
                sys.exit(0)
                
            signal.signal(signal.SIGTERM, sigterm)
            
            
            
            while True:
                self.manageTimers()
                sleep(0.1)
        except BaseException as e:
            logger.error(format_exc())
            sys.exit(-1)
            

# print("stop=stop all the processes")
        # print("show=generate the table")
        # print("help=display this menu")
        
        
        # while True:
        #     command = input("Enter command:")
        #     if command == 'stop':
        #         
        #         self.shutdown()
        #         break
        #     elif command=="show":
        #         f= open('table.txt', 'w')
        #         entries = self.table.getAllEntries()
        #         for e in entries:
        #             f.write(str(e))
        #             f.write('\n\n')
        #         f.close()
        #     elif command=="help":
        #         print("stop=stop all the processes")
        #         print("show=generate the table")
        #         print("help=display this menu")
        #     elif command=="interfaces":
        #         print(self.interfaceSender)
        #         print('\n\n')
        #         print(self.senderInterface)
        #     else:
        #         system(command)
            