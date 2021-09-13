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

    output =  dict(
        score = bcd_toint(raw_input[0:6]),
        time = bcd_toint(raw_input[6:9]),
        xpos = bcd_toint(raw_input[9:10]),
        dead = raw_input[10:11]
    )
    logging.debug(raw_input[12:18])
    logging.debug(raw_input)
    logging.debug(output)

    return output


def bcd_toint(b: list[int]) -> int:
    """
    converts a list containing a BCD formatted decimal 
    number to an integer.
    [ 1, 2, 2] --> 122
    """
    output = 0
    c = len(b) - 1
    for i, value in enumerate(b):
        output += value * pow(10, c - i)
    return output



def send_update() -> bytes:
    dpad = random.randint(1, 4)
    controls = dict(
        left = dpad == 1,
        right = dpad == 2,
        up = dpad == 3,
        down = dpad == 4,
        a = bool(random.getrandbits(1)),
        b = bool(random.getrandbits(1)),
        reset = False
    )

    str_packet = ''.join([str(int(v)) for v in controls.values()])
    byte_packet = str_packet.encode()
    logging.debug(f"sent packet: {controls}")
    return byte_packet

if __name__ == "__main__":
    main()