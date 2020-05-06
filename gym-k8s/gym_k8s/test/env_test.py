import gym
import numpy as np

FIT = 0
NOTFIT = 1

def first_fit(observation):
    feasible_node = filter(observation)

    if len(feasible_node) <= 0:
        return 0
    else:
        return feasible_node[0] + 1

def filter(observation):
    feasible_node = []

    # pod_status = observation[0][1]
    cluster_status = observation[1:]

    pod_request = observation[0][1]
    
    for i in range(len(cluster_status)):
        feasible = True

        node_status = cluster_status[i]
        allocation = node_status[0]
        # print(allocation)
        request = node_status[1]
        
        remain_resource = allocation - request - pod_request
        # print(remain_resource)
        
        for j in range(4):
            if remain_resource[j] < 0:
                feasible = False
                break

        if feasible == True:
            feasible_node.append(i)

    return feasible_node

if __name__ == "__main__":
    env = gym.make('gym_k8s:k8s-v0')

    # observation = env.reset()
    
    # print('observation: ', end = '')
    # print(observation)

    # action = first_fit(observation)
    # observation, reward, done, info = env.step(action)
    # print(reward)
    # print(observation)

    
    for i_episode in range(20):
        observation = env.reset()
        t = 0
        while True:
            # env.render()
            print(observation)
            action = first_fit(observation)
            # print(action)
            observation, reward, done, info = env.step(action)
            print(reward)
            t += 1
            if done:
                print("Episode finished after {} timesteps".format(t+1))
                break

    env.close()