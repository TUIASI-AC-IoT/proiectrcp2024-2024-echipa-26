import multiprocessing.managers
import multiprocessing.queues
from time import sleep, time
from random import seed, randint
from os import environ, listdir, chdir, getpid, system
from ProcessTarget import *
from Message import *
import multiprocessing
from multiprocessing.managers import BaseManager
from CLI import *



class MyManager(multiprocessing.managers.BaseManager):
    pass


MyManager.register('RIPEntry', RIPEntry)
MyManager.register('Timer', Timer)

def main():

    IPSubnetList = [] # lista de tuple
    ID = environ['ID']
    path = f'/home/tc/pr/cfg/r{ID}'
    for config in listdir(path):
        configPath = path+f'/{config}'
        file = open(configPath)
        lines = file.readlines()
        IPSubnetList.append((lines[2][3:-1],lines[3][7:-1]))

    #TODO cfg
    #read cfg (timers etc)
    
    
    seed(time())
    sleep(randint(1,10))

    
    
    
    myManager = MyManager()
    myManager.start()
    manager = multiprocessing.Manager()
    
    timeout = manager.dict()
    garbage = manager.dict()
    flags = manager.dict()
    entries = manager.dict()

    


    for ip in IPSubnetList:
        
        e = myManager.RIPEntry()
        e.setIP(ip[0])
        e.setNextHop(ip[0])
        e.setSubnet(ip[1])

        entries[ip[0]] = e
        flags[ip[0]] = Flags.UNCHANGED
        timeout[ip[0]] = myManager.Timer(40)
        garbage[ip[0]] = myManager.Timer(30)
    
    table = (entries, flags, timeout, garbage)
    sender, listener = multiprocessing.Pipe(False)
    
    
    listenerProcess = multiprocessing.Process(target = multicastListen, args=(listener,IPSubnetList))
    senderProcess = multiprocessing.Process(target = multicastSenderOld, args=(sender,IPSubnetList))

    listenerProcess.start()
    senderProcess.start()




    print('DONE')




    chdir('/home/tc')
    
    bashrc = open('.ashrc', 'a')
    toWrite = f'\nalias stop=\"sudo kill {listenerProcess.pid} {senderProcess.pid} {getpid()}\"\n'
    toWrite = toWrite+f'alias show=\"sudo kill -s sigusr1 {senderProcess.pid}\"\n'
    toWrite = toWrite + 'echo \"stop=kill\"\necho \"show=display table\"\n'
    bashrc.write(toWrite)
    bashrc.close()

    system("echo \"run source ~/.ashrc\n\"")

    


    listenerProcess.join()
    senderProcess.join()

    myManager.shutdown()
    manager.shutdown()
    
    #test doar daca se vede interfata pe tinycore
    wrapper(CLI)

    


if __name__=="__main__":
    main()
    