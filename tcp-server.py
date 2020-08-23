import socket as s
import threading


bind_ip = ""
bind_port = 1337

server = s.socket(s.AF_INET, s.SOCK_STREAM)
server.setsockopt(s.SOL_SOCKET, s.SO_REUSEADDR, 1) 
# the SO_REUSEADDR flag tells the kernel to reuse a local socket 
# in TIME_WAIT state, without waiting for its natural timeout to expire

server.bind((bind_ip, bind_port))

server.listen(5) # maximum backlog of connections

print("[*] Listening on %s:%d" % (bind_ip, bind_port))

# client-handling thread below
def handle_client(client_socket):

    request = client_socket.recv(1024)
    # print out what the client sends
    print("[*] Received %s" % request)

    # send back a packet
    client_socket.send(b"ACK!")
    client_socket.close()

while True:

    client,addr = server.accept() # receive client socket into the client variable,
    # and remote connection details into the addr variable

    print("[*] Accepted connection from: %s:%d" % (addr[0], addr[1]))

    # spawn client thread to handle incoming data
    client_handler = threading.Thread(target=handle_client, args=(client,))
    client_handler.start()
