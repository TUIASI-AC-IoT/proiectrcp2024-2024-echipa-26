import multiprocessing.managers
from time import sleep, time
from random import seed, randint
import socket
import struct
import signal
import select
from typing import List,Tuple, Dict
import logging
import multiprocessing
from os import kill, environ, listdir, getppid, system
from traceback import format_exc


from RIPEntry import *
from Message import *
from Timer import *

multicastPort = 520
multicastIP = '224.0.0.9'
IP_PKTINFO = 8
multicast = (multicastIP, multicastPort)


INF = 16          

class Flags:
    CHANGED = 1
    UNCHANGED = 0
    

UPDATE_SIGNAL = signal.SIGUSR1
TRIGGER_UPDATE_SIGNAL = signal.SIGUSR2
    
class MyManager(multiprocessing.managers.BaseManager):
    pass

MyManager.register('Timer', Timer)
MyManager.register('RIPEntry', RIPEntry)


logger = logging.getLogger('log')
logger.setLevel(logging.DEBUG)
file = logging.FileHandler('log')
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file.setFormatter(formatter)
logger.addHandler(file)



class SharedTable:
    '''
    Class for storing a routing table which is accesible by multiple processes.
    '''
    def __init__(self, IPSubnetList:List[Tuple[str,str]], timeoutVals:Dict[str,int], garbageVals:Dict[str,int], metricVals:Dict[str,int])->None:
        '''
        Constructs the initial table.
        '''
        self.manager = multiprocessing.Manager()
        self.objectManager = MyManager()
        self.objectManager.start()
        
        
        self.entries = self.manager.dict()
        self.flags = self.manager.dict()
        self.timeout = self.manager.dict()
        self.garbage = self.manager.dict()
        
        self.timeoutVals = self.manager.dict()
        for IP in timeoutVals:
            self.timeoutVals[IP] = timeoutVals[IP]
        
        self.garbageVals = self.manager.dict()
        for IP in garbageVals:
            self.garbageVals[IP]=garbageVals[IP]
            
        self.metricVals = self.manager.dict()
        for IP in metricVals:
            self.metricVals[IP] = metricVals[IP]
        
        

        
        
        
        for IP, subnet in IPSubnetList:
            self.entries[IP] = self.objectManager.RIPEntry(ip=IP, subnet=subnet, nextHop = IP )
            self.timeout[IP] = self.objectManager.Timer(self.timeoutVals[IP])
            self.garbage[IP] = self.objectManager.Timer(self.garbageVals[IP])
            self.flags[IP] = Flags.UNCHANGED
            
    def answerRequest(self, req:Message)->Message:
        '''
        Method used to answer a request.
        '''
        if len(req.entries)==0:
            logger.debug('Request with 0 entries.')
            return Message(Commands.RESPONSE, Versions.V2, [])
        
        
        if len(req.entries)==1 and req.entries[0].AF_id==0 and req.entries[0].getMetric()==INF:
            logger.debug('Request for the entire table.')
            toBeSent = list(self.entries.values())
            m = Message(Commands.RESPONSE, Versions.V2, toBeSent)
            return m
        
        logger.debug('Debug request.')
        for entry in req.entries:
            pass
        
        return Message(Commands.RESPONSE, Versions.V2, [])
    
    def triggerUpdate(self):
        '''
        Sends a trigger update signal to the parent process.
        '''
        kill(getppid(), TRIGGER_UPDATE_SIGNAL)
    
    def answerResponse(self, sender:Tuple[str,int], response:Message, myIP:str)->None:
        '''
        Method used to manage a response.
        '''
        for entry in response.entries:
            if entry.getIP() in ['0.0.0.0', '127.0.0.1']:
                logger.error(f'Entry with local IP: {entry.getIP()}.')
                continue
            
            if entry.getMetric()<0 or entry.getMetric()>INF:
                logger.erro(f'Entry with wrong metric: {entry.getMetric()}.')
                continue
            
            entry.setMetric((int(min(entry.getMetric()+self.metricVals[myIP], INF))))
            entry.setNextHop(sender[0])
            key = entry.getIP()
            if entry.getIP() in list(self.entries.keys()):
                
                if self.entries[key].getNextHop() == entry.getNextHop():
                    self.timeout[key].reset()
                    if self.entries[key].getMetric()!= entry.getMetric():
                        self.entries[key].copy(entry)
                        self.flags[key] = Flags.CHANGED
                        self.triggerUpdate()
                        if self.entries[key].getMetric()==INF:
                            self.garbage[key].activate()
                            self.timeout[key].deactivate()
                else:
                    if self.entries[key].getMetric() > entry.getMetric():
                        self.entries[key].copy(entry)
                        self.flags[key] = Flags.CHANGED
                        self.timeout[key].reset()
                        self.garbage[key].deactivate()
                        self.triggerUpdate()
            else:
                logger.debug(f'New route to {key}.')
                self.entries[key] = self.objectManager.RIPEntry(other=entry)
                self.timeout[key]=self.objectManager.Timer(self.timeoutVals[myIP])
                self.garbage[key]=self.objectManager.Timer(self.garbageVals[myIP])
                self.flags[key] = Flags.CHANGED
                self.timeout[key].activate()
                self.triggerUpdate()
                
    def checkGarbage(self)->None:
        '''
        Method used for checking the garbage timers and deleting expired routes.
        '''
        for IP in list(self.garbage.keys()):
            if self.garbage[IP].tick():
                logger.debug(f'Deleted the route for {IP}.')
                del self.garbage[IP]
                del self.timeout[IP]
                del self.flags[IP]
                del self.entries[IP]
                
    def checkTimeout(self)->None:
        '''
        Method used for checking the timeout timers.
        '''
        for IP in list(self.garbage.keys()):
            if self.timeout[IP].tick():
                logger.debug(f'The route to {IP} timed out.')
                self.entries[IP].setMetric(INF)
                self.timeout[IP].deactivate()
                self.garbage[IP].activate()
                self.flags[IP] = Flags.CHANGED
                
    def cleanup(self)->None:
        '''
        Shuts down the managers used.
        '''
        self.objectManager.shutdown()
        self.manager.shutdown()
        
        
        
        
        
    def setTimeout(self, newVal:int, myIP:str, neighbourIP:str)->None:
        '''
        Changes the timeout for all the entries.
        '''
        
        if newVal <= 0:
            return
        
       
        self.timeoutVals[myIP] = newVal
        
        for IP in self.entries.keys():
            if self.entries[IP].getNextHop() == neighbourIP:
                self.timeout[IP].setTimeout(newVal)
                self.timeout[IP].setBaseTimeout(newVal)
        
        logger.debug(f'New timeout set {newVal} for interface {myIP}')
            
    def setGarbage(self, newVal:int, myIP:str, neighbourIP:str)->None:
        
        '''
        Changes the garbage timeout for all the entries.
        '''
        
        if newVal<=0 :
            return
        
        self.garbageVals[myIP] = newVal
        
        for IP in self.entries.keys():
            if self.entries[IP].getNextHop() == neighbourIP:
                self.garbage[IP].setTimeout(newVal)
                self.garbage[IP].setBaseTimeout(newVal)
        
        
            
        logger.debug(f'New garbage set {newVal} for interface {myIP}')

    def setMetric(self, newVal:int, myIP:str, neighborIP:str)->None:
        '''
        Changes the metric for packets coming from the myIP interface.
        '''
        
        if newVal<=0 :
            return
        
        diffMetric = self.metricVals[myIP] - newVal
        self.metricVals[myIP] = newVal
        
        for IP in self.entries.keys():
            if self.entries[IP].getNextHop() == neighborIP:
                self.entries[IP].setMetric(min(self.entris[IP].getMetric()+diffMetric, INF))
            
        logger.debug(f'New metric set {newVal} for interface {myIP}')



    def getAllEntries(self)->List[RIPEntry]:
        '''
        Returns a list of all the entries in the table.
        '''
        
        ret = []
        for IP in list(self.entries.keys()):
            e = RIPEntry(other=self.entries[IP])
            ret.append(e)
        return ret
    
    def getAllChangedEntries(self)->List[RIPEntry]:
        '''
        Returns all the entries that are changed. Beware returned entries are marked as unchanged when added to the result.
        '''
        ret = []
        for IP in list(self.entries.keys()):
            if self.flags[IP] == Flags.CHANGED:
                e = RIPEntry(other=self.entries[IP])
                ret.append(e)
                self.flags[IP] = Flags.UNCHANGED
        
        return ret


class Router:
    '''
    Class for simulating a router.
    '''
    def __init__(self, IPSubnetList:List[Tuple[str,str]], timeoutVals:Dict[str,int], garbageVals:Dict[str,int],metricVals:Dict[str,int], update=30)->None:
        '''
        Constructs the table and sockets.
        '''
        self.manager = multiprocessing.Manager()
        self.objectManager = MyManager()
        self.objectManager.start()
        
        
        
        self.table = SharedTable(IPSubnetList, timeoutVals, garbageVals, metricVals)  
        self.senderInterface = self.manager.dict()
        self.interfaceSender = self.manager.dict()
        
        
        self.listenSockets = dict()
        self.sendSockets = dict()
        
        
        self.update = self.objectManager.Timer(update)
        self.triggeredUpdate = self.objectManager.Timer()
        
        
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
            multicastReceiver.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_LOOP, 0)
            multicastReceiver.setsockopt(socket.IPPROTO_IP, IP_PKTINFO, 1)
        self.listenSockets[multicastIP] = multicastReceiver
         
    def start(self)->None:
        '''
        Starts the sender, receiver, timer checker and the main process initializes the CLI.
        '''
        logger.debug('Starting processes.')
        self.sendProcess.start()
        self.listenProcess.start()
        self.timeCheckerProcess.start()
        self.update.activate()
        self.cli()
        
    def setTimeout(self, timeout:int, myIP:str, neighbourIP:str)->None:
        '''
        Sets the timeout value for the table entries that came from neighbourIP.
        '''
        self.table.setTimeout(timeout, myIP, neighbourIP)
    
    def setGarbage(self, garbage:int, myIP:str, neighbourIP:str)->None:
        '''
        Sets the garbage value for the table entries that came from neighbourIP.
        '''
        self.table.setGarbage(garbage, myIP, neighbourIP)
    
    
    def setMetric(self, metric:int, myIP:str, neighbourIP:str)->None:
        '''
        Updates the metric value for the table entries that came from neighbourIP.
        '''
        self.table.setMetric(metric, myIP, neighbourIP)
    
    def setUpdate(self,update:int)->None:
        '''
        Changes the update timer.
        '''
        if update<=0:
            return
        
        self.update.setTimeout(update)
        self.update.setBaseTimeout(update)
    
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
            self.triggeredUpdate.deactivate()
            kill(self.sendProcess.pid, TRIGGER_UPDATE_SIGNAL)
        
    def cli(self)->None:
        '''
        CLI method. Runs in a separate process.
        '''
        def triggerUpdate(a,b):
            kill(self.sendProcess.pid, TRIGGER_UPDATE_SIGNAL)
        signal.signal(TRIGGER_UPDATE_SIGNAL, triggerUpdate)
        
        
        
        print("stop=stop all the processes")
        print("show=generate the table")
        print("help=display this menu")
        
        
        while True:
            command = input("Enter command:")
            if command == 'stop':
                logger.debug('Shutting down the processes.')
                kill(self.sendProcess.pid, signal.SIGTERM)
                kill(self.listenProcess.pid, signal.SIGTERM)
                kill(self.timeCheckerProcess.pid, signal.SIGTERM)
                self.shutdown()
                break
            elif command=="show":
                f= open('table.txt', 'w')
                entries = self.table.getAllEntries()
                for e in entries:
                    f.write(str(e))
                    f.write('\n\n')
                f.close()
            elif command=="help":
                print("stop=stop all the processes")
                print("show=generate the table")
                print("help=display this menu")
            else:
                system(command)
                
        self.join()
        
    
    
    
    def listen(self, pipe)->None:
        '''
        Listen the sockets and responds to all types of messages. Runs in a separate process.
        '''
        def sigterm(a,b):
            exit(0)
            
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
                
                self.interfaceSender[dest_ip] = addr[0]
                self.senderInterface[addr[0]] = dest_ip
                
                
                if msg.command == Commands.REQUEST:
                    logger.debug(f'New request from {addr[0]}.')
                    pipe.send((msg, addr))
                if msg.command == Commands.RESPONSE:
                    logger.debug(f'New response from {addr[0]}.')
                    self.table.answerResponse(addr, msg, self.senderInterface[addr[0]])
    
    def send(self, pipe)->None:
        '''
        Answer requests, triggered updates and updates. Runs in a separate process.
        '''
        
        def triggeredUpdate(a,b):
            if self.triggeredUpdate.isWorking() and self.triggeredUpdate.tick():
                
                changed = self.table.getAllChangedEntries()
                
                logger.debug('Triggered update.')
                
                for s in list(self.sendSockets.values()):
                    myIP = s.getsockname()[0]
                    splitHorizon = []
                    
                    if myIP not in list(self.interfaceSender.keys()):
                        continue
                    
                    for entry in changed:
                        if entry.getNextHop() != self.interfaceSender[myIP]:
                            splitHorizon.append(entry)
                    
                    while len(splitHorizon)>0:
                        m = Message(Commands.RESPONSE, Versions.V2, splitHorizon[:25])
                        m = messageToBytes(m)
                        s.sendto(m,multicast)
                        splitHorizon = splitHorizon[25:]
                    
                    
                    
                    
            else:
                self.triggeredUpdate.setTimeout(randint(1,5))
                self.triggeredUpdate.activate()
            
        def update(a,b):
            entries = self.table.getAllEntries()
            logger.debug('Update.')
            for s in list(self.sendSockets.values()):
                myIP = s.getsockname()
                splitHorizon = []
                if myIP not in list(self.interfaceSender.keys()):
                    continue
                
                for entry in entries:
                    if entry.getNextHop()!=self.interfaceSender[myIP]:
                        splitHorizon.append(entry)
                
                while len(splitHorizon)>0:
                    m = Message(Commands.RESPONSE, Versions.V2, splitHorizon[:25])
                    m = messageToBytes(m)
                    s.sendto(m, multicast)
                    splitHorizon = splitHorizon[:25]                        
        
        def sigterm(a,b):
            exit(0)          
        
        signal.signal(signal.SIGTERM, sigterm)
        signal.signal(TRIGGER_UPDATE_SIGNAL, triggeredUpdate)
        signal.signal(UPDATE_SIGNAL, update)
        
        seed(time)
        sleep(randint(1,10))
        
        for sock in list(self.sendSockets.values()):
            null = RIPEntry(metric=INF, AF_id=0)
            req = Message(Commands.REQUEST, Versions.V2, [null])
            req = messageToBytes(req)
            sock.sendto(req, multicast)
            logger.debug(f'Sending request over the {sock.getsockname()[0]} group.')
            
            
        while True:
            if pipe.poll(0.1):
                req, sender = pipe.recv()
                m = self.table.answerRequest(req)
                m = messageToBytes(m)
                self.sendSockets[self.senderInterface[sender[0]]].sendto(m,sender)
                
                
    def checkTimers(self)->None:
        '''
        Method that checks the timers constantly. Runs in a separate process.
        '''
        
        def sigterm(a,b):
            exit(0)
            
        signal.signal(signal.SIGTERM, sigterm)
        
        
        
        while True:
            self.manageTimers()
            sleep(0.1)
            

def main():
    try:
        IPSubnetList = []
        timeoutVals = dict()
        metric = dict()
        garbage = dict()
        
        ID = environ['ID']
        
        path = f'/home/tc/pr/cfg/r{ID}'
        for config in listdir(path):
            configPath = path+f'/{config}'
            file = open(configPath)
            lines = file.readlines()
            IPSubnetList.append((lines[2][3:-1],lines[3][7:-1]))
            
            timeoutVals[IPSubnetList[-1][0]] = int(lines[4].split('=')[1])
            metric[IPSubnetList[-1][0]] = int(lines[5].split('=')[1])
            garbage[IPSubnetList[-1][0]] = int(lines[6].split('=')[1])
            
        
        
        R = Router(IPSubnetList, timeoutVals, garbage, metric)
        R.start()
    except KeyboardInterrupt:
        try:
            pass
            #R.shutdown()
        except BaseException as e:
            logger.error(format_exc())
    except BaseException as e:
        logger.error(format_exc())
        try:
            pass
            #R.shutdown()
        except BaseException as e:
            logger.error(format_exc())
            exit(0)
        
        
if __name__ == "__main__":
    main()
        