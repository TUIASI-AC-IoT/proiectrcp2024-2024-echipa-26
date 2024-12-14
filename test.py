import multiprocessing
import multiprocessing.managers
from RIPEntry import *

from time import sleep
from Timer import *

def write(table):
    entries, timeout = table
    i = 0
    while True:
        entries['key'+str(i)] = RIPEntry(ip=f'{i}.{i}.{i}.{i}')
        timeout['key'+str(i)] = Timer(30)
        timeout['key'+str(i)].activate()
        sleep(1)
        i = i+1
        i=i%256

def show(table):
    entries, timeout = table
    while True:
        for i in entries:
            print(f'Key: i\nVal: {entries[i]}')
        sleep(3)


def main():
    m = multiprocessing.Manager()
    
    entries = m.dict()
    timeout = m.dict()
    table = (entries, timeout)
    w = multiprocessing.Process(target=write, args =(table,))
    s = multiprocessing.Process(target=show, args=(table,))
    
    w.start()
    s.start()
    
    
    w.join()
    s.join()
    
    m.shutdown()