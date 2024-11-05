from socket import *

def main():
    
    my_sock = socket(AF_INET, SOCK_DGRAM)
    
    
    my_ip = "192.168.56.105" 
    my_port = 50000

    my_sock.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
    my_sock.bind((my_ip, my_port))
    
    
    send_ip = "192.168.56.255"
    send_port = 50001

    msg = "hello"
    my_sock.sendto(msg.encode(), (send_ip, send_port))
    print(f"Sent {msg} to {send_ip}")

    my_sock.close()

if __name__ == "__main__":
    main()
