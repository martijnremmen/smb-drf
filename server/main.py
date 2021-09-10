#!/usr/bin/env python3
import socket
import logging
import random

HOST = '127.0.0.1'
PORT = 6969

logging.basicConfig(level=logging.DEBUG)


def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        s.listen(2)
        logging.info(f"listening on {s.getsockname()[0]}:{s.getsockname()[1]}")
    
        while True:
            con, addr = s.accept()
            with con as c:
                handle_client(c, addr)


def handle_client(c: socket.socket, addr):
    logging.info(f"Client {addr[0]}:{addr[1]} connected")

    while True:
        r = c.recv(4096)
        read_packet(r)
        if not r:
            break
        c.send(send_update())

    c.close()
    logging.info(f"Client {addr[0]}:{addr[1]} disconnected")


def read_packet(raw_input: bytes) -> dict:
    logging.debug("received packet:")
    logging.debug(raw_input.hex())

    output =  dict(
        score = raw_input[0:12]
    )
    logging.debug(output)

    return output


def send_update() -> bytes:
    dpad = random.randint(1, 4)
    controls = dict(
        left = dpad == 1,
        right = dpad == 2,
        up = dpad == 3,
        down = dpad == 4,
        a = bool(random.getrandbits(1)),
        b = bool(random.getrandbits(1))
    )

    str_packet = ''.join([str(int(v)) for v in controls.values()])
    byte_packet = str_packet.encode()
    return byte_packet

if __name__ == "__main__":
    main()