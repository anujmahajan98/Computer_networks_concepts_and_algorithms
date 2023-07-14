from typing import BinaryIO
import socket

def file_server(iface:str, port:int, use_udp:bool, fp:BinaryIO) -> None:
    if use_udp:
        sck = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sck.bind((iface,port))
        print('Hello, I am a server')
        file = open(fp.name, "w",errors = "ignore")
        while 1:
            data,address = sck.recvfrom(256)
            data = data.decode('utf-8','ignore')
            if data[len(data)-3:len(data)] != 'eof':
                file.write(data)
            else:
                file.write(data[:len(data)-3])
                break
        sck.sendto("File received".encode('utf-8','ignore'),address)
        file.close()
        sck.close()
    else:
        sck = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sck.bind((iface, port))
        sck.listen()
        print('Hello, I am a server')
        conn, addr = sck.accept()
        with open(fp.name, "wb") as file:
            while 1:    
                data = conn.recv(256)
                if data:
                    file.write(data)
                else:
                    break
            file.close()
        conn.close()
        
def file_client(host:str, port:int, use_udp:bool, fp:BinaryIO) -> None:
    if use_udp:
        sck = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        address = findIP(host, port, use_udp)
        address = (address,port)
        print('Hello, I am a client')
        file = open(fp.name, "r", errors = 'ignore')
        fileData = file.read()
        i = 0
        fileLength = len(fileData)
        while fileLength > 256:
            dataToSend = fileData[i:i+256]
            sck.sendto(dataToSend.encode('utf-8','ignore'),address)
            i = i+256
            fileLength -= 256
        dataToSend = fileData[i:]
        sck.sendto(dataToSend.encode('utf-8','ignore'),address)
        dataToSend = "eof"
        sck.sendto(dataToSend.encode('utf-8','ignore'),address)
        data,addr = sck.recvfrom(256)
        data = data.decode('utf-8','ignore')
        if data == 'File received':
            sck.close()
    else:
        sck = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print('Hello, I am a client')
        address = findIP(host, port, use_udp)
        host = address
        if address == '':
            host = (socket.gethostbyname(host),port)
        sck.connect((host, port))
        with open(fp.name, "rb") as file:
            while True:
                fileData = file.read(256)
                if fileData:
                    sck.send(fileData)
                else:
                    break
            file.close()
        sck.close()

def findIP(domain, port, udp):
    ip_addr = ''
    if udp:
        protocol_type = socket.IPPROTO_UDP
    else:
        protocol_type = socket.IPPROTO_TCP
    addressInfo = socket.getaddrinfo(domain, port, family = socket.AF_UNSPEC, proto = protocol_type)
    for address in addressInfo:
        if address[0] == socket.AddressFamily.AF_INET:
            ip_addr = address[4][0]
            break
    return ip_addr
