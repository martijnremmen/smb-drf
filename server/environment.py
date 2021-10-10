import gym
from gym import spaces

import server


class SuperMarioBrosEnvironment(gym.Env):

    def __init__(self) -> None:
        super().__init__()
        self.action_space = spaces.MultiDiscrete([5, 2, 2])
        self.observation_space = spaces.Box(low=0, high=8, shape=(12, 10), dtype='uint8')

        self._previous_x_position = 44
        self.serve()

    def _get_reward(self, gamestate) -> float:
        reward = 0

        # Reward for progressing to the right
        reward += gamestate['x_position'] - self._previous_x_position
        self._previous_x_position = gamestate['x_position']

        # Dying and falling out of viewport are punished
        if gamestate['playerstate'] == 11 or\
            gamestate['viewport_y'] >= 2:
            reward += -10

        # Reaching the finish flag is rewarded (based on the 'sliding' playerstate)
        if gamestate['playerstate'] == 4:
            reward += 100

        # Passing of time is punished (quicker runs are better)
        reward += -0.5

        # Future rewards have larger weight
        reward *= (400 - gamestate['time']) / 400

        return reward

    def _response_to_output(self, r: bytes):
        r = server.deserialize_packet(r)
        
        observation = r['view']
        reward = self._get_reward(r)
        done = (    
            r['playerstate'] == 4   or  # Sliding down the pole
            r['playerstate'] == 11  or  # Dying animation
            r['viewport_y']  >= 2       # Fallen down hole
        )
        info = {}

        return observation, reward, done, info

    def serve(self) -> None:
        conn, addr = server.get_connection()

        self.conn = conn
        self.client_address = addr

    def reset(self):
        pkt = server.serialize_packet(dict(
            up = False,
            right = False,
            down = False,
            left = False,
            a = False,
            b = False,
            reset = True
        ))
        self.conn.send(pkt)
        r = server.receive_pkt(self.conn) # After sending we should receive a response
        self._previous_x_position = 44
        observation, _, _, _ = self._response_to_output(r)
        return observation # Apparently `reset` should only return an observation 

    def step(self, action):
        assert self.action_space.contains(action), "%r (%s) invalid " % (
            action,
            type(action),
        )

        pkt = server.serialize_packet(dict(
            up = action[0] == 1,
            right = action[0] == 2,
            down = action[0] == 3,
            left = action[0] == 4,
            a = action[1] == 1,
            b = action[2] == 1,
            reset = False
        ))
        self.conn.send(pkt)
        r = server.receive_pkt(self.conn)
        return self._response_to_output(r)


    def close(self):
        self.conn.close()
        return
    

    def render(self, mode="human") -> None:
        return None


def main():
    env = SuperMarioBrosEnvironment()
    while True:
        obs, reward, done, info = env.step([0, 0, 0])
        if done:
            env.reset()

if __name__ == "__main__":
    main()