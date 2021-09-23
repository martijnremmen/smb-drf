#!/usr/bin/env python3
import socket
import logging
import random
import numpy as np

BIND_ADDRESS = '127.0.0.1'
BIND_PORT = 6969

logging.basicConfig(level=logging.DEBUG)


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
        read_packet(r)
        c.send(create_packet())
    

    c.close()
    logging.info(f"Client {addr[0]}:{addr[1]} disconnected")


def deserialize_view(sview: bytes) -> list[list[int]]:

    print(sview.decode('utf-8').split())
    temp = [ int(i) for i in sview.decode('utf-8') ]
    arr = np.array(temp, dtype='uint8')
    arr.shape = (12, 10)
    return arr

def read_packet(raw_input: bytes) -> dict:

    logging.debug(f"received packet: {raw_input}")
    output =  dict(
        score = int(raw_input[0:6]),
        time = int(raw_input[6:9]),
        view = deserialize_view(raw_input[9:129]),
        x_position = int(raw_input[129:133])
    )
    print(len(raw_input[129:]))
    logging.debug(output['x_position'])
    logging.debug(f"received values: {output}")

    return output



def create_packet(controls: dict = None) -> bytes:

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

    # serialize the control byte
    control_byte = 0
    for i, value in enumerate(controls.values()):
        control_byte += value * (2 ** i)
    control_byte =  control_byte.to_bytes(1, 'little')

    packet = bytearray()
    packet += bytearray(control_byte)

    logging.debug(f"sent values: {controls}")
    logging.debug(f"sent packet: {packet}")
    return packet

if __name__ == "__main__":
    main()