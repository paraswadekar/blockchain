from struct import *
from Crypto.Random.random import randint
from Crypto import Random
from Crypto.Cipher import AES
import base64
import hashlib

def recvall(sock):
    data = ""
    while 1:
        part = sock.recv(4096).decode('utf-8')
        data += part
        if len(part) < 4096:
            break
    return data 
        
def construct_packet(payload):
    fmt="%ds"%len(payload)
    padding_size=calc_padding_size(fmt)
    packet_length=calcsize(fmt)+padding_size+1
    random_padding=bytes('a'*padding_size,'ascii')
    fs="%ds"%padding_size
    fmt="!IB"+fmt+fs
    packet=pack(fmt,packet_length,padding_size,payload,random_padding)#,bytes("none",'ascii'))
    return packet

def create_namelist(namelist):
    l=len(namelist)
    p=pack("!I%ds" % (l,), l, bytes(namelist,'ascii'))
    return p

def add_to_payload(payload,data):
    fmt="%ds%ds"%(len(payload),len(data))
    payload=pack(fmt,payload,data)
    return payload    
    
def pack_TLS(content_type,message):
    block_size=32
    length=len(message)
    padding_size=block_size-(length+4)%block_size
    padding=bytes('a'*padding_size,'ascii')
    fmt="!4s{}s{}s".format(length,padding_size)
    p=pack(fmt,bytes("{0:0{1}x}".format(length,4),'utf-8'),bytes(message,'utf-8'),padding)
    return p
    
def unpack_TLS(buffer):
    block_size=32
    fmt="!1s"
#==============================================================================
#     (check,)=unpack_from(fmt,buffer)
#     print (check)
#     if check=="b":
#         (check,)=unpack_from(fmt,buffer,offset=2)
#         if check=='b':
#             (length)=unpack_from("!4s",buffer,offset=4)
#         else:
#             (length)=unpack_from("!4s",buffer,offset=2)
#     else:
#         (length)=unpack_from("!4s",buffer,offset=0)
#==============================================================================
    (garbage,length)=unpack_from("!2s4s",buffer)
    print (length)
    print (garbage[0])
    if (garbage[0]!=ord('b')):
        length=garbage+length[:2]
        offset=4
    else:
        offset=6
    length=int(length,16)
    padding_size=block_size-(length+4)%block_size
    fmt="{}s{}s".format(length,padding_size)
    (message,padding)=unpack_from(fmt,buffer,offset=offset)
    return message.decode('utf-8')
    
def DH_genkeys():
    p=int('0xFFFFFFFFFFFFFFFFC90FDAA22168C234C4C6628B80DC1CD129024E088A67'
            'CC74020BBEA63B139B22514A08798E3404DDEF9519B3CD3A431B302B0A6DF2'
            '5F14374FE1356D6D51C245E485B576625E7EC6F44C42E9A637ED6B0BFF5CB6'
            'F406B7EDEE386BFB5A899FA5AE9F24117C4B1FE649286651ECE45B3DC2007C'
            'B8A163BF0598DA48361C55D39A69163FA8FD24CF5F83655D23DCA3AD961C62'
            'F356208552BB9ED529077096966D670C354E4ABC9804F1746C08CA18217C32'
            '905E462E36CE3BE39E772C180E86039B2783A2EC07A28FB5C55DF06F4C52C9'
            'DE2BCBF6955817183995497CEA956AE515D2261898FA051015728E5A8AAAC4'
            '2DAD33170D04507A33A85521ABDF1CBA64ECFB850458DBEF0A8AEA71575D06'
            '0C7DB3970F85A6E1E4C7ABF5AE8CDB0933D71E8C94E04A25619DCEE3D2261A'
            'D2EE6BF12FFA06D98A0864D87602733EC86A64521F2B18177B200CBBE11757'
            '7A615D6C770988C0BAD946E208E24FA074E5AB3143DB5BFCE0FD108E4B82D1'
            '20A92108011A723C12A787E6D788719A10BDBA5B2699C327186AF4E23C1A94'
            '6834B6150BDA2583E9CA2AD44CE8DBBBC2DB04DE8EF92E8EFC141FBECAA628'
            '7C59474E6BC05D99B2964FA090C3A2233BA186515BE7ED1F612970CEE2D7AF'
            'B81BDD762170481CD0069127D5B05AA993B4EA988D8FDDC186FFB7DC90A6C0'
            '8F4DF435C93402849236C3FAB4D27C7026C1D4DCB2602646DEC9751E763DBA'
            '37BDF8FF9406AD9E530EE5DB382F413001AEB06A53ED9027D831179727B086'
            '5A8918DA3EDBEBCF9B14ED44CE6CBACED4BB1BDB7F1447E6CC254B33205151'
            '2BD7AF426FB8F401378CD2BF5983CA01C64B92ECF032EA15D1721D03F482D7'
            'CE6E74FEF6D55E702F46980C82B5A84031900B1C9E59E7C97FBEC7E8F323A9'
            '7A7E36CC88BE0F1D45B7FF585AC54BD407B22B4154AACC8F6D7EBF48E1D814'
            'CC5ED20F8037E0A79715EEF29BE32806A1D58BB7C5DA76F550AA3D8A1FBFF0'
            'EB19CCB1A313D55CDA56C9EC2EF29632387FE8D76E3C0468043E8F663F4860'
            'EE12BF2D5B0B7474D6E694F91E6DCC4024FFFFFFFFFFFFFFFF', 16)
    g=2
#    print (p.bit_length())
    private_key=randint(1,p-1)
    public_key=pow(g,private_key,p)
    return p,private_key,public_key
    
def DH_sharedsecret(p,public_key,private_key):
    secret=pow(public_key,private_key,p)
    return secret
    
def AESencrypt(message,key):
    iv = Random.new().read(AES.block_size)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    encrypted=base64.b64encode(iv + cipher.encrypt(message))
    return encrypted
    
def AESdecrypt(encrypted,key):
    encrypted = base64.b64decode(encrypted)
    iv = encrypted[:16]
    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted=cipher.decrypt(encrypted[16:])
    return decrypted