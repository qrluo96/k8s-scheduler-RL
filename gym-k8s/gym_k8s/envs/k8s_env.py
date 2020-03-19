import gym
import numpy as np
import threading
from gym import error, spaces, utils
from gym.utils import seeding

import gym_k8s.envs.client as client
import gym_k8s.envs.config as config
import gym_k8s.envs.server as server

'''
observation space:
    CPU     MEM     GPU    pod
┌───────┬───────┬───────┬───────┐
├───────┼───────┼───────┼───────┤
 ...............................     num of nodes
├───────┼───────┼───────┼───────┤
└───────┴───────┴───────┴───────┘
'''

class K8sEnv(gym.Env):
#   metadata = {'render.modes': ['human']}
    
    # _client_thread = None
    _path = "./config.yaml"

    def __init__(self):
        self._threads = []
        self._set_space()

    def step(self, action):
        ...

    def reset(self):
        self._stop_sim()
        self._start_sim()

#   def render(self, mode='human'):
#     ...

    def close(self):
        self._stop_sim()
        self._clear_threads()

    def _start_sim(self):
        _start_server(self)
        self._client_thread = _start_client(self)

    def _stop_sim(self):
        for t in self._threads:
            t.stop()

    def _start_server(self):
        serve_thread = server.ServeThread()
        serve_thread.start()
        self._threads.append(serve_thread)

    def _start_client(self):
        client_thread = client.ClientThread()
        client_thread.start()
        self._threads.append(client_thread)

        return client_thread
    
    def _clear_threads(self):
        for t in self._threads:
            t.join()
        
        print("all exited")

    def _set_space(self):
        yaml_data = config.read_config(self._path)

        cluster_data = yaml_data["cluster"]
        
        node_names = []
        node_resources = {}
        for node_data in cluster_data:
            node_name = node_data['metadata']['name']
            node_names.append(node_name)
            node_resources[node_name] = node_data['status']['allocatable']
        
        node_num = len(node_names)
        lows = np.zeros((node_num, 4))
        highs = []
        for name in node_names:
            cpu = node_resources[name]['cpu']
            mem = node_resources[name]['memory']
            gpu = node_resources[name]['nvidia.com/gpu']
            pod = node_resources[name]['pods']
            high = [cpu, mem, gpu, pod]
            highs.append(high)
        highs = np.array(highs)

        self.action_space = spaces.Discrete(node_num)
        self.observation_space = spaces.Box(lows, highs, dtype=np.uint32)

