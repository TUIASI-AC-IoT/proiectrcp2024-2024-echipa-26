import multiprocessing.queues
from time import sleep, time
from random import seed, randint
from os import environ, listdir, chdir, getpid, system
from ProcessTarget import *
from Message import *
import multiprocessing
from multiprocessing.managers import BaseManager



class MyManager(BaseManager):
    pass

MyManager.register('RIPEntry', RIPEntry)
MyManager.register('Timer', Timer)


def main():

    ipList = [] # lista de tuple
    ID = environ['ID']
    path = f'/home/tc/pr/cfg/r{ID}'
    for config in listdir(path):
        configPath = path+f'/{config}'
        file = open(configPath)
        lines = file.readlines()
        ipList.append((lines[2][3:-1],lines[3][7:-1]))

    #TODO cfg
    #read cfg (timers etc)
    
    
    seed(time())
    sleep(randint(1,10))

    
    
    
    interfaces =dict()
    timeout = dict()
    garbage = dict()
    flags = dict()
    entries = dict()
    
    table = (entries, timeout, garbage, flags)
    
    for ip in ipList:
        ent = RIPEntry()
        ent.setIP(ip[0])
        ent.setSubnet(ip[1])
        ent.setNextHop(ip[0])
        ent.setMetric(0)
        entries[ip[0]] = ent
    # entries       =   map<ip_dest     ,   RIPEntry>
    # timeout       =   map<ip_dest     ,   Timer>
    # garbage       =   map<ip_dest     ,   Timer>
    # flags         =   map<ip_dest     ,   flags>
    # interfaces va fi folosit pentru split horizon
    # interfaces    =   map<ip_vecin    ,   my_ip>
    
    queue = multiprocessing.Queue(256)
    queue.put_nowait((table, interfaces))
    
    sender, listener = multiprocessing.Pipe(False)
    
    
    listenerProcess = multiprocessing.Process(target = multicastListen, args=(listener,ipList,queue))
    senderProcess = multiprocessing.Process(target = multicastSender, args=(sender,ipList,queue))

    listenerProcess.start()
    senderProcess.start()









    chdir('/home/tc')
    
    bashrc = open('.ashrc', 'a')
    toWrite = f'\nalias stop=\"sudo kill {listenerProcess.pid} {senderProcess.pid} {getpid()}\"\n'
    toWrite = toWrite+f'alias show=\"sudo kill -s sigusr1 {senderProcess.pid}\"\n'
    toWrite = toWrite + 'echo \"stop=kill\"\necho \"show=display table\"\n'
    bashrc.write(toWrite)
    bashrc.close()

    system("echo \"run source ~/.ashrc\n\"")

    t = time()
    while True:
        if time()-t>60:
            table, interfaces = getValues(queue)
            entries, timeout, garbage, flags = table
            for key in entries.keys():
                print(entries[key].getIP())
            table = (entries, timeout, garbage, flags)
            putValues(queue, (table, interfaces))
            t= time()


    listenerProcess.join()
    senderProcess.join()
    

    


if __name__=="__main__":
    main()
    