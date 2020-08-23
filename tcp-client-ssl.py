import socket as s
import ssl

target_host = "segfault.sh"
target_port = 443

ssl_context = ssl.create_default_context()

with s.create_connection((target_host, target_port)) as sock:
    with ssl_context.wrap_socket(sock, server_hostname=target_host) as sslsock:
        sslsock.send(("GET / HTTP/1.1\r\nHost: segfault.sh\r\n\r\n").encode())
        print(sslsock.version())
        response = sslsock.recv(4096)
        print(response)