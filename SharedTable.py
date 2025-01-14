from typing import List,Tuple, Dict
from os import kill, getppid
import multiprocessing



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
            return Message(Commands.RESPONSE, Versions.V2, [])
        
        
        if len(req.entries)==1 and req.entries[0].AF_id==0 and req.entries[0].getMetric()==INF:
            toBeSent = list(self.entries.values())
            m = Message(Commands.RESPONSE, Versions.V2, toBeSent)
            return m
        
        for entry in req.entries:
            pass
        
        return Message(Commands.RESPONSE, Versions.V2, [])
    
    def triggerUpdate(self)->None:
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
                self.entries[IP].setMetric(INF)
                self.timeout[IP].deactivate()
                self.garbage[IP].activate()
                self.flags[IP] = Flags.CHANGED
                self.triggerUpdate()
                
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
        
        ret = []
        for IP in list(self.entries.keys()):
            try:
                e = RIPEntry(other=self.entries[IP])
                ret.append(e)
            except KeyError:
                continue
        return ret
    
    def getAllTimeout(self)->Dict[str,Timer]:
        ret = dict()
        for IP in list(self.timeout.keys()):
            try:
                t = Timer(other=self.timeout[IP])
                ret[IP]=t
            except KeyError:
                continue
        return ret
    
    def getAllGarbage(self)->Dict[str,Timer]:
        ret = dict()
        for IP in list(self.garbage.keys()):
            try:
                g = Timer(other=self.garbage[IP])
                ret[IP]=g
            except KeyError:
                continue
        return ret
    
    
    def getAllFlag(self)->Dict[str,Flags]:
        ret = dict()
        for IP in list(self.flags.keys()):
            try:
                f = self.flags[IP]
                ret[IP] = f
            except KeyError:
                continue
        return ret
    
    def getAllChangedEntries(self)->List[RIPEntry]:
        '''
        Returns all the entries that are changed. Beware returned entries are marked as unchanged when added to the result.
        '''
        ret = []
        for IP in list(self.entries.keys()):
            try:
                if self.flags[IP] == Flags.CHANGED:
                    e = RIPEntry(other=self.entries[IP])
                    ret.append(e)
                    self.flags[IP] = Flags.UNCHANGED
            except KeyError:
                continue
        
        return ret
