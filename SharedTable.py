from typing import List,Tuple, Dict
from os import kill, getppid
import multiprocessing
from traceback import format_exc


from Message import Message
from RIPEntry import RIPEntry
from Timer import Timer

from define import *


class SharedTable:
    '''
    Class for storing a routing table which is accesible by multiple processes.
    '''
    def __init__(self, IPSubnetList:List[Tuple[str,str]], timeoutVals:Dict[str,int], garbageVals:Dict[str,int], metricVals:Dict[str,int])->None:
        '''
        Constructs the initial table.
        '''
        
        MyManager.register('Timer', Timer)
        MyManager.register('RIPEntry', RIPEntry)
        
        self.manager = multiprocessing.Manager()
        self.objectManager = MyManager()
        self.objectManager.start()
        
        
        self.tableLock = self.manager.Lock()
        
        
        self.IPLock = self.manager.dict()
        
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
            self.IPLock[IP] = self.manager.Lock()
            
    def answerRequest(self, req:Message)->Message:
        '''
        Method used to answer a request.
        '''
        if len(req.entries)==0:
            return Message(Commands.RESPONSE, Versions.V2, [])
        
        
        if len(req.entries)==1 and req.entries[0].AF_id==0 and req.entries[0].getMetric()==INF:
            self.tableLock.acquire()
            ipList = list(self.entries.keys())
            self.tableLock.release()
            
            toBeSent = []
            for IP in ipList:
                try:
                    r = RIPEntry(other=self.entries[IP])
                    toBeSent.append(r)
                except KeyError:
                    continue
            m = Message(Commands.RESPONSE, Versions.V2, toBeSent)
            return m
        
        for entry in req.entries:
            pass
        
        return Message(Commands.RESPONSE, Versions.V2, [])
    
    def triggerUpdate(self)->None:
        '''
        Sends a trigger update signal to the parent process.
        '''
        try:
            kill(getppid(), TRIGGER_UPDATE_SIGNAL)
        except BaseException as e:
            logger.error(format_exc())
    
    def answerResponse(self, sender:Tuple[str,int], response:Message, myIP:str)->None:
        '''
        Method used to manage a response.
        '''
        for entry in response.entries:
            if entry.getIP() in ['0.0.0.0', '127.0.0.1']:
                logger.error(f'Entry with local IP: {entry.getIP()}.')
                continue
            
            if entry.getMetric()<0 or entry.getMetric()>INF:
                logger.error(f'Entry with wrong metric: {entry.getMetric()}.')
                continue
            
            entry.setMetric((int(min(entry.getMetric()+self.metricVals[myIP], INF))))
            entry.setNextHop(sender[0])
            key = entry.getIP()
            IPList = []
            self.tableLock.acquire()
            IPList=list(self.entries.keys())
            self.tableLock.release()
            
            if entry.getIP() in IPList:
                
                
                
                if self.entries[key].getNextHop() == entry.getNextHop():
                    self.IPLock[key].acquire()
                    self.timeout[key].reset()
                    if self.entries[key].getMetric()!= entry.getMetric():
                        self.entries[key].copy(entry)
                        self.flags[key] = Flags.CHANGED
                        self.triggerUpdate()
                        if self.entries[key].getMetric()==INF:
                            self.garbage[key].activate()
                            self.timeout[key].deactivate()
                    self.IPLock[key].release()
                else:
                    if self.entries[key].getMetric() > entry.getMetric():
                        self.IPLock[key].acquire()
                        self.entries[key].copy(entry)
                        self.flags[key] = Flags.CHANGED
                        self.timeout[key].reset()
                        self.garbage[key].deactivate()
                        self.IPLock[key].release()
                        self.triggerUpdate()
                
                
            else:
                self.tableLock.acquire()
                self.entries[key] = self.objectManager.RIPEntry(other=entry)
                self.timeout[key]=self.objectManager.Timer(self.timeoutVals[myIP])
                self.garbage[key]=self.objectManager.Timer(self.garbageVals[myIP])
                self.flags[key] = Flags.CHANGED
                self.IPLock[key] = self.manager.Lock()
                self.timeout[key].activate()
                self.triggerUpdate()
                self.tableLock.release()
                
    def checkGarbage(self)->None:
        '''
        Method used for checking the garbage timers and deleting expired routes.
        '''
        IPList = []
        self.tableLock.acquire()
        IPList = list(self.garbage.keys())
        self.tableLock.release()
        
        
        
        
        for IP in IPList:
            
            
            
           
            if self.garbage[IP].tick():
                
                self.tableLock.acquire()
                del self.garbage[IP]
                del self.timeout[IP]
                del self.flags[IP]
                del self.entries[IP]
                del self.IPLock[IP]
                self.tableLock.release()
                
            
            
            
                
    def checkTimeout(self)->None:
        '''
        Method used for checking the timeout timers.
        '''
        IPList = []
        self.tableLock.acquire()
        IPList = list(self.garbage.keys())
        self.tableLock.release()
        
        for IP in IPList:
            try:
                
                
                if self.timeout[IP].tick():
                    self.IPLock[IP].acquire()
                    self.entries[IP].setMetric(INF)
                    self.timeout[IP].deactivate()
                    self.garbage[IP].activate()
                    self.flags[IP] = Flags.CHANGED
                    self.triggerUpdate()
                    self.IPLock[IP].release()
            except KeyError:
                continue
                
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
        
        
            

    def setMetric(self, newVal:int, myIP:str, neighborIP:str)->None:
        '''
        Changes the metric for packets coming from the myIP interface.
        '''
        
        
        
        diffMetric = newVal -self.metricVals[myIP]
        self.metricVals[myIP] = newVal
        
        for IP in self.entries.keys():
            if self.entries[IP].getNextHop() == neighborIP:
                self.entries[IP].setMetric(min(self.entries[IP].getMetric()+diffMetric, INF))
            

    def getTimeout(self, myIP:str):
        return self.timeoutVals[myIP]

    def getGarbage(self, myIP:str):
        return self.garbageVals[myIP]
    
    def getMetric(self, myIP:str):
        return self.metricVals[myIP]

    def getAllEntries(self)->List[RIPEntry]:
        '''
        Returns a list of all the entries in the table.
        '''
        IPlist =[]
        self.tableLock.acquire()
        IPlist = list(self.entries.keys())
        self.tableLock.release()
        
        ret = []
        for IP in IPlist:
            try:
                e = RIPEntry(other=self.entries[IP])
                ret.append(e)
            except KeyError:
                continue
        
        return ret
    
    def getAllTimeout(self)->Dict[str,Timer]:
        
        IPlist =[]
        self.tableLock.acquire()
        IPlist = list(self.entries.keys())
        self.tableLock.release()
        
        ret = dict()
        for IP in IPlist:
            try:
                
                t = Timer(other=self.timeout[IP])
                
                ret[IP]=t
            except KeyError:
                continue
        return ret
    
    def getAllGarbage(self)->Dict[str,Timer]:
        IPlist =[]
        self.tableLock.acquire()
        IPlist = list(self.entries.keys())
        self.tableLock.release()
        
        ret = dict()
        for IP in IPlist:
            try:
                #self.IPLock[IP].acquire()
                t = Timer(other=self.garbage[IP])
                #self.IPLock[IP].release()
                ret[IP]=t
            except KeyError:
                continue
        return ret
    
    
    def getAllFlag(self)->Dict[str,Flags]:
        IPlist =[]
        self.tableLock.acquire()
        IPlist = list(self.entries.keys())
        self.tableLock.release()
        
        ret = dict()
        for IP in IPlist:
            try:
                #self.IPLock[IP].acquire()
                t = self.flags[IP]
                #self.IPLock[IP].release()
                ret[IP]=t
            except KeyError:
                continue
        return ret
    
    def getAllChangedEntries(self)->List[RIPEntry]:
        '''
        Returns all the entries that are changed. Beware returned entries are marked as unchanged when added to the result.
        '''
        
        IPlist =[]
        self.tableLock.acquire()
        IPlist = list(self.entries.keys())
        self.tableLock.release()
        
        ret = []
        for IP in IPlist:
            try:
                
                if self.flags[IP] == Flags.CHANGED:
                    e = RIPEntry(other=self.entries[IP])
                    ret.append(e)
                    self.flags[IP] = Flags.UNCHANGED
            except KeyError:
                continue
       
        return ret
