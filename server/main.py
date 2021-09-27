import logging

import gym
from ray import tune
from ray.rllib.agents.ppo import PPOTrainer

from environment import SuperMarioBrosEnvironment

logging.basicConfig(level=logging.INFO)



def main():
    gym.register('SMB-v0', entry_point=SuperMarioBrosEnvironment)
    tune.register_env('SMB-v0', lambda cfg: SuperMarioBrosEnvironment())
    tune.run(PPOTrainer, config={
        "env": "SMB-v0",
        "num_workers": 1,
        "framework": "tf2"
        })







if __name__ == "__main__":
    main()
