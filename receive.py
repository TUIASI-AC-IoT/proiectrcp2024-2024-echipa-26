from socket import *
import struct
def main():
    
    sock = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP)
    multicast = '224.0.0.9'
    sock.bind((multicast, ''))
    mreq = struct.pack("4sl", socket.inet_aton(multicast), socket.INADDR_ANY)

    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

    
    msg, addr = sock.recvfrom(1024, 0)
    print(f"Received: {msg.decode()} from {addr}")

    sock.close()

if __name__ == "__main__":
    main()
