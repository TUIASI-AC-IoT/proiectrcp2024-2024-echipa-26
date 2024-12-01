from time import sleep, time
from random import seed, randint
from os import environ, listdir, chdir, getpid
from ProcessTarget import *
from Message import *
from multiprocessing import Process, Pipe
def main():

    ipList = []
    ID = environ['ID']
    path = f'/home/tc/pr/cfg/r{ID}'
    for config in listdir(path):
        configPath = path+f'/{config}'
        file = open(configPath)
        lines = file.readlines()
        ipList.append(lines[2][3:-1])

    #read cfg (timers etc)
    
    
    seed(time())
    sleep(randint(1,10))

    sender, listener = Pipe(False)
    listenerProcess = Process(target = multicastListen, args=(listener,ipList,))
    senderProcess = Process(target = multicastSender, args=(sender,ipList,))

    listenerProcess.start()
    senderProcess.start()

    chdir('/home/tc')
    details = open('info', 'w')
    toWrite = f'Main: {getpid()}\n'+'Listener: {listenerProcess.pid}\n' + f'Sender: {senderProcess.pid}\n'+f'Run sudo kill -s SIGUSR1 {senderProcess.pid} to display the routing table\n'
    details.write(toWrite)
    details.close()

    listenerProcess.join()
    senderProcess.join()

    


if __name__=="__main__":
    main()
    