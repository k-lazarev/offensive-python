import socket as s

target_host = "127.0.0.1"
target_port = 1337

# can listen with nc -ulvnp 1337, but for the 
# sake of demonstration I create a server below:
server = s.socket(s.AF_INET, s.SOCK_DGRAM)
server.bind((target_host, target_port)) 

client = s.socket(s.AF_INET, s.SOCK_DGRAM)

client.sendto("AAABBBCCC".encode(), (target_host, target_port))
client.close()

data, addr = server.recvfrom(4096)

print(data)
