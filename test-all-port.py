#!/usr/bin/env python3
import time
import threading
import socket
import socketserver
import argparse

BUFFER_SIZE = 1024
TIMEOUT_PERIOD = 0.1

parser = argparse.ArgumentParser(description='''Test for open ports.
Might need to run as root for ports below 1024
and upping open file limit with `ulimit` for opening more than 1024 ports at a time.''')
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


def start_server():
    print('Setting up server ...')
    tcp_servers = []
    udp_servers = []
    skipped_tcp_ports = []
    skipped_udp_ports = []
    for port in range(args.sp, args.ep):
        if args.udp:
            break
        try:
            print(f'Setting up server on TCP port {port}/{args.ep} ...', end='\r')
            server = socketserver.TCPServer((args.hostname, port), CustomTCPRequestHandler)
            server.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_thread = threading.Thread(target=server.serve_forever)
            server_thread.daemon = True
            server_thread.start()
            tcp_servers.append(server_thread)
        except OSError as e:
            skipped_tcp_ports.append(port)
    print('\n\nDone setting up TCP ports.\n')
    for port in range(args.sp, args.ep):
        if args.tcp:
            break
        try:
            print(f'Setting up server on UDP port {port}/{args.ep} ...', end='\r')
            server = socketserver.UDPServer((args.hostname, port), CustomUDPRequestHandler)
            server.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_thread = threading.Thread(target=server.serve_forever)
            server_thread.daemon = True
            server_thread.start()
            udp_servers.append(server_thread)
        except OSError as e:
            skipped_udp_ports.append(port)
    print('\n\nDone setting up UDP ports.\n')
    if len(skipped_tcp_ports) != 0 or len(skipped_udp_ports) != 0:
        print(f'Skipped {len(skipped_tcp_ports)} TCP ports and {len(skipped_udp_ports)} UDP ports due to OS errors.')
        print('Try running as root for port number below 1024 and upping open file limit with `ulimit`.')
    print('Done setting up server.')
    while True:
        time.sleep(1)

def start_client():
    tcp_ports_open = []
    udp_ports_open = []
    for port in range(args.sp, args.ep):
        if args.udp:
            break
        print(f'Testing TCP port {port}/{args.ep} ...', end='\r')
        client = socket.socket(type=socket.SOCK_STREAM)
        client.settimeout(TIMEOUT_PERIOD)
        try:
            client.connect((args.hostname, port))
            client.sendall(f'hello tcp port {port}\n'.encode('ascii'))
            tcp_ports_open.append(port)
            print(f'\nTCP port {port} is open.\n')
        except (ConnectionError, TimeoutError) as e:
            pass
        client.close()
    print('\nDone testing TCP ports.\n\n')
    for port in range(args.sp, args.ep):
        if args.tcp:
            break
        print(f'Testing UDP port {port}/{args.ep} ...', end='\r')
        client = socket.socket(type=socket.SOCK_DGRAM)
        client.settimeout(TIMEOUT_PERIOD)
        try:
            client.sendto(f'hello udp port {port}\n'.encode('ascii'), (args.hostname, port))
            if client.recv(BUFFER_SIZE):
                print(f'\nUDP port {port} is open.\n')
                udp_ports_open.append(port)
        except (ConnectionError, TimeoutError) as e:
            pass
        client.close()
    print('\nDone testing UDP ports.\n\n')
    print('-- Summary --')
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
