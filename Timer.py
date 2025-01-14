
from time import time
from random import randint

class Timer:
    '''
    Clasa Timer RIPV2
    '''
    def __init__(self, timeout=0, other=None):
        '''
        timeout - s
        '''
        
        if other is not None:
            self.timeout = other.getTimeout()
            self.timer = other.getTimer()
            self.baseTimeout =other.getBaseTimeout()
            return
            
        self.timeout = timeout
        self.timer = -1
        self.baseTimeout = timeout
    
    def getTimeout(self):
        return self.timeout
    
    def setTimeout(self, newVal):
        self.timeout = newVal
        
    def setBaseTimeout(self, newVal):
        self.baseTimeout = newVal
        
    def getBaseTimeout(self):
        return self.baseTimeout
        
    def getTimer(self):
        return self.timer
    
    def activate(self):
        if self.timer == -1:
            self.timer = time()
        
    def deactivate(self):
        self.timer = -1
    
    def tick(self):
        if self.timer == -1:
            return False
        if time()-self.timer>self.timeout:
            return True
        return False
    
    def isWorking(self):
        return not self.timer == -1
        
    def reset(self, random=False, val=5):
        if self.timer == -1:
            return
        if random == False:
            self.timer = time()
        
        if random == True:
            original = self.baseTimeout
            i = randint(0,1)
            if i%2 == 0:
                self.setTimeout(original+randint(0,val))
            else:
                self.setTimeout(original-randint(0,val))
            self.timer = time()
