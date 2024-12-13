import socket
import struct
import select

multicastPort = 520
multicastIP = '224.0.0.9'

listenIP=['192.168.1.1', '192.168.2.1']
sendIP = ['192.168.1.2', '192.168.3.2']

def listen():
    
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, proto=17)
    s.sender.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(('', multicastPort))
    
    
    receiver = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, proto=17)
    receiver.bind((multicastIP, multicastPort))
    for ip in listenIP:
        r = struct.pack("=4s4s", socket.inet_aton(multicastIP), socket.inet_aton(ip))
        receiver.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, r)

    socket_list =[s, receiver]
        
        
    while True:
        ready_to_read, _,_ = select.select(socket_list,[],[], 0.1)
        for receiver in ready_to_read:
            data, s = receiver.recvfrom(1024)
            print(data.decode('ascii')+' '+str(s) + ' '+str(receiver.getsockname()))
            
            
            

def send():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, proto=17)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(('', multicastPort))
    s.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 1)
    s.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_LOOP, 0)
    for ip in sendIP:
        s.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_IF, socket.inet_aton(ip))
        
    s.sendto(bytes('hey', 'ascii'), (listenIP[0], multicastPort))
    s.sendto(bytes('multicast', 'ascii'), (multicastIP, multicastPort))
        

if __name__=="__main__":
    pass