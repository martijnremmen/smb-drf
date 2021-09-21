import gym
from gym import spaces
from gym.spaces import space

from numpy import uint8

class SuperMarioBros(gym.Env):

    def __init__(self) -> None:
        super().__init__()
        self.action_space = spaces.Discrete(6) # up, down, left, right, A, B
        self.observation_space = spaces.Box(low=0, high=3, shape=(12, 10), dtype=uint8)

    def __set_socket(self) -> None:
        pass

    
    def step(self, action):
        pass
