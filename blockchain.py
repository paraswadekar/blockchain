import os
import socket
import hashlib
import numpy as np
import time


def create_server(process_id,port_array):
    host = "127.0.0.1"
    port = port_list[process_id]
    MAX_BUFFER_SIZE=4096     
    mySocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    mySocket.bind((host,port))
#    mySocket.setblocking(0)
    mySocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
     
    print (port)
    mySocket.listen(5)
    
    while True:
        print ("waiting for connections")
        try:
            conn, addr = mySocket.accept()
            ip, port = str(addr[0]), str(addr[1])
            print('Accepting connection from ' + ip + ':' + port)
            input_from_client_bytes = conn.recv(MAX_BUFFER_SIZE).decode("utf-8").rstrip()
            print (input_from_client_bytes)
        except BlockingIOError:
            pass
            print ("BlockingIOError occurred")
            
        #do something here
    mySocket.close()    
    
    
#    print ("socket listening")
#    
#    conn, client_addr = mySocket.accept()
#    print ("still listening")
    return mySocket, conn, client_addr
    
def create_client(port,message):
    host = '127.0.0.1'
    
    mySocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    mySocket.connect((host,port))
    mySocket.send(message.encode("utf-8"))
    mySocket.close()
    return None    
    
def broadcast(message,process_id,port_list):
    host = '127.0.0.1'
    for i in range(5):
        if i!=process_id:
            
            mySocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            mySocket.connect((host,port))
            mySocket.send(message.encode("utf-8"))
            mySocket.close()
        

#==============================================================================
# def create_connections(self_port, port_array):
#     for port in port_array:
#         if port<self_port:
#             create_server(self_port,port)
#         elif port>self_port:
#             create_client(self_port,port)
#             
#==============================================================================
    pass

def create_processes():
    port_list=list(range(5000,5005))
    port_list=list(range(6000,6005))
    
    print (port_list)
    for process_id in range(5):
        pid1=os.fork()
        if pid1==0:
            print ("in child1")
            pid=os.fork()
            if pid==0:
                print ("creating server")
                create_server(process_id,port_list)
            else:
                print (pid)
                time.sleep(1)
#                create_client(process_id,port_list)
                print ("do other stuff")
        else:
            print ("in parent")
            print (pid1)
    
                
def generate_block(previous_hash,transaction):
    difficulty=2
    delay=0.1
    blocksize=5
    nonce=1
    while 1:
        t=int(time.time())
        for i in range(100):
            time.sleep(delay)
            m = hashlib.sha256(str(blocksize).encode("utf-8"))
            m.update(str(t).encode("utf-8"))
            m.update(str(previous_hash).encode("utf-8"))
            nonce+=1
            m.update(str(nonce).encode("utf-8"))
            m.update(str(transaction).encode("utf-8"))
            m_int=int(m.hexdigest(),16)
            if 256-m_int.bit_length()>=difficulty:
                print (m.hexdigest())
                return t,nonce
    
def initialization():
    empty_hash=hashlib.sha256().hexdigest()
    t=int(time.time())
    transaction=1000000
    t,nonce=generate_block(empty_hash,transaction)
    for i in range(5):
        blocksfile = open('blocks_{}.txt'.format(i),'w') 
        blocksfile.write('0,{},{},{},{}'.format(str(empty_hash),str(t),str(nonce),str(transaction)))
        transfile= open('trans_{}.txt'.format(i),'w') 
        transfile.write('-1,{}'.format(str(transaction)))
    
if __name__ == '__main__':
    
#    for i in range(10):
    initialization()
#    empty_hash=hashlib.sha256().hexdigest()
    
#    generate_block(empty_hash)
#    create_processes()