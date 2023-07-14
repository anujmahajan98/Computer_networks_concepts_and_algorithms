from datetime import datetime
from typing import BinaryIO
import socket
import pickle
import time
import hashlib

def gbn_server(iface:str, port:int, fp:BinaryIO) -> None:
    serverSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    ipAddress = findIP(iface, port)
    serverSocket.bind((ipAddress, port))
    print("Hello, I am a server")
    flag = 1
    PrevSeqNo = 0
    abc = 0 
    while flag:
        count = 0
        nackCount = 0
        messageToWrite = bytearray()
        sendData = {}
        while 1:
            message,address = serverSocket.recvfrom(2096)
            receivedMsg = pickle.loads(message)
            if receivedMsg['msgsize']  == 0 :
                sendData['nextSeqNo'] = -1
                #print('Last chunk')
                datagram = pickle.dumps(sendData,protocol=pickle.DEFAULT_PROTOCOL)
                serverSocket.sendto(datagram,address)
                flag = 0
                break
            if len(receivedMsg['message'])< 1024:
                if messageToWrite != b'':
                    fp.write(messageToWrite)
                fp.write(receivedMsg['message'])
                flag = 0
                sendData['nextSeqNo'] = -1
                #print('last chunk < 512')
                datagram = pickle.dumps(sendData,protocol=pickle.DEFAULT_PROTOCOL)
                serverSocket.sendto(datagram,address)
                break

            if not receivedMsg['message']:
                flag = 0
                break

            seqNo = receivedMsg['nextSeqNo']
            windowLength = receivedMsg['windowsize']
            if seqNo == PrevSeqNo:
                PrevSeqNo += 1
                count += 1
                messageToWrite.extend(receivedMsg['message'])
                if count == windowLength:
                    fp.write(messageToWrite)
                    sendData['nextSeqNo'] = seqNo + 1
                    sendData['ack'] = 'ACK'
                    datagram = pickle.dumps(sendData,protocol=pickle.DEFAULT_PROTOCOL)
                    serverSocket.sendto(datagram,address)
                    break
            else:
                PrevSeqNo -= count
                messageToWrite = bytearray()
                sendData['nextSeqNo'] = PrevSeqNo
                nackCount += 1
                count = 0
                if nackCount == 1:
                    sendData['ack'] = 'NACK'
                    datagram = pickle.dumps(sendData,protocol=pickle.DEFAULT_PROTOCOL)
                    serverSocket.sendto(datagram,address)
    fp.close()


def gbn_client(host:str, port:int, fp:BinaryIO) -> None:
    clientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    print("Hello, I am a client")
    ipAddress = findIP(host, port)
    address =(ipAddress,port)
    windowSize = 5
    buffer = []
    i = 0
    initialData = fp.read(1024)
    dataDict = {}
    nextSeqNo = 0
    while initialData:
        buffer.append(initialData)
        initialData = fp.read(1024)
        i += 1
    index = 0
    while index < len(buffer):
        base = nextSeqNo
        for i in range(base,min(base+windowSize,len(buffer))):
            message = buffer[i]
            dataDict = {'message':message , 'nextSeqNo':i, 'windowsize':min(windowSize,len(buffer)-base), 'msgsize':len(message) + 3}
            datagram = pickle.dumps(dataDict,protocol=pickle.DEFAULT_PROTOCOL)
            clientSocket.sendto(datagram,address)
            nextSeqNo += 1
        clientSocket.settimeout(0.06)
        try :
            receivedData,addr = clientSocket.recvfrom(2096)
            receivedMsg = pickle.loads(receivedData)
            if receivedMsg['nextSeqNo'] == -1:
                index = 999999
                break
            if receivedMsg['ack'] == 'ACK':
                index = nextSeqNo
                windowSize += 1
                base = receivedMsg['nextSeqNo']
                nextSeqNo = base
                clientSocket.settimeout(0)
            else:
                if windowSize // 2 >= 1:
                    windowSize //= 2
                base = receivedMsg['nextSeqNo']
                nextSeqNo = base
                clientSocket.settimeout(0)
            #print('windowSize -> ',windowSize)
        except socket.timeout:
            if windowSize // 2 >= 1:
                windowSize //= 2
            base = index
            nextSeqNo = base
            continue
    if index != 999999:    
        while 1:
            dataDict = {'message':bytes(), 'nextSeqNo':-10, 'windowsize':0, 'msgsize':0}
            datagram = pickle.dumps(dataDict)
            clientSocket.sendto(datagram,address)
            clientSocket.settimeout(0.06)
            try :
                receivedData,addr = clientSocket.recvfrom(1024)
                receivedMsg = pickle.loads(receivedData)
                print('last Seq No -> ',receivedMsg['nextSeqNo'])
                if receivedMsg['nextSeqNo'] == -1:
                    clientSocket.settimeout(0)
                    print('EOF')
                    break
            except socket.timeout:
                continue
    fp.close()

        
    

def findIP(domain, port):
    ip_addr = ''
    protocol_type = socket.IPPROTO_UDP
    addressInfo = socket.getaddrinfo(domain, port, family = socket.AF_UNSPEC, proto = protocol_type)
    for address in addressInfo:
        if address[0] == socket.AddressFamily.AF_INET:
            ip_addr = address[4][0]
            break
    return ip_addr
