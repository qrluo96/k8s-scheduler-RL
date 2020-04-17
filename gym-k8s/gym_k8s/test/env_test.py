import gym

env = gym.make('gym_k8s:k8s-v0')

observation = env.reset()

print(observation)