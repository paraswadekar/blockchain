from utils import *
import Crypto
import socket


def create_server():
    host = "127.0.0.1"
    port = 5000
    mySocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    mySocket.bind((host,port))
    mySocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    mySocket.listen(1)
    
    while 1:
        print ("Waiting for connections ...")
        conn, addr = mySocket.accept()
        print ("Connected to client with {} and port {}".format(addr[0],addr[1]))
        received_data=recvall(conn)
        dh_p,server_private,server_public=DH_genkeys()
        client_public=unpack_TLS(bytes(received_data,'utf-8'))
        client_public=int(client_public)
        message=str(server_public)
        content_type=20
        p = pack_TLS(content_type,str(message))
        conn.send(str(p).encode("utf-8"))
        secret=DH_sharedsecret(dh_p,client_public,server_private)
#        print (secret)
        key = hashlib.sha256(str(secret).encode('utf-8')).digest()
#        print (key)
        received_data=recvall(conn)
        print (received_data)
        decrypted=AESdecrypt(bytes(received_data[2:-1],'utf-8'),key)
        print (decrypted)
        message=unpack_TLS(decrypted)
        print (message)
    mySocket.close()
    return 
    


    
    
if __name__ == '__main__':
    create_server()
    (change_cipher_spec, alert, handshake,application_data)=(20,21,22,23)
    protocol_version=(3,3)      # TLS v1.2