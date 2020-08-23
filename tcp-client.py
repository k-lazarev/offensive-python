import socket as s

target_host = "segfault.sh"
target_port = 80

# create socket object
client = s.socket(s.AF_INET, s.SOCK_STREAM)

# connect the client
client.connect((target_host, target_port))

# send GET request
client.send(("GET / HTTP/1.1\r\nHost: segfault.sh\r\n\r\n").encode())

#receive some data back
response = client.recv(4096)

print(response)