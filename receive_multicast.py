import socket
import struct

receiver1 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, proto=17)

ip1='192.168.1.2'
ip2=''



multicast_port = 520
multicast_ip = '224.0.0.9'

receiver1.bind((multicast_ip, multicast_port))


r = struct.pack("=4s4s", socket.inet_aton(multicast_ip), socket.inet_aton(ip1))

receiver1.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, r)


b, s = receiver1.recvfrom(1024)

print(b.decode()+" from "+s)