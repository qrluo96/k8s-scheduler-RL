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
clock:

pod infomation:
                       CPU     MEM     GPU
                    ┌───────┬───────┬───────┐
limit_resource      │       │       │       │
                    ├───────┼───────┼───────┤              
request_resource    │       │       │       │
                    └───────┴───────┴───────┘

cluster infomation:
  alloc  request  usage 
┌───────┬───────┬───────┐
│   x   │   x   │   x   │
├───────┼───────┼───────┤
 .......................     num of nodes
├───────┼───────┼───────┤
└───────┴───────┴───────┘

x = [
    cpu
    mem
    gpu
    pod
]

'''

class K8sEnv(gym.Env):
#   metadata = {'render.modes': ['human']}
    # _client_thread = None
    _path = "/Users/qrluo/Documents/GitHub/k8s-scheduler-RL/gym-k8s/gym_k8s/envs/config.yaml"

    def __init__(self):
        self._threads = []
        self._set_space()

    def step(self, action):
        self._take_action(action)
        self.status = self._get_status()

        ob = self.status
        is_over = self._is_over()
        reward = self._get_reward()

        return ob, reward, is_over, {}

    def reset(self):
        self._stop_sim()
        self._start_sim()

#   def render(self, mode='human'):
#     ...

    def close(self):
        self._stop_sim()
        self._clear_threads()

    def _is_over(self):
        scheduled_pod_num = self.client_thread.scheduled_pod_num()

        if scheduled_pod_num < 1024:
            return False
        else:
            return True

    def _get_reward(self):
        # TODO: complete reward calculate function
        return 1

    def _get_status(self):
        cluster_info = self.client_thread.get_cluster_info()

        clock = cluster_info['clock']
        pod_status = cluster_info['pod_data']
        cluster_data = cluster_info['cluster_data']

        cluster_status = []
        for node_name in self.node_names:
            cluster_status.append(cluster_data[node_name])
        cluster_status = np.array(cluster_status)

        status = tuple(clock, pod_status, cluster_status)

        return status

    def _take_action(self, action):
        is_fit = ACTION_LOOKUP[action[0]]
        node_name = self.node_names[action[1]]
        node_num = len(self.node_names)
        # TODO: complete the calculation of feasible_node_num
        feasible_node_num = node_num
        self.client_thread.act(is_fit, node_name, node_num, feasible_node_num)

    def _start_sim(self):
        _start_server(self)
        self.client_thread = _start_client(self)

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
        
        self.node_names = node_names
        node_num = len(node_names)

        max_cpu = 0
        max_mem = 0
        max_gpu = 0
        max_pod = 0
        # set the space of cluster information
        cluster_info_spaces = []
        for name in node_names:
            cpu = node_resources[name]['cpu']
            mem = node_resources[name]['memory']
            mem_suffix = mem[len(mem) - 2:]
            if mem_suffix != 'Gi':
                raise Exception('The unit should be \'Gi\'')
            mem_int = int(mem[:-2])
            gpu = node_resources[name]['nvidia.com/gpu']
            pod = node_resources[name]['pods']

            max_cpu = max(max_cpu, cpu)
            max_mem = max(max_mem, mem_int)
            max_gpu = max(max_gpu, gpu)
            max_pod = max(max_pod, pod)

            # resources_limit = [cpu, mem_int, gpu, pod]

            # discrete_space  = spaces.Box(
            #     low = [0, 0, 0, 0], 
            #     high = resources_limit,
            #     dtype = np.int32,
            # )
            # cluster_info_spaces.append(discrete_space)
        
        resource_limit = [max_cpu, max_mem, max_gpu, max_pod]
        node_limit = []
        for i in range(3):
            node_limit.append(resource_limit)
        cluster_limit = []
        for i in range(node_num):
            cluster_limit.append(node_limit)

        pod_resources_limit = [max_cpu, max_mem, max_gpu]

        # self.action_space = spaces.Discrete(node_num)
        self.action_space = spaces.Tuple((
            spaces.Discrete(2),
            spaces.Discrete(node_num),
        ))
        self.observation_space = spaces.Tuple((
            # clock
            spaces.Discrete(np.inf),
            # pod info
            spaces.Box(
                low = np.zeros((2, 3)),
                high = np.array([pod_resources_limit, pod_resources_limit]),
                # shape = (2, 3),
                dtype=np.int32
            ),
            # cluster info
            spaces.Box(
                low = np.zeros((node_num, 3, 4)),
                high = np.array(cluster_limit),
                # shape = (node_num, 3, 4),
                dtype = np.int32
            ),
        ))

ACTION_LOOKUP = {
    0 : client.FIT,
    1 : client.NOTFIT,
}


