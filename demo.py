import socket


multicastPort = 520
multicastIP = '224.0.0.9'
multicast = (multicastIP, multicastPort)

R1IP1 = '192.168.1.1'
R1IP2 = '192.168.2.1'

R2IP1 ='192.168.1.2'
R2IP2 ='192.168.3.2'


def R1():
    s1 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, proto=17)
    s1.bind((R1IP1, multicastPort))

    s2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, proto=17)
    s2.bind((R1IP2, multicastPort))

    s1.sendto(bytes('Hello', 'ascii'), (R2IP2, multicastPort))


def R2():
    s1 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, proto=17)
    s1.bind((R2IP1, multicastPort))

    s2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, proto=17)
    s2.bind((R2IP2, multicastPort))

    d,s =s1.recvfrom()
    print(s)

R1()
