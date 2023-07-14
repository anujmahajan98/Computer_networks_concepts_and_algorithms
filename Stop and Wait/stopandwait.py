from typing import BinaryIO
import hashlib
import socket
import struct
import pickle

sndSeqnNum = 0
rcvSeqnNum = 0


def stopandwait_server(iface:str, port:int, fp:BinaryIO) -> None:
    serverSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    ipAddress = findIP(iface, port)
    serverSocket.bind((ipAddress, port))
    
    #Creating a new dictionary to send the acknowledgement from server
    sendData = {}
    print("Hello, I am server")
    global rcvSeqnNum
    
    while True:
        #Assigning 1024 bytes for receiving the message as pickle.dumps() will increase the size of original 256 bytes of message
        #Received error multiple times while sending the message to server becasue of this size parameter, that's why set it to significantly large number
        message,address = serverSocket.recvfrom(2096)
        
        #uNpickled the message got from client by using loads. loads work same as unpack of struct method.
        receivedMsg = pickle.loads(message)
        
        #If message is empty break the loop and close everything
        if len(receivedMsg['message'])  == 0 :
            break

        if not receivedMsg['message']:
            break

        #If ACK Type is 20 that means we got the message 
        if receivedMsg['ackType'] == 20:
            #If seqence number doesn't match on client and server, notify client to resend the packate
            if receivedMsg['seqNo'] != rcvSeqnNum:
                sendData['ackType'] = 10
                sendData['seqNo'] = receivedMsg['seqNo']
                datagram = pickle.dumps(sendData,protocol=pickle.DEFAULT_PROTOCOL)
                serverSocket.sendto(datagram,address)
            #else, everything is OK, write to the file
            else:
                sendData['ackType'] = 10
                sendData['seqNo'] = receivedMsg['seqNo']
                datagram = pickle.dumps(sendData,protocol=pickle.DEFAULT_PROTOCOL)
                serverSocket.sendto(datagram,address)
                if rcvSeqnNum == 1: 
                    rcvSeqnNum = 0
                else:
                    rcvSeqnNum = 1
                if not receivedMsg['message'] or len(receivedMsg['message']) == 0:
                    break
                else:
                    fp.write(receivedMsg['message'])

def stopandwait_client(host:str, port:int, fp:BinaryIO) -> None:
    clientSocket =socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    print("Hello, I am a client")
    ipAddress = findIP(host, port)
    address =(ipAddress,port)
    ackType = 20
   
    global sndSeqnNum
    with open(fp.name, "rb") as f:
        message = f.read(256)
        dataDict = {'message':message , 'ackType':ackType, 'seqNo':sndSeqnNum}

        #Received error as Unpickling Error - Invalid load Key at first as I didn't use the DEFAULT_PROTOCOL.
        #Set the protocol to correctly use the dumps() method
        datagram = pickle.dumps(dataDict,protocol=pickle.DEFAULT_PROTOCOL)

        while message:
            clientSocket.sendto(datagram,address)

            #Taking time out as 50ms as mentioned on course wiki
            clientSocket.settimeout(0.5)
            try :
                receivedData,addr = clientSocket.recvfrom(1024)
                clientSocket.settimeout(0)
            except socket.timeout:
                continue

            receivedMsg = pickle.loads(receivedData)
            if receivedMsg['ackType'] == 10:
                if receivedMsg['seqNo'] == sndSeqnNum:  
                    if sndSeqnNum == 1:
                        sndSeqnNum = 0
                    else:
                        sndSeqnNum = 1
                    message = f.read(256)
                    ackType = 20
                    dataDict = {'message':message, 'ackType':ackType, 'seqNo':sndSeqnNum}
                    datagram = pickle.dumps(dataDict)
                else:
                    continue
        
        #If we are done with reading all the file send 0 byte message
        #way of sending 0 byte message is discussed with Alex in lab discussions session
        dataDict = {'message':bytes(), 'ackType':ackType, 'seqNo':sndSeqnNum}

        datagram = pickle.dumps(dataDict)
        clientSocket.sendto(datagram,address)
        f.close()

def findIP(domain, port):
    ip_addr = ''
    protocol_type = socket.IPPROTO_UDP
    addressInfo = socket.getaddrinfo(domain, port, family = socket.AF_UNSPEC, proto = protocol_type)
    for address in addressInfo:
        if address[0] == socket.AddressFamily.AF_INET:
            ip_addr = address[4][0]
            break
    return ip_addr


'''

#Did the code by using struct method, worked fine on lunar and solar even on 30% loss channel but failed on autograder not sure why
#that's wht tried with pickle method
#Keeping this for reference 

def stopandwait_server(iface:str, port:int, fp:BinaryIO) -> None:
    serverSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    ipAddress = findIP(iface, port)
    serverSocket.bind((ipAddress, port))
    global rcvSeqnNum
    print('Hello, I am a server')
    while True:
        message,address = serverSocket.recvfrom(258)

        if message  == b'':
            break
        if not message:
            break

        #If there is any message from client, it must be in packet.
        #But packet length is 258 as messageLen = 256 and additional 2 bytes of packet structure
        msgLen = (len(message) - 2)
        recvPackate = struct.Struct('BB'+ str(msgLen) + 's')
        (ackType,sqnNo, message) = recvPackate.unpack(message)
        if ackType == 20:
            if sqnNo != rcvSeqnNum:
                ackType = 10
                sendMsgFormat = struct.Struct('BB')
                sendPacket = sendMsgFormat.pack(ackType, sqnNo)
                serverSocket.sendto(sendPacket,address)
            else:
                ackType = 10
                sendMsgFormat = struct.Struct('BB')
                sendPacket = sendMsgFormat.pack(ackType,sqnNo)
                serverSocket.sendto(sendPacket,address)
                if rcvSeqnNum == 1:
                    rcvSeqnNum = 0
                else:
                    rcvSeqnNum = 1
                if not message or message == b'':
                    break
                else:
                    fp.write(message)
        else:
            continue
def stopandwait_client(host:str, port:int, fp:BinaryIO) -> None:
    clientSocket =socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    print("Hello, I am a client")
    ipAddress = findIP(host, port)
    address =(ipAddress,port)
    ackType = 20
    global sndSeqnNum
    with open(fp.name, "rb") as file:
        message = file.read(256)
        messageFormat = struct.Struct('BB' + str(len(message)) + 's')
        packet = messageFormat.pack(ackType, sndSeqnNum, message)

        while message:
            clientSocket.sendto(packet,address)
            clientSocket.settimeout(0.5)
            try :
                receivedData,addr = clientSocket.recvfrom(258)
                clientSocket.settimeout(0)
            except socket.timeout:
                continue
            recvMsgFormat = struct.Struct('BB')
            (ackType, sequenceNum) = recvMsgFormat.unpack(receivedData)
            if ackType == 10:
                if sequenceNum == sndSeqnNum:  # update the global variables to alternate states # this is done to check for duplicacy with previous message
                    if sndSeqnNum == 1:
                        sndSeqnNum = 0
                    else:
                        sndSeqnNum = 1
                    message = file.read(256)
                    ackType = 20
                    messageFormat = struct.Struct('BB' + str(len(message)) + 's')
                    packet = messageFormat.pack(ackType, sndSeqnNum, message)
                else:
                    continue

        clientSocket.sendto(b'',address)
        file.close()

'''
