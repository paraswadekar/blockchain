from utils import *
import Crypto
import socket

def create_client(message):
    host = '127.0.0.1'
    port = 5000
    mySocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    mySocket.connect((host,port))
    mySocket.send(message.encode("utf-8"))
#    mySocket.close()
    return mySocket

if __name__ == '__main__':
    

    dh_p,client_private,client_public=DH_genkeys()
#    print (dh_p,client_private,client_public)

    content_type=20
    message=str(client_public)
    p = pack_TLS(content_type,str(message))
    sock=create_client(str(p))
    
    received_data=recvall(sock)
    server_public=unpack_TLS(bytes(received_data,'utf-8'))
    server_public=int(server_public)
    secret=DH_sharedsecret(dh_p,server_public,client_private)
#    print (secret)
#    secret="message"
    key = hashlib.sha256(str(secret).encode('utf-8')).digest()
#    print (key)
    message="hello"
    p = pack_TLS(content_type,str(message))
    print (p)
    encrypted=AESencrypt(p,key)
    print (encrypted)
#    sock.send(str(encrypted).encode("utf-8"))
    sock.send(str(encrypted).encode('utf-8'))
    print ("Encrypted message Sent to server: ")
    print (str(encrypted).encode('utf-8'))
    sock.close()
#    print (encrypted)
#    decrypted=AESdecrypt(encrypted,key)
#    print (decrypted)
