from socket import *

def main():
    
    my_sock = socket(AF_INET, SOCK_DGRAM)
    
    
    my_ip = '' 
    my_port = 50001
    my_sock.bind((my_ip, my_port))
    
    
    send_ip = ''
    send_port = 50000
    
    msg, addr = my_sock.recvfrom(1024, 0)
    print(f"Received: {msg.decode()} from {addr}")

    my_sock.close()

if __name__ == "__main__":
    main()
