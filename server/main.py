from environment import SuperMarioBrosEnvironment
from pprint import pprint

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
    boi = env.action_space.sample()
    print(
        boi[0],
        boi[1],
        boi[2]
    )

    # if asdkjnaksjnd:
        # hier iets doen als knop 'A'


if __name__ == "__main__":
    main()