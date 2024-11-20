import socket

# 17 e protocolul udp
sender1 = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM, proto=17)


ip1 ='192.168.1.1'
ip2=''


multicast_port = 520
multicast_ip = '224.0.0.9'

multicast = (multicast_ip, multicast_port)

sender1.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 1)
sender1.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_IF, socket.inet_aton(ip1))


sender1.sendto("buna", multicast)

sender1.close()
