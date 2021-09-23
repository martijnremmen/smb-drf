import abc

import gym
import tensorflow as tf
from gym import spaces

import server


import numpy as np


class SuperMarioBrosEnvironment(gym.Env):

    def __init__(self) -> None:
        super().__init__()
        self.action_space = spaces.MultiDiscrete([5, 2, 2])
        self.observation_space = spaces.Box(low=0, high=3, shape=(12, 10), dtype='uint8')

    def serve(self) -> None: # dit moet serve zijn, niet server
        conn, addr = server.get_connection()

        self.conn = conn
        self.client_address = addr


    def reset(self):
        pass


    def step(self, action):
        assert self.action_space.contains(action), "%r (%s) invalid " % (
            action,
            type(action),
        )

        pkt = server.create_packet(dict(
            up = action[0] == 1,
            right = action[0] == 2,
            down = action[0] == 3,
            left = action[0] == 4,
            a = action[1] == 1,
            b = action[2] == 1
        ))
        self.conn.send(pkt)
        r = self.conn.recv(255)
        r = server.read_packet(r)

        observation = r['view']
        reward = r['score']
        
        return observation, reward, done, info


    def close(self):
        # TODO: close tcp session
        self.conn.close()
        pass
    

    def render(self, mode="human") -> None:
        return None
