#!/usr/bin/env python3
import time
import threading
import resource
import socket
import socketserver
import argparse

BUFFER_SIZE = 1024
TIMEOUT_PERIOD = 0.5
OPEN_FILE_LIMIT = resource.getrlimit(resource.RLIMIT_NOFILE)[1]

tcp_ports_open = []
udp_ports_open = []

resource.setrlimit(resource.RLIMIT_NOFILE, (OPEN_FILE_LIMIT, OPEN_FILE_LIMIT))

parser = argparse.ArgumentParser(description='''Test for open ports.
Might need to run as root for ports below 1024
and upping open file limit with `ulimit` for opening more ports at a time.''')
parser.add_argument('mode', help='server, client')
parser.add_argument('hostname', help='set this to "0" for server to listen on all interfaces')
parser.add_argument('-t', '--tcp', action='store_true', help='TCP only')
parser.add_argument('-u', '--udp', action='store_true', help='UDP only')
parser.add_argument('-sp', '--start-port', dest='sp', type=int, default=1, metavar='port', help='start port')
parser.add_argument('-ep', '--end-port', dest='ep', type=int, default=65535, metavar='port', help='end port')
args = parser.parse_args()

class CustomTCPRequestHandler(socketserver.StreamRequestHandler):
    def handle(self):
        print(self.rfile.readline())
        self.wfile.write(f'hi tcp\n')

class CustomUDPRequestHandler(socketserver.DatagramRequestHandler):
    def handle(self):
        print(self.rfile.read())
        self.wfile.write(b'hi udp\n')

def test_tcp(hostname, port):
    client = socket.socket(type=socket.SOCK_STREAM)
    client.settimeout(TIMEOUT_PERIOD)
    try:
        client.connect((hostname, port))
        client.sendall(f'hello tcp port {port}\n'.encode('ascii'))
        client.close()
        print(f'\nTCP port {port} is open.\n')
        tcp_ports_open.append(port)
    except (ConnectionError, TimeoutError) as e:
        client.close()

def test_udp(hostname, port):
    client = socket.socket(type=socket.SOCK_DGRAM)
    client.settimeout(TIMEOUT_PERIOD)
    try:
        client.sendto(f'hello udp port {port}\n'.encode('ascii'), (hostname, port))
        if client.recv(BUFFER_SIZE):
            print(f'\nUDP port {port} is open.\n')
            udp_ports_open.append(port)
        client.close()
    except (ConnectionError, TimeoutError) as e:
        client.close()

def start_server():
    print('Setting up server ...')
    server_thread_list = []
    skipped_tcp_ports = []
    skipped_udp_ports = []
    for port in range(args.sp, args.ep+1):
        if args.udp:
            break
        try:
            print(f'Setting up server on TCP port {port}/{args.ep} ...', end='\r')
            server = socketserver.TCPServer((args.hostname, port), CustomTCPRequestHandler)
            server.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_thread = threading.Thread(target=server.serve_forever)
            server_thread.daemon = True
            server_thread.start()
            server_thread_list.append(server_thread)
        except OSError as e:
            skipped_tcp_ports.append(port)
    print('\n\nDone setting up TCP ports.\n')
    for port in range(args.sp, args.ep+1):
        if args.tcp:
            break
        try:
            print(f'Setting up server on UDP port {port}/{args.ep} ...', end='\r')
            server = socketserver.UDPServer((args.hostname, port), CustomUDPRequestHandler)
            server.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_thread = threading.Thread(target=server.serve_forever)
            server_thread.daemon = True
            server_thread.start()
            server_thread_list.append(server_thread)
        except OSError as e:
            skipped_udp_ports.append(port)
    print('\n\nDone setting up UDP ports.\n')
    if len(skipped_tcp_ports) != 0 or len(skipped_udp_ports) != 0:
        print(f'Skipped {len(skipped_tcp_ports)} TCP ports and {len(skipped_udp_ports)} UDP ports due to OS errors.')
        print('Try running as root for port number below 1024 and upping open file limit with `ulimit`.')
    print('Done setting up server.')
    server_thread_list[0].join()

def start_client():
    client_thread_list = []
    for port in range(args.sp, args.ep+1):
        if args.udp:
            break
        print(f'Testing TCP port {port}/{args.ep} ...', end='\r')
        client_thread = threading.Thread(target=test_tcp, args=(args.hostname, port))
        client_thread.daemon = True
        client_thread.start()
        client_thread_list.append(client_thread)
    for port in range(args.sp, args.ep+1):
        if args.tcp:
            break
        print(f'Testing UDP port {port}/{args.ep} ...', end='\r')
        client_thread = threading.Thread(target=test_udp, args=(args.hostname, port))
        client_thread.daemon = True
        client_thread.start()
        client_thread_list.append(client_thread)
    for thread in client_thread_list:
        thread.join()
    tcp_ports_open.sort()
    udp_ports_open.sort()
    print('\n-- Summary --')
    print('Opened TCP ports:')
    for port in tcp_ports_open:
        print(port, end=', ')
    print('\nOpened UDP ports:')
    for port in udp_ports_open:
        print(port, end=', ')
    print('')

if args.mode == 'server':
    start_server()
elif args.mode == 'client':
    start_client()
