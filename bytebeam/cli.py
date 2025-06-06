import argparse
import socket
import os
import json

from .const import RED, GREEN, YELLOW, RESET, logger, CONFIG_PATH, VERSION
from .transfer import send_file, recieve_file

def main():
    parser = argparse.ArgumentParser(description="ByteBeam: Terminal File Sharing App")

    parser.add_argument('--version', action='version', version=f'bytebeam {VERSION}')

    parser.add_argument('-s', '--send', type=str, help='Path of file to send')
    parser.add_argument('-r', '--recv', action='store_true', help='Run in receive mode')
    parser.add_argument('-H', '--host', type=str, default=socket.gethostbyname(socket.gethostname()), help='Host/Server IP address')
    parser.add_argument('-p', '--port', type=int, default=5001, help='Port to use')
    parser.add_argument('-t', '--token', type=str, help='Token for authentication on reciever\'s end')
    parser.add_argument('-f', '--from', dest='from_ip', type=str, help='Only recieve from this IP address')

    parser.add_argument('--force', action='store_true', help='Force overwrite when duplicate of file found')
    parser.add_argument('--no-overwrite', action='store_true', help='Never overwite when duplicate of file found')
    parser.add_argument('-y', '--yes', action='store_true', help='Always accept incomming file')

    args = parser.parse_args()

    if args.send and not args.host:
        parser.error("argument -H/--host is required when using -s/--send")

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        if args.force and args.no_overwrite:
            parser.error("Specify either --force or --no-overwrite, not both")

        if args.send and args.recv:
            parser.error("Specify either --send or --recv, not both")
        elif args.send:
            print(f"Sending {args.send} to {args.host}:{args.port}", end='\n\n')
            logger.info(f"Sending {args.send} to {args.host}:{args.port}")
            send_file(server, args)
        elif args.recv:
            print(f"Receiving on {args.host}:{args.port}", end='\n\n')
            logger.info(f"Receiving on {args.host}:{args.port}")
            recieve_file(server, args)
        else:
            parser.error("Specify either --send or --recv")
        
        print(f"{YELLOW}[EXITING]: thanks for using ByteBeam{RESET}")

    except Exception as e:
        print(f"{RED}[FATAL ERROR]: {e}{RESET}")
        logger.error("Fatal error: %s", e)
    finally:
        server.close()
        logger.info("Exiting")

def config():
    parser = argparse.ArgumentParser(description="ByteBeam token configuration")

    parser.add_argument('--version', action='version', version=f'bytebeam-config {VERSION}')

    parser.add_argument('-s', '--set-token', type=str, help='Update or create token')
    parser.add_argument('-e', '--enable-token', action='store_true', help='Enable token usage while receiving files')
    parser.add_argument('-d', '--disable-token', action='store_true', help='Disable token usage while receiving files')

    args = parser.parse_args()

    if args.enable_token and args.disable_token:
        parser.error("Use either --enable-token or --disable-token, not both")

    # Load or create default config
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, 'r') as f:
            config = json.load(f)
    else:
        config = {
            "token": "token",
            "use_token": False
        }

    # Apply changes
    if args.set_token:
        if args.set_token == '!DISCONNECT' or len(args.set_token) == 0:
            parser.error("token can't be empty string or \"!DISCONNECT\"")
            exit()
        config["token"] = args.set_token
        logger.info(f"Auth token updated: {args.set_token}")
    if args.enable_token:
        config["use_token"] = True
        logger.info("Auth token use started")
    if args.disable_token:
        config["use_token"] = False
        logger.info("Auth token use stopped")

    # Save back
    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
    with open(CONFIG_PATH, 'w') as f:
        json.dump(config, f, indent=4)

    print("[CONFIG UPDATED]")
    logger.info("Config file updated")
    print(json.dumps(config, indent=4))
