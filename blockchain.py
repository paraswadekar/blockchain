import os
import socket
import hashlib
import numpy as np
import time


def create_server(process_id,port_list):
    host = "127.0.0.1"
    port = port_list[process_id]
#    MAX_BUFFER_SIZE=4096     
    mySocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    mySocket.bind((host,port))
    mySocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
     
    print (port)
    mySocket.listen(50)
#    received_data=[]
    while True:
        print ("waiting for connections")
        conn, addr = mySocket.accept()
        ip, port = str(addr[0]), str(addr[1])
        print('Accepting connection from ' + ip + ':' + port)
        
        received_data=recvall(conn).replace('\r\n','')
        if received_data[:2]=='-1':
            transfile='trans_{}.txt'.format(process_id)
            f=open(transfile,'w')
            print (len(received_data))
            print (f.write(received_data))
            f.close()
            print (os.path.getsize(transfile))
            f=open(transfile,'r')
            lines=f.readlines()
            print ("trans lines")
            for line in lines:
                print (line)
            f.close()
        
        print (received_data)
#==============================================================================
#         time.sleep(10)
#==============================================================================
        
#==============================================================================
#         try:
#             conn, addr = mySocket.accept()
#             ip, port = str(addr[0]), str(addr[1])
#             print('Accepting connection from ' + ip + ':' + port)
#             input_from_client_bytes = conn.recv(MAX_BUFFER_SIZE).decode("utf-8").rstrip()
#             print (input_from_client_bytes)
#         except BlockingIOError:
#             pass
#             print ("BlockingIOError occurred")
#==============================================================================
            
    mySocket.close()    
    
    
    return None
    
def recvall(sock):
    data = ""
    while True:
        part = sock.recv(1024).decode('utf-8')
        data += part
        if len(part) < 1024:
            break
    return data    
    
def broadcast(filename,process_id,port_list):
    host = '127.0.0.1'
    for i in range(len(port_list)):
        if i!=process_id:
            print ("Connecting from process {} to process {}".format(str(process_id),str(i)))
            port=port_list[process_id]
            mySocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            mySocket.connect((host,port))
            f=open(filename)
            lines=f.readlines()
            f.close()
            for line in lines:
                mySocket.send(line.encode("utf-8"))
            mySocket.close()
        

    
def create_processes(port_list):
    
    print (port_list)
    for process_id in range(1,len(port_list)):
        pid1=os.fork()
        if pid1==0:
            print ("in child1")
            pid2=os.fork()
            if pid2==0:
                print ("creating server")
                create_server(process_id,port_list)
            else:
                print (pid2)
                time.sleep(1)
                mining(process_id,port_list)
                print ("do other stuff")
        else:
            print ("in parent")
            print (pid1)
    process_id=0
    pid3=os.fork()
    if pid3==0:
        create_server(process_id,port_list)
    else:
        generate_trans(process_id,port_list)
                    
def mining(process_id,port_list):
    while 1:

        blocksfile='blocks_{}.txt'.format(process_id)
        blockdata=np.genfromtxt(blocksfile,delimiter=',',dtype='str').reshape(-1,5)
#==============================================================================
#         print (blockdata)
#==============================================================================
        blockindices=blockdata[:,0].astype(np.int)
        max_index=np.argmax(blockindices)
        prev_line=','.join(list(blockdata[max_index,:]))
        previous_hash=hashlib.sha256(prev_line.encode("utf-8")).hexdigest()
        transfile='trans_{}.txt'.format(process_id)
#        print ("checking trans file size ")
#        print (os.path.getsize(transfile))
        if os.path.getsize(transfile)>11:
            f=open(transfile,'r+')
            lines = f.readlines()
            second_line=lines[1].split(sep=',')
            f.close()
            transaction=int(second_line[1])
#==============================================================================
#             print (transaction)            
#==============================================================================
            blocknumber=int(blockdata[max_index,0])
            timestamp,nonce=generate_block(blocknumber,previous_hash,transaction)
            if nonce>0:
                found=0
                f=open(transfile,'r+')
                lines1 = f.readlines()
                f.close()
                for line in lines1:
                    if line.find(str(transaction))>=0:
                        found=1
                        break
                if found==1:
                    print ("deleting {}".format(transaction))
                    delete_trans(transaction,process_id)
                    f=open(blocksfile,'a')
                    blocknumber+=1
                    f.write('{},{},{},{},{}\n'.format(str(blocknumber),str(previous_hash),str(timestamp),str(nonce),str(transaction)))
                    f.close()
                
                    
def generate_trans(process_id,port_list):  
    transaction=1000000
    filename='trans_0.txt'
    while 1:
        time.sleep(0.1)
        if os.path.getsize(filename)<50:
            transaction+=1
            
            f=open(filename,'a')
            f.write('-1,{}\n'.format(str(transaction)))
            f.close()
            broadcast(filename,process_id,port_list)

    
    
def delete_trans(transaction,process_id):
    transaction=str(transaction)
    filename='trans_{}.txt'.format(process_id)
    f=open(filename,'r+')
    lines = f.readlines()
    f.seek(0)
    for line in lines:
        if line.find(transaction)<0:
#==============================================================================
#             print (line)
#==============================================================================
            f.write(line)
    f.truncate()
    f.close()
                
def generate_block(blocknumber,previous_hash,transaction):
    difficulty=2
    delay=0.1
    nonce=1
    timestamp=int(time.time())
    for i in range(100):
        time.sleep(delay)
        message='{},{},{},{},{}'.format(str(blocknumber),str(previous_hash),str(timestamp),str(nonce),str(transaction))
        m = hashlib.sha256(message.encode("utf-8"))
        m_int=int(m.hexdigest(),16)
        if 256-m_int.bit_length()>=difficulty:
            print (m.hexdigest())
            return timestamp,nonce
        nonce+=1
        
    nonce=-1
    return timestamp,nonce
    
def initialization():
    port_list=list(range(5000,5002))
    empty_hash=hashlib.sha256().hexdigest()
    t=int(time.time())
    transaction=1000000
    t,nonce=generate_block(0,empty_hash,transaction)
    for i in range(len(port_list)):
        blocksfile = open('blocks_{}.txt'.format(i),'w') 
        blocksfile.write('0,{},{},{},{}\n'.format(str(empty_hash),str(t),str(nonce),str(transaction)))
        blocksfile.close()
        transfile= open('trans_{}.txt'.format(i),'w') 
        transfile.write('-1,{}\n'.format(str(transaction)))
        transfile.close()
    return port_list
        
    
if __name__ == '__main__':
    

    port_list=initialization()
    create_processes(port_list)