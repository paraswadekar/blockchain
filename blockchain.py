import os
import socket
import hashlib
import numpy as np
import time


def create_server(process_id,port_list):
    host = "127.0.0.1"
    port = port_list[process_id]
    mySocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    mySocket.bind((host,port))
    mySocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    mySocket.listen(50)
    while True:
        conn, addr = mySocket.accept()
        
        received_data=recvall(conn)
        if received_data[:2]=='-1':
            valid_array=check_validity_trans(received_data,process_id)
            transfile='trans_{}.txt'.format(process_id)
            f=open(transfile,'a')            
            f.write(valid_array)
            f.close()
            delete_emptylines(transfile)
        else:
            valid=verify_blockchain(received_data,process_id)
            if valid==1:
                blocksfile='blocks_{}.txt'.format(process_id)
                f=open(blocksfile,'w')
                f.write(received_data)
                f.close()            
    mySocket.close()


def verify_blockchain(data,process_id):
    data_array=np.array([[j for j in i.split(',')] for i in data.splitlines()])
    data_array=data_array[np.argsort(data_array[:,0].astype(np.int))]
    good=1
    for i in range(1,data_array.shape[0]):                
        message=','.join(data_array[i-1,:])
        if data_array[i,1]==hashlib.sha256(message.encode("utf-8")).hexdigest() and check_difficulty(message)==True:
            pass
        else:
            good=0
            break
    if good==1:
        num_blocks = sum(1 for line in open('blocks_{}.txt'.format(process_id)))
        if num_blocks-1<data_array.shape[0]:
            for j in range(1,data_array.shape[0]):
                delete_trans(data_array[j,-1],process_id)
            return 1
        else:
            print ("Proces {} already has {} blocks, rejecting set of {} blocks".format(process_id,num_blocks,data_array.shape[0]))
    return 0
                        

def check_difficulty(message):
    difficulty=5
    m = hashlib.sha256(message.encode("utf-8"))
    m_int=int(m.hexdigest(),16)
    if 256-m_int.bit_length()>=difficulty:
        return True
    else:
        return False    


def check_validity_trans(data,process_id):
    data_array=np.array([[j for j in i.split(',')] for i in data.splitlines()])
    data_array=data_array.reshape(-1,2)
    trans_check=data_array[:,-1]
    blocksfile='blocks_{}.txt'.format(process_id)
    blockdata=np.genfromtxt(blocksfile,delimiter=',',dtype='str').reshape(-1,5)
    transfile='trans_{}.txt'.format(process_id)
    transdata=np.genfromtxt(transfile,delimiter=',',dtype='str').reshape(-1,2)
    trans_available=np.append(blockdata[:,-1],transdata[:,-1])
    trans_remove=np.intersect1d(trans_check,trans_available)
    for i in range(trans_remove.shape[0]):
        data_array=data_array[data_array[:,-1]!=trans_remove[i]]
    valid_array='\n'.join([','.join(row) for row in data_array])
    return valid_array+'\n'
        

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
            port=port_list[i]
            mySocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            mySocket.connect((host,port))
            f=open(filename)
            lines=f.readlines()
            f.close()
            for line in lines:
                mySocket.send(line.encode("utf-8"))
            mySocket.close()
        
    
def create_processes(port_list):
    for process_id in range(1,len(port_list)):
        pid1=os.fork()
        if pid1==0:
            pid2=os.fork()
            if pid2==0:
                create_server(process_id,port_list)
            else:
                time.sleep(1)
                mining(process_id,port_list)
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
        blockindices=blockdata[:,0].astype(np.int)
        max_index=np.argmax(blockindices)
        prev_line=','.join(list(blockdata[max_index,:]))
        previous_hash=hashlib.sha256(prev_line.encode("utf-8")).hexdigest()
        transfile='trans_{}.txt'.format(process_id)
        if os.path.getsize(transfile)>11:
            wait=0
            f=open(transfile,'r+')
            lines = f.readlines()
            second_line=lines[1].split(sep=',')
            f.close()
            transaction=int(second_line[1])
            blocknumber=int(blockdata[max_index,0])+1
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
                    delete_trans(transaction,process_id)
                    f=open(blocksfile,'a')
                    f.write('{},{},{},{},{}\n'.format(str(blocknumber),str(previous_hash),str(timestamp),str(nonce),str(transaction)))
                    f.close()
                    broadcast(blocksfile,process_id,port_list)
                    print ("Process {} got transaction {}".format(str(process_id),str(transaction)))
        else:
            wait+=1
            time.sleep(1)
            if wait>10:
                broadcast(blocksfile,process_id,port_list)
                
                    
def generate_trans(process_id,port_list):  
    transaction=1000000
    filename='trans_0.txt'
    while 1:
        time.sleep(0.1)
        if os.path.getsize(filename)<150:
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
            f.write(line)
    f.truncate()
    f.close()
    

def delete_emptylines(filename):
    f=open(filename,'r+')
    lines = f.readlines()
    f.seek(0)
    for line in lines:
        if line!='\n':
            f.write(line)
    f.truncate()
    f.close()
            

def generate_block(blocknumber,previous_hash,transaction):
    delay=0.1
    nonce=np.random.randint(0,1024)
    timestamp=int(time.time())
    for i in range(10000):
        time.sleep(delay)
        message='{},{},{},{},{}'.format(str(blocknumber),str(previous_hash),str(timestamp),str(nonce),str(transaction))
        if check_difficulty(message)==True:
            return timestamp,nonce
        nonce+=1
        
    nonce=-1
    return timestamp,nonce
    

def initialization():
    port_list=list(range(5000,5006))
    empty_hash=hashlib.sha256().hexdigest()
    transaction=1000000
    timestamp,nonce=generate_block(0,empty_hash,transaction)
    for i in range(len(port_list)):
        blocksfile = open('blocks_{}.txt'.format(i),'w') 
        blocksfile.write('0,{},{},{},{}\n'.format(str(empty_hash),str(timestamp),str(nonce),str(transaction)))
        blocksfile.close()
        transfile= open('trans_{}.txt'.format(i),'w') 
        transfile.write('-1,{}\n'.format(str(transaction)))
        transfile.close()
    return port_list
        
    
if __name__ == '__main__':
    port_list=initialization()
    create_processes(port_list)
