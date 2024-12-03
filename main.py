from time import sleep, time
from random import seed, randint
from os import environ, listdir, chdir, getpid, system
from ProcessTarget import *
from Message import *
from multiprocessing import Process, Pipe
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

    sender, listener = Pipe(False)
    listenerProcess = Process(target = multicastListen, args=(listener,ipList,))
    senderProcess = Process(target = multicastSender, args=(sender,ipList,))

    listenerProcess.start()
    senderProcess.start()

    chdir('/home/tc')
    
    bashrc = open('.ashrc', 'a')
    toWrite = f'\nalias stop=\"sudo kill {listenerProcess.pid} {senderProcess.pid} {getpid()}\"\n'
    toWrite = toWrite+f'alias show=\"sudo kill -s sigusr1 {senderProcess.pid}\"\n'
    toWrite = toWrite + 'stop=kill\nshow=display table\n'
    bashrc.write(toWrite)
    bashrc.close()

    system("echo \"run source ~/.ashrc\"")

    


    listenerProcess.join()
    senderProcess.join()

    


if __name__=="__main__":
    main()
    