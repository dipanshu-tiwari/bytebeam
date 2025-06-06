import json

from .const import *

def recv_exact(conn, lenght):
    data = b''
    while len(data) < lenght:
        packet = conn.recv(lenght - len(data))
        data += packet
    return data

def validateToken(conn):
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, 'r') as f:
            config = json.load(f)
            use_token = config['use_token']
    else:
        use_token = False
    
    if use_token:
        conn.send('!TRUE'.encode(FORMAT, errors='replace'))
        token_len = int(recv_exact(conn, HEADER).decode(FORMAT, errors='replace'))
        token = recv_exact(conn, token_len).decode(FORMAT, errors='replace')
        if token == '!DISCONNECT':
            auth = False
        elif token == config['token']:
            auth = True
        else:
            auth = False
    else:
        conn.send('FALSE'.encode(FORMAT, errors='replace'))
        auth = True
    if auth:
        conn.send('!TRUE'.encode(FORMAT, errors='replace'))
    else:
        conn.send('FALSE'.encode(FORMAT, errors='replace'))
    return auth

def sendToken(server, args):
    need_token = recv_exact(server, 5).decode(FORMAT, errors='replace')
    if need_token == '!TRUE':
        if args.token == None:
            args.token = ''
            while len(args.token) == 0:
                print(f"[WARNING]: Token is required by the reciever, enter the token: ", end='')
                args.token = input()
        token_len = str(len(args.token)).encode(FORMAT, errors='replace')
        token_len += b' ' * (HEADER - len(token_len))
        server.send(token_len)
        server.send(str(args.token).encode(FORMAT, errors='replace'))
    auth = recv_exact(server, 5).decode(FORMAT, errors='replace')
    if auth == 'FALSE':
        return False
    return True