from time import sleep, time
from random import seed, randint
from os import environ, listdir
from process_target import *

from multiprocessing import Process, Pipe
def main():

    ipList = []
    ID = environ['ID']
    path = f'/home/tc/pr/r{ID}'
    for config in listdir(path):
        configPath = path+f'/{config}'
        file = open(configPath)
        lines = file.readlines()
        ipList.append(lines[2][3:-1])
    
    print(ipList)
    return



    seed(time())
    sleep(randint(1,10))

    sender, listener = Pipe(False)
    listener_process = Process(target =multicast_listener, args=(listener,))
    sender_process = Process(target = multicast_sender, args=(sender,))

    listener_process.start()
    sender_process.start()

    listener_process.join()
    sender_process.join()

if __name__=="__main__":
    main()