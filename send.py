from socket import *

def main():
    
    sock = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP)
    sock.setsockopt(IPPROTO_IP, IP_MULTICAST_TTL)
    
    multicast = '224.0.0.9'


    
    
    send_ip = "192.168.56.255"
    send_port = 50001

    msg = "hello"
    sock.sendto(msg, multicast)
    print(f"Sent {msg} to {send_ip}")

    sock.close()

if __name__ == "__main__":
    main()
