

class RIPEntry:
    '''
    RIPEntry
    '''
    #de completat cu parametri si chestii
    def __init__(self, address_family_identifier, route_tag, ipv4, subnet, next_hop, metric):
        self.address_family_identifier = address_family_identifier
        self.route_tag = route_tag
        self.ipv4 = ipv4
        self.subnet = subnet
        self.next_hop = next_hop
        self.metric = metric

    def __str__(self):
        for eticheta, val in vars(self).items():
            print(f'{eticheta} : {val}')

