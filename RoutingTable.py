from Timer import *

class RoutingTable:
    def __init__(self):
        self.dict = dict()
        self.update = Timer(30*1000)

    def addRoute(self, route):
        pass

    def updateRoute(self, key, route):
        pass

    def __str__(self):
        for key, value in self.dict:
            print(str(key)+' '+str(value))

    def toBytes(self):
        pass