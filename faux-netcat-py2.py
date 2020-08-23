#!/usr/bin/python

import sys
import socket
import getopt
import threading
import subprocess

# define global variables
listen = False
command = False
upload = False
execute = ""
target = ""
upload_destination = ""
port = 0


def usage():
    print(" ___                        ___ ___  __       ___ ")
    print("|__   /\  |  | \_/    |\ | |__   |  /  `  /\   |  ")
    print("|    /~~\ \__/ / \    | \| |___  |  \__, /~~\  |  ")
    print("\nFaux Netcat v. 0.1\n")
    print("Usage: faux-netcat.py -t target_host -p port\n")
    print("-l --listen                  - listen on [host]:[port] for incoming connections")
    print("-e --execute=file_to_run     - execute the file upon receiving a connection")
    print("-c --command                 - initialize a command shell")
    print("-u --upload=destination      - upon receiving a connection upload a file and write to [destination]\n")
    print("Examples:\n")
    print("faux-netcat.py -t 192.168.0.1 -p 1337 -l -c")
    print("faux-netcat.py -t 192.168.0.1 -p 1337 -l -u=C:\\target.exe")
    print("faux-netcat.py -t 192.168.0.1 -p 1337 -l -e=\"cat /etc/passwd\"")
    print("echo 'ABCDEFG' | ./faux-netcat.py -t 192.168.0.1 -p 1337")
    sys.exit(0)


def main():
    global listen
    global command
    global execute
    global target
    global upload_destination
    global port

    if not len(sys.argv[1:]):
        usage()

    # read cli options and set the necessary variables depending on the options
    # if any cli parameters don't match criteria, print usage info
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hle:t:p:cu:", ["help", "listen", "execute", "target", "port", "command", "upload"])
    except getopt.GetoptError as err:
        print(str(err))
        usage()

    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
        elif o in ("-l", "--listen"):
            listen = True
        elif o in ("-e", "--execute"):
            execute = a
        elif o in ("-c --command"):
            command = True
        elif o in ("-u", "--upload"):
            upload_destination = a
        elif o in ("-t", "--target"):
            target = a
        elif o in ("-p", "--port"):
            port = int(a)
        else:
            assert False, "Unhandled Option"

        # are we going to listen, or just send data from stdin?
    if not listen and len(target) and port > 0:  # mimic netcat

        # if planning on sending data interactively,
        # send CTRL-D to bypass stdin read
        buffer = sys.stdin.read()

        # send data off
        client_sender(buffer)

    if listen:
        server_loop()  # detect if we are to set up a listening socket,
                       # and process further commands


def client_sender(buffer):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        # connect to the target host
        client.connect((target, port))

        if len(buffer):  # test if we received any input from stdin
            client.send(buffer)

        while True:

            # wait for data back
            recv_len = 1
            response = ""

            while recv_len:

                data = client.recv(4096)
                recv_len = len(data)
                response += data

                if recv_len < 4096:
                    break

            print(response)

            # wait for more input
            buffer = raw_input("")
            buffer += "\n"

            # send it off
            client.send(buffer)

    except:

        print("[x] Exception! Exiting.")

        # close the conection
        client.close()


def server_loop():
    global target

    # if no target is defined, listen on all interfaces
    if not len(target):
        target = "0.0.0.0"

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((target, port))
    server.listen(5)

    while True:
        client_socket, addr = server.accept()

        # spin off a thread to handle a new client
        client_thread = threading.Thread(target=client_handler, args=(client_socket,))
        client_thread.start()


def run_command(command):
    # trim the new line
    command = command.rstrip()

    # run the command and get the output back
    try:
        output = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)
    except:
        output = "Failed to execute the command.\r\n"

    # send output back to the client
    return output


def client_handler(client_socket):
    global upload
    global execute
    global command

    # check for upload
    if len(upload_destination):

        # read in all of the bytes and write to destination
        file_buffer = ""

        # keep reading until none is available
        while True:
            data = client_socket.recv(1024)

            if not data:
                break
            else:
                file_buffer += data

            # now take these bytes and try to write them out
        try:
            file_descriptor = open(upload_destination, "wb")
            file_descriptor.write(file_buffer)
            file_descriptor.close()

                # ack that the file was written
            client_socket.send("Successfully saved file to %s\r\n" % upload_destination)
        except:
            client_socket.send("Failed to save file to %s\r\n" % upload_destination)

    if len(execute):
        # run the command
        output = run_command(execute)

        client_socket.send(output)

    # go into another loop if a command was requested
    if command:

        while True:
            # show simple prompt
            client_socket.send("FxNC:$\r\r\r")

            # receive until there's a linefeed (enter key)
            cmd_buffer = ""

            while "\n" not in cmd_buffer:
                cmd_buffer += client_socket.recv(8192)

            # send back the command output
            response = run_command(cmd_buffer)

            # send back the response
            client_socket.send(response)

main()
