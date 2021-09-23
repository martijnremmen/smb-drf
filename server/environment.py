import gym
from gym import spaces

import server


class SuperMarioBrosEnvironment(gym.Env):

    def __init__(self) -> None:
        super().__init__()
        self.action_space = spaces.MultiDiscrete([5, 2, 2])
        self.observation_space = spaces.Box(low=0, high=3, shape=(12, 10), dtype='uint8') # TODO: Check this

    def serve(self) -> None:
        conn, addr = server.get_connection()

        self.conn = conn
        self.client_address = addr

    def reset(self):
        pkt = server.create_packet(dict(
            up = False,
            right = False,
            down = False,
            left = False,
            a = False,
            b = False,
            reset = True
        ))
        self.conn.send(pkt)
        self.conn.recv(1024) # After sending we should reveice a response
        return

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
            b = action[2] == 1,
            reset = False
        ))
        self.conn.send(pkt)
        r = self.conn.recv(255)
        r = server.read_packet(r)
        
        observation = r['view']
        reward = r['score']
        done = (    
            r['playerstate'] == 4   or  # Sliding down the pole
            r['playerstate'] == 11  or  # Dying animation
            r['viewport_y']  >= 2       # Fallen down hole
        )
        info = None
        
        return observation, reward, done, info

    def close(self):
        self.conn.close()
        pass
    

    def render(self, mode="human") -> None:
        return None
