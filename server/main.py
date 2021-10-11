import logging

import gym
from stable_baselines3 import PPO
from stable_baselines3.common.env_util import make_vec_env

from environment import SuperMarioBrosEnvironment

logging.basicConfig(level=logging.INFO)



def main():
    gym.register('SMB-v0', entry_point=SuperMarioBrosEnvironment)
    env = make_vec_env('SMB-v0')

    model = PPO("MlpPolicy", env, verbose=1, tensorboard_log='./tslog')
    model.load('Mark-v5', env=env)
    model.learn(total_timesteps=409600)
    model.save('Mark-v5')



if __name__ == "__main__":
    main()
