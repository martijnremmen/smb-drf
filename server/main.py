import logging

from environment import SuperMarioBrosEnvironment

logging.basicConfig(level=logging.INFO)


def main():

    env = SuperMarioBrosEnvironment()

    while True:
        action = env.action_space.sample()
        observation, reward, done, info = env.step(action)
        if done: env.reset()

if __name__ == "__main__":
    main()
