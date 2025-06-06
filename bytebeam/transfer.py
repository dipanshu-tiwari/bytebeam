import time
import socket
import os

from .utils import recv_exact, validateToken, sendToken
from .const import *

def send_file(server, args):
    logger.info("========== ByteBeam session started (SENDING)==========")
    try:

        # Checking the existence of file
        if os.path.isfile(args.send):
            print(f"[FOUND]: found the file")
            logger.info(f"Found the file: {args.send}")
        else:
            print(f"{RED}[ERROR]: file not found{RESET}")
            logger.error("File not found: %s", args.send)
            return

        # Connecting to server
        ADDR = (args.host, args.port)
        server.connect(ADDR)

        print(f"[CONNECTED]: connected to {args.host}")
        logger.info(f"Connected to reciever: {args.host}")

        # Sender Verification/Authentication
        res = recv_exact(server, 5).decode(FORMAT, errors='replace')
        if res == 'FALSE':
            print(f'{RED}[ERROR]: reciever wasn\'t expecting you{RESET}')
            logger.error("connection blocked from server: reciever was using the IP blocker")
            return

        if not sendToken(server, args):
            print(f"{RED}[ERROR]: incorrect token{RESET}")
            logger.error("incorrect token: %s", args.token)
            return

        # Sending metadata
        file_size = os.path.getsize(args.send)
        file_name = os.path.basename(args.send)

        enc_file_size = str(file_size).encode(FORMAT, errors='replace')
        enc_file_name = file_name.encode(FORMAT, errors='replace')

        enc_file_size_len = str(len(enc_file_size)).encode(FORMAT, errors='replace')
        enc_file_size_len += b' ' * (HEADER - len(enc_file_size_len))

        enc_file_name_len = str(len(enc_file_name)).encode(FORMAT, errors='replace')
        enc_file_name_len += b' ' * (HEADER - len(enc_file_name_len))

        server.send(enc_file_size_len)
        server.send(enc_file_size)
        server.send(enc_file_name_len)
        server.send(enc_file_name)

        print(f"[METADATA SENT]: file name and size have been sent")
        logger.info(f"Metadata of file sent: {file_name}, {file_size}")

        # Waiting for acceptace by user
        print(f"[NOTICE]: waiting for acceptance")
        logger.info(f"Waiting for file to be accepted")
        res = recv_exact(server, 5).decode(FORMAT, errors='replace')
        if res == 'FALSE':
            print(f'{RED}[ERROR]: operation stopped by user{RESET}')
            logger.error("Transfer cancelled by reciever: file rejected")
            return
        print(f"[NOTICE]: file accepted by reciever")
        logger.info("File accepted by reciever")

        flag = recv_exact(server, 5).decode(FORMAT, errors='replace')
        if flag == 'FALSE':
            print(f'{RED}[ERROR]: operation stopped by user (file already existed){RESET}')
            logger.error("Operation stopped by user: file already existed")
            return

        # Sending the file
        print(f"[SENDING]: sending {file_name}")
        logger.info(f"Sending file: {file_name}")

        with open(args.send, 'rb') as file:
            sent = 0
            start_time = time.time()
            for i in range(0, file_size, CHUNK_SIZE):
                msg = file.read(CHUNK_SIZE)
                msg_len = len(msg)
                msg_len_enc = str(msg_len).encode(FORMAT, errors='replace')
                msg_len_enc += b' ' * (CHUNK_LEN - len(msg_len_enc))

                server.send(msg_len_enc)
                server.send(msg)

                sent += msg_len
                elapsed = time.time() - start_time
                speed = sent / 1024 / elapsed if elapsed > 0 else 0

                remaining = file_size - sent
                eta = remaining / (sent / elapsed) if sent > 0 else 0
                eta_min = int(eta // 60)
                eta_sec = int(eta % 60)


                percent = sent / file_size
                filled_len = int(BAR_LENGTH * percent)
                bar = '#' * filled_len + '-' * (BAR_LENGTH - filled_len)
                print(f"\r[SENDING]: |{bar}| {percent * 100:.2f}% @ {speed:.2f} KB/s | ETA: {eta_min:02d}:{eta_sec:02d} ", end='')

        print(f"\n[DONE]: file \'{file_name}\' sent")
        logger.info(f"File sent successfully: {file_name}")

    except (ConnectionRefusedError, ConnectionResetError):
        print(f"\n{RED}[ERROR]: connection failed{RESET}")
        logger.error("Connection failed: %s", args.host)
    except FileNotFoundError:
        print(f"\n{RED}[ERROR]: file not found{RESET}")
        logger.error("File %s not found", args.send)
    except BrokenPipeError:
        print(f"{RED}[ERROR]: reciever crashed or disconnected{RESET}")
        logger.error("Broken pipe error")
    except KeyboardInterrupt:
        print(f"\n{YELLOW}[ABORTED]: Interrupted by user{RESET}")
        logger.error("Interrupted by user")
    except socket.timeout:
        print(f"\n{RED}[TIMEOUT]: connection timed out{RESET}")
        logger.error("Connection timed out")
    except Exception as e:
        print(f"\n{RED}[ERROR]: {e}{RESET}")
        logger.error("Error: %s", e)

def recieve_file(server, args):
    logger.info("========== ByteBeam session started (SENDING)==========")
    try:
        ADDR = (args.host, args.port)

        # Creating the server and connecting to client
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind(ADDR)
        print(f"[STARTED]: started the server")
        logger.info(f"Started the server: {args.host}")
        server.listen()
        print(f"[LISTENING]: listening on {args.host}, {args.port}")
        logger.info(f"Listening: {args.host}, {args.port}")
        conn, addr = server.accept()

        # Sender Verification/Authentication
        if args.from_ip and args.from_ip != addr[0]:
            print(f"[UNAUTHORIZED CONNECTION]: connection blocked from {addr[0]}")
            logger.warning(f"Unauthorized connection blocked: {addr[0]}")
            conn.send('FALSE'.encode(FORMAT, errors='replace'))
            conn.close()
            return
        conn.send('!TRUE'.encode(FORMAT, errors='replace'))
        
        print(f"[CONNECTED]: connected to {addr}")
        logger.info(f"Connected to: {addr}")

        if not validateToken(conn):
            print("[TOKEN AUTH FAILED]: closing connection")
            logger.error("Token auth failed")
            conn.close()
            return

        # Recieving metadata
        file_size_len = recv_exact(conn, HEADER).decode(FORMAT, errors='replace')
        file_size = int(recv_exact(conn, int(file_size_len)).decode(FORMAT, errors='replace'))
        file_name_len = recv_exact(conn, HEADER).decode(FORMAT, errors='replace')
        file_name = recv_exact(conn, int(file_name_len)).decode(FORMAT, errors='replace')
        print(f"[METADATA RECIEVED]: size: {file_size}, name: {file_name}")
        logger.info(f"Metadata of file recieved: {file_name}, {file_size}")

        # Confirmation to recieve the file and overwriting
        if not args.yes:
            print(f"[NOTICE]: do you want to recieve the file \'{file_name}\'? [Y/n]: ", end='')
            perm = input()
            if perm == 'n' or perm == 'N':
                conn.send('FALSE'.encode(FORMAT, errors='replace'))
                conn.close()
                return
        
        conn.send('!TRUE'.encode(FORMAT, errors='replace'))

        if os.path.exists(file_name):
            logger.warning("File already exists")
            if args.no_overwrite:
                print("[NOTICE]: file already existed")
                logger.error("Overwrite dennied: closing")
                conn.send('FALSE'.encode(FORMAT, errors='replace'))
                conn.close()
                return

            if not args.force:
                print(f'[WARNING]: file with name \'{file_name}\' already exist, do you with to overwrite the file? [Y/n]: ', end='')
                perm = input()
                if perm == 'n' or perm == 'N':
                    logger.error("Overwrite dennied: closing")
                    conn.send('FALSE'.encode(FORMAT, errors='replace'))
                    conn.close()
                    return
        logger.warning("Overwrite accepted: overwriting the file")
        conn.send('!TRUE'.encode(FORMAT, errors='replace'))

        # Recieving the file
        with open(file_name, 'wb') as file:
            recvd = 0
            start_time = time.time()
            for i in range(0, file_size, CHUNK_SIZE):
                msg_len = int(recv_exact(conn, CHUNK_LEN))
                msg = recv_exact(conn, msg_len)
                file.write(msg)

                recvd += msg_len
                elapsed = time.time() - start_time
                speed = recvd / 1024 / elapsed if elapsed > 0 else 0

                remaining = file_size - recvd
                eta = remaining / (recvd / elapsed) if recvd > 0 else 0
                eta_min = int(eta // 60)
                eta_sec = int(eta % 60)

                percent = recvd / file_size
                filled_len = int(BAR_LENGTH * percent)
                bar = '#' * filled_len + '-' * (BAR_LENGTH - filled_len)
                print(f"\r[RECIEVING]: |{bar}| {percent * 100:.2f}% @ {speed:.2f} KB/s | ETA: {eta_min:02d}:{eta_sec:02d}", end='')
        
        print(f"\n[DONE]: file \'{file_name}\' recieved")
        logger.info(f"File recieved: {file_name}")
        conn.close()

    except KeyboardInterrupt:
        print(f"\n{YELLOW}[ABORTED]: Interrupted by user{RESET}")
        logger.error("Interrupted by user")
    except socket.timeout:
        print(f"\n{RED}[TIMEOUT]: connection timed out{RESET}")
        logger.error("Connection timed out")
    except Exception as e:
        print(f"\n{RED}[ERROR]: {e}{RESET}")
        logger.error("Error: %s", e)