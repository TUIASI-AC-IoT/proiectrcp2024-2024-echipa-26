import multiprocessing
import multiprocessing.managers

from RIPEntry import *

from time import sleep
from Timer import *




class MyManager(multiprocessing.managers.BaseManager):
    pass

MyManager.register('RIPEntry', RIPEntry)
MyManager.register('Timer', Timer)



def write(q, m):
    entries, timeout = q
    
    entries['lol'] = m.RIPEntry(ip='lol')
    timeout['lol'] = m.Timer(30)
    sleep(5)
    p = entries['lol']
    print(p.getIP())
    print(timeout['lol'].getTimer())
    
    

def show(q, m):
    entries, timeout = q
    
    sleep(2)
    entries['lol'].setIP('atre')
    timeout['lol'].activate()

        

def main():
    
    
    m = MyManager()
    p = multiprocessing.Manager()
    m.start()
    
    entries = p.dict()
    timeout = p.dict()
    entries['lol'] = 'mata'
    table = (entries, timeout)
    
    w = multiprocessing.Process(target=write, args =(table,m,))
    s = multiprocessing.Process(target=show, args=(table,m,))
    
    w.start()
    s.start()
    
    
    w.join()
    s.join()
    
    m.shutdown()
    p.shutdown()
    
    

if __name__ =="__main__":
    main()