#!/usr/bin/env python3
import time
import threading
import resource
import socket
import argparse

BUFFER_SIZE = 1024
TIMEOUT_PERIOD = 0.5
MESSAGE_LENGTH_FIELD_LENGTH = 2
OPEN_FILE_LIMIT = resource.getrlimit(resource.RLIMIT_NOFILE)[1]

ports_open = {'tcp': [], 'udp': []}
ports_error = {'tcp': [], 'udp': []}

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

def get_socket_protocol_name(sock_type):
    if sock_type == socket.SOCK_STREAM:
        return 'TCP'
    elif sock_type == socket.SOCK_DGRAM:
        return 'UDP'
    elif sock_type == socket.SOCK_RAW:
        return 'RAW'
    else:
        return 'UNK'

def get_formatted_message(socket_type, sender_address, receiver_address, message, codec='utf-8'):
        notification = f'\n* A {len(message)}-bytes {get_socket_protocol_name(socket_type)} '
        notification += f'message from {sender_address} at {receiver_address}:'
        notification += '\n-- MESSAGE START --\n'
        notification += str(message) if codec == 'raw' else str(message, codec)
        notification += '\n-- MESSAGE END --\n'
        return notification

def run_server(hostname, port, socket_type):
    
    sock = socket.socket(type=socket_type)
    sock_empty = socket.socket(type=socket_type)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        sock.bind((hostname, port))
    except (PermissionError, OSError) as e:
        sock.close()
        ports_error[get_socket_protocol_name(socket_type).lower()].append(port)
        return
    if socket_type == socket.SOCK_STREAM:
        sock.listen()
    while True:
        response = bytes(f'hi {get_socket_protocol_name(socket_type)} socket\n',
                        'utf-8')
        data = b''
        if socket_type == socket.SOCK_STREAM:
            client_socket, client_address = sock.accept()
            message_length = int.from_bytes(
                                        client_socket.recv(MESSAGE_LENGTH_FIELD_LENGTH),
                                        'big')
            client_socket.send(message_length.to_bytes(MESSAGE_LENGTH_FIELD_LENGTH, 'big'))
        else:
            client_socket = sock
            message_length_raw, client_address = client_socket.recvfrom(MESSAGE_LENGTH_FIELD_LENGTH)
            message_length = int.from_bytes(message_length_raw, 'big')
            sock_empty.sendto(message_length.to_bytes(MESSAGE_LENGTH_FIELD_LENGTH, 'big'),
                client_address)
        while message_length > 0:
            chunk = client_socket.recv(min(message_length, BUFFER_SIZE))
            data += chunk
            message_length -= len(chunk)
        print(get_formatted_message(socket_type,
                                    client_address, client_socket.getsockname(),
                                    data))
        if socket_type == socket.SOCK_STREAM:
            client_socket.send(len(response).to_bytes(MESSAGE_LENGTH_FIELD_LENGTH, 'big'))
        else:
            sock_empty.sendto(len(response).to_bytes(MESSAGE_LENGTH_FIELD_LENGTH, 'big'),
                client_address)
        while len(response) > 0:
            if socket_type == socket.SOCK_STREAM:
                response = response[client_socket.send(response):]
            else:
                response = response[sock_empty.sendto(response, client_address):]
        if socket_type == socket.SOCK_STREAM:
            client_socket.close()

def send_test(hostname, port, socket_type):
    target_address = (hostname, port)
    sock = socket.socket(type=socket_type)
    sock.settimeout(TIMEOUT_PERIOD)
    message = bytes(f'hello {get_socket_protocol_name(socket_type)} port {port}\n', 'utf-8')
    data = b''
    try:
        if socket_type == socket.SOCK_STREAM:
            sock.connect((hostname, port))
            start_timer = time.perf_counter()
            sock.send(len(message).to_bytes(MESSAGE_LENGTH_FIELD_LENGTH, 'big'))
        else:
            start_timer = time.perf_counter()
            sock.sendto(len(message).to_bytes(MESSAGE_LENGTH_FIELD_LENGTH, 'big'),
                target_address)
        sock.recv(MESSAGE_LENGTH_FIELD_LENGTH)
        end_timer = time.perf_counter()
        while len(message) > 0:
            if socket_type == socket.SOCK_STREAM:
                message = message[sock.send(message):]
            else:
                message = message[sock.sendto(message, target_address):]
        response_length = int.from_bytes(
                                        sock.recv(MESSAGE_LENGTH_FIELD_LENGTH),
                                        'big')
        while response_length > 0:
            chunk = sock.recv(min(response_length, BUFFER_SIZE))
            data += chunk
            response_length -= len(chunk)
        if socket_type == socket.SOCK_STREAM:
            peer_name = sock.getpeername()
        else:
            peer_name = target_address
        print(get_formatted_message(socket_type,
                                    peer_name, sock.getsockname(),
                                    data))
        print(f'RTT latency = {(end_timer - start_timer)*1000} ms.')
        if len(data) > 0:
            ports_open[get_socket_protocol_name(socket_type).lower()].append(port)
    except (ConnectionError, TimeoutError, OSError) as e:
        sock.close()

def start_server():
    print('Setting up server ...')
    server_thread_list = []
    skipped_tcp_ports = []
    skipped_udp_ports = []
    for port in range(args.sp, args.ep+1):
        if args.udp:
            break
        print(f'Setting up server on TCP port {port}/{args.ep} ...', end='\r')
        server_thread = threading.Thread(target=run_server, args=(
            args.hostname, port, socket.SOCK_STREAM))
        server_thread.daemon = True
        server_thread.start()
        server_thread_list.append(server_thread)
    print('\n\nDone setting up TCP ports.\n')
    for port in range(args.sp, args.ep+1):
        if args.tcp:
            break
        print(f'Setting up server on UDP port {port}/{args.ep} ...', end='\r')
        server_thread = threading.Thread(target=run_server, args=(
            args.hostname, port, socket.SOCK_DGRAM))
        server_thread.daemon = True
        server_thread.start()
        server_thread_list.append(server_thread)
    print('\n\nDone setting up UDP ports.\n')
    if len(ports_error["tcp"]) != 0 or len(ports_error["udp"]) != 0:
        print(f'Skipped {len(ports_error["tcp"])} TCP ports ' +
              f'and {len(ports_error["udp"])} UDP ports due to OS errors.')
        print('Try running as root for port number below 1024 ' +
              'and upping open file limit with `ulimit`.')
    print('Done setting up server.')
    while True:
        time.sleep(1)

def start_client():
    client_thread_list = []
    print('Running test ...')
    for port in range(args.sp, args.ep+1):
        if args.udp:
            break
        client_thread = threading.Thread(target=send_test, args=(
                                        args.hostname, port, socket.SOCK_STREAM))
        client_thread.daemon = True
        client_thread.start()
        client_thread_list.append(client_thread)
    for port in range(args.sp, args.ep+1):
        if args.tcp:
            break
        client_thread = threading.Thread(target=send_test, args=(
                                        args.hostname, port, socket.SOCK_DGRAM))
        client_thread.daemon = True
        client_thread.start()
        client_thread_list.append(client_thread)
    for thread in client_thread_list:
        thread.join()
    ports_open['tcp'].sort()
    ports_open['udp'].sort()
    print('\n-- Summary --')
    print('Opened TCP ports:')
    for port in ports_open['tcp']:
        print(port, end=', ')
    print('\nOpened UDP ports:')
    for port in ports_open['udp']:
        print(port, end=', ')
    print('')

if __name__ == "__main__":
    if args.mode == 'server':
        start_server()
    elif args.mode == 'client':
        start_client()
