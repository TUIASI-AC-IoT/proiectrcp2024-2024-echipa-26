from time import sleep, time
from random import seed, randint

def multicast_listener(pipe):
    seed(time())
    sleep(randint(1,10))

    #TODO
    # send req

    while True:
        pass


def multicast_sender(pipe):
    while True:
        if pipe.poll(0.05):
            #TODO
            #check msg type
            #if req send directly the table
            #if update, update the routing table
            pass
        #check timers
