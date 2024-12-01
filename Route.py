from Timer import *

class Route:
    def __init__(self, destination, mask, nextHop, source, cost):

        self.destination = destination
        self.mask = mask
        self.nextHop = nextHop
        self.source = source
        self.cost =cost

        self.garbage = Timer(120*1000)
        self.timeout = Timer(180*1000)

    