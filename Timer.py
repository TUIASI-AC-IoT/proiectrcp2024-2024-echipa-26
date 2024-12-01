
from time import time

class Timer:
    '''
    Clasa Timer RIPV2
    '''
    def __init__(self, timeout):
        '''
        timeout - ms
        '''
        self.timeout = timeout
        self.timer = time()*1000

    def isValid(self):
        if time()*1000-self.timer > self.timeout:
            return False
        return True
    
    def reset(self):
        self.timer = time()*1000