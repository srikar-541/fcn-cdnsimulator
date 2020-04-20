#!/usr/bin/env python
from socket import *
import requests, os, sys


def create_server():
    global url, port, addr
    server_socket = socket(AF_INET, SOCK_STREAM)
    try:
        server_socket.bind((addr, port))
        server_socket.listen(5)
        while True:
            (client_socket, address) = server_socket.accept()
            rd = client_socket.recv(5000).decode()
            pieces = rd.split("\n")
            p = ''
            if len(pieces) > 0:
                print pieces[0]
                p = pieces[0].split(" ")
            print p[1]
            if p[1] != '/index.html':
                client_socket.send('HTTP/1.1 404 Not Found\n')
            else:
                request = 'http://' + url + '/index.html'
                client_socket.send('HTTP/1.1 200 OK\n')
                client_socket.send('Content-Type: text/html\n')
                client_socket.send('\n')
                if os.path.isfile('cache'):
                    print "in cacheeeee"
                    data = fetch_from_file('cache')
                else:
                    data = fetch_from_origin(request)
                client_socket.sendall(data)
                print "Data sent"
            client_socket.shutdown(SHUT_WR)
    except KeyboardInterrupt:
        print "Shutting down"
    except Exception as e:
        print "Error\n"
        print e
    server_socket.close()


def fetch_from_file(cached_file_path):
    print "file"
    f = open(cached_file_path, "rb")
    data = f.read()
    print data
    return data


def fetch_from_origin(request):
    print "origin"
    response = requests.get(request)
    print "req",request,"res", response
    d = response.__dict__
    response_content = d['_content']
    data = response_content
    f = open('cache', "wb+")
    f.write(data)
    return data

args = sys.argv[1:]
if len(args) != 4 or args[0] != '-p' or args[2] != '-o':
    print "Invalid request"
    sys.exit()

if args[3] != 'cs5700cdnproject.ccs.neu.edu':
    print "Can serve only cs5700cdnproject.ccs.neu.edu"
    sys.exit()

port = int(args[1])

if port < 40000 or port > 65535:
    print "Please enter the port number between 40000 and 65000"
    sys.exit()

url = "3.88.208.124"

addr = 'localhost'

print 'Access http://locahost:' + str(port) + '/index.html'
create_server()
