#!/usr/bin/env python3
import logging
import random
import socket

import numpy as np

logging.basicConfig(level=logging.INFO)

BIND_ADDRESS = '127.0.0.1'
BIND_PORT = 6969

def main():
    con, addr = get_connection()
    handle_client(con, addr)

def get_connection(
        address: str = BIND_ADDRESS, 
        port: int = BIND_PORT
    ) -> tuple[socket.socket, set]:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((address, port))
        s.listen(2)
        logging.info(f"listening on {s.getsockname()[0]}:{s.getsockname()[1]}")
    
        return s.accept()


def handle_client(c: socket.socket, addr):
    logging.info(f"Client {addr[0]}:{addr[1]} connected")

    while True:
        r = c.recv(4096)
        if not r:
            break
        deserialize_packet(r)
        c.send(serialize_packet())
    

    c.close()
    logging.info(f"Client {addr[0]}:{addr[1]} disconnected")


def receive_pkt(conn: socket.socket) -> bytes:
    r = b""
    while len(r) != 140:
        r += conn.recv(140)
        if not r:
            break
    return r


def deserialize_view(sview: bytes) -> np.array:
    temp = [ int(i) for i in sview.decode('utf-8') ]
    arr = np.array(temp, dtype='uint8')
    arr.shape = (12, 10)
    return arr

def deserialize_packet(raw_input: bytes) -> dict:

    logging.debug(f"received packet: {raw_input}")
    output =  dict(
        score = int(raw_input[0:6]),
        time = int(raw_input[6:9]),
        view = deserialize_view(raw_input[9:129]),
        x_position = int(raw_input[129:133]),
        y_position = int(raw_input[133:136]),
        playerstate = int(raw_input[136:138]),
        viewport_y = int(raw_input[138:140])
    )
    logging.debug(f"received values: {output}")

    return output

def serialize_packet(controls: dict = None) -> bytes:

    # serialize the control byte
    control_byte = 0
    for i, value in enumerate(controls.values()):
        control_byte += value * (2 ** i)
    control_byte = int(control_byte).to_bytes(1, 'little')

    packet = bytearray()
    packet += bytearray(control_byte)

    logging.debug(f"sent values: {controls}")
    logging.debug(f"sent packet: {packet}")
    return packet

if __name__ == "__main__":
    main()