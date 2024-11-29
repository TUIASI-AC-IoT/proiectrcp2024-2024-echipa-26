from time import sleep, time
from random import seed, randint
from os import environ, listdir, chdir
from process_target import *

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
    
    
    seed(time())
    sleep(randint(1,10))

    sender, listener = Pipe(False)
    listener_process = Process(target = multicast_listener, args=(listener,ipList,))
    sender_process = Process(target = multicast_sender, args=(sender,ipList,))

    listener_process.start()
    sender_process.start()

    listener_process.join()
    sender_process.join()

    chdir('home/tc')
    details = open('info', 'w')
    toWrite = f'Listener: {listener_process.pid}\n' + f'Sender: {sender_process.pid}\n'+f'Run sudo kill -s SIGUSR1 {sender_process.pid} to display the routing table'
    details.write(toWrite)
    # print(f'Listener: {listener_process.pid}')
    # print(f'Sender: {sender_process.pid}')
    # print(f'Run kill -s SIGUSR1 {sender_process.pid} to display the routing table')


if __name__=="__main__":
    main()