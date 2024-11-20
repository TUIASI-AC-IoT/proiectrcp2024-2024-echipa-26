import struct

class Message:
    def __init__(self, address_family_identifier, route_tag, ipv4, subnet, next_hop, metric):
        self.address_family_identifier = address_family_identifier
        self.route_tag = route_tag
        self.ipv4 = ipv4
        self.subnet =  subnet
        self.next_hop = next_hop
        self.metric = metric

    def to_bytes(self):
        pass