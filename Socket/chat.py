import socket
import threading
import os
import sys
def multi_thread(conn,addr) -> None:
    count = -1
    connectionClosed = False
    while conn:
        data = conn.recv(1024).decode()
        print('got message from',addr)
        if data == 'goodbye':
            serverResp = 'farewell'
            connectionClosed = True
        elif data == 'hello':
            serverResp = 'world'
        elif data == 'exit':
            serverResp = 'ok'
            conn.send(serverResp.encode())
            conn.close()
            os._exit(1)
        else:
            serverResp = data
        serverResp = serverResp[:min(255,len(serverResp))]
        conn.send(serverResp.encode())
        if connectionClosed:
            conn.close()
            sys.exit()

def chat_server(iface:str, port:int, use_udp:bool) -> None:
    if use_udp:
        sck = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sck.bind((iface,port))
        print('Hello, I am a server')
        while True:
            data,address = sck.recvfrom(1024)
            data = data.decode()
            print('got message from',address)
            if data == 'goodbye':
                serverResp = 'farewell'
                connectionClosed = True
            elif data == 'hello':
                serverResp = 'world'
            elif data == 'exit':
                serverResp = 'ok'
                sck.sendto(serverResp.encode(),address)
                break
            else:
                serverResp = data
            serverResp = serverResp[:min(255,len(serverResp))]
            sck.sendto(serverResp.encode(),address)
    else:
        sck = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sck.bind((iface, port))
        sck.listen()
        print('Hello, I am a server')
        count = -1
        while True:
            conn, addr = sck.accept()
            if conn:
                count += 1
                print('connection ', count, ' from',str(addr))
            temp = threading.Thread(target=multi_thread,args=(conn,addr))
            temp.start()
        
def chat_client(host:str, port:int, use_udp:bool) -> None:
    if use_udp:
        sck = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        print('Hello, I am a client')
        address = findIP(host, port, use_udp)
        address = (address,port)
        while True:
            clientMessage = input()
            clientMessage = clientMessage[:min(255,len(clientMessage))]
            sck.sendto(clientMessage.encode(),address)
            data,addr = sck.recvfrom(1024)
            data = data.decode()
            print(data)
            if data == 'farewell' or (data == 'ok' and clientMessage == 'exit'):
                break
    else:
        sck = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        address = findIP(host, port, use_udp)
        host = address
        if address == '':
            host = (socket.gethostbyname(host),port)
        sck.connect((host, port))
        print('Hello, I am a client')
        while True:
            clientMessage = input()
            clientMessage = clientMessage[:min(255,len(clientMessage))]
            sck.send(clientMessage.encode())
            data = sck.recv(1024).decode()
            print(data)
            if data == 'farewell' or (data == 'ok' and clientMessage == 'exit'):
                break
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
