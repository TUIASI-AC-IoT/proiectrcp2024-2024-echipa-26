
from time import time

class Timer:
    '''
    Clasa Timer RIPV2
    '''
    def __init__(self, timeout):
        '''
        timeout - s
        '''
        self.timeout = timeout
        self.timer = -1
    

        
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
        if time()-self.timer()>self.timeout:
            return True
        return False
    
    def isRunning(self):
        return not (self.timer == -1)
    
    
    def reset(self):
        if self.timer != -1:
            self.timer = time()

    