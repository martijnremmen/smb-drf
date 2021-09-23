import logging

from environment import SuperMarioBrosEnvironment

logging.basicConfig(level=logging.INFO)


def main():
    # time_step = tf_env.reset()
    # rewards = []
    # steps = []
    # num_episodes = 10000

    # for _ in range(num_episodes):
    #     episode_reward = 0
    #     episode_steps = 0
    #     tf_env.reset()
    #     while not tf_env.current_time_step().is_last():
    #         action = tf.random_uniform([1], 0, 9, dtype=tf.int32)
    #         next_time_step = tf_env.step(action)
    #         episode_steps += 1
    #         episode_reward += next_time_step.reward.numpy()
    #     rewards.append(episode_reward)
    #     steps.append(episode_steps)

    env = SuperMarioBrosEnvironment()
    env.serve()

    while True:
        action = env.action_space.sample()
        observation, reward, done, info = env.step(action)
        print(action)
        print(observation)
        print(reward)
        print(done)


if __name__ == "__main__":
    main()
