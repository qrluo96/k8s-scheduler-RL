import copy
import gym
import numpy as np
import threading
from gym import error, spaces, utils
from gym.utils import seeding

import time

import gym_k8s.envs.client as client
import gym_k8s.envs.config as config
import gym_k8s.envs.server as server

'''

observation space:

# pod infomation:
#                        CPU     MEM     GPU
#                     ┌───────┬───────┬───────┐
# # limit_resource      │       │       │       │
#                     ├───────┼───────┼───────┤              
# request_resource    │       │       │       │
#                     └───────┴───────┴───────┘

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

TIME_WINDOW = 360

class K8sEnv(gym.Env):
#   metadata = {'render.modes': ['human']}

    # _path = "/Users/qrluo/Documents/GitHub/k8s-scheduler-RL/gym-k8s/gym_k8s/envs/config.yaml"

    def __init__(self):
        # variables
        self._variable_init()

        self._threads = []
        self._serve_thread = None
        self._client_thread = None

    def _variable_init(self):
        self.clock = 0
        self._feasible_node = []
        self.node_names = []
        self.status = {}
        self.tick = 0

        self._set_space()

    def step(self, action):
        print(action)
        punish = 0

        if action == 0:
            is_fit = client.NOTFIT
            node_result = 0
        # if fit, do feadible check
        else:
            is_fit = client.FIT
            node_result = action - 1

            is_feasible = self._feasible_check(node_result)
            if is_feasible == False:
                punish = -1

                is_fit = client.NOTFIT
                node_result = 0

        self._take_action(is_fit, node_result)
        # wait for next status
        self._update_status()

        ob = self._ob_format()
        is_over = self._is_over()
        reward = self._get_reward(action)
        reward += punish

        return ob, reward, is_over, {}

    def reset(self):
        self.close()
        time.sleep(3)

        self._variable_init()

        self._start_sim()

        print("Simulator starting...")
        time.sleep(3)

        self._update_status()
        ob = self._ob_format()

        return ob

    def close(self):
        self._stop_sim()
        # self._clear_threads()

    # format cluster info into observation space type
    def _ob_format(self):
        cluster_status = []

        cluster_data = self.status

        pod_data = cluster_data['pod_data']
        cluster_data = cluster_data['cluster_data']

        # format pod status
        pod_limit = pod_data['limit']
        pod_request = pod_data['request']
        pod_status = [
            [0, 0, 0, 0],
            [pod_request['cpu'], pod_request['mem'], pod_request['gpu'], 1],
            [0, 0, 0, 0],
        ]
        cluster_status.append(pod_status)

        # format cluster status
        for node_name in cluster_data.keys():
            node_data = cluster_data[node_name]
            keyword = ['cpu', 'mem', 'gpu', 'pod']
            node_alloc = self._dict_format(keyword, node_data['allocatable'])
            node_request = self._dict_format(keyword, node_data['request'])
            node_usage = self._dict_format(keyword, node_data['usage'])
            node_status = [
                node_alloc,
                node_request,
                node_usage,
            ]
            cluster_status.append(node_status)

        observation = np.array(cluster_status)

        return observation

    def _dict_format(self, key_order, dict):
        result = []

        for key in key_order:
            result.append(dict[key])

        return result

    def _feasible_check(self, node_result):
        self._feasible_node = self._filter()

        node_name = self.node_names[node_result]

        if node_name not in self._feasible_node:
            return False
        else:
            return True

#   def render(self, mode='human'):
#     ...

    def _filter(self):
        feasible_node = []

        pod_status = self.status['pod_data']
        cluster_status = self.status['cluster_data']

        pod_request = pod_status['request']

        for node_name in self.node_names:
            status = cluster_status[node_name]
            allocatable = status['allocatable']
            request = status['request']

            if allocatable['pod'] - request['pod'] < 1:
                continue
            if allocatable['cpu'] - request['cpu'] < pod_request['cpu']:
                continue
            if allocatable['mem'] - request['mem'] < pod_request['mem']:
                continue
            if allocatable['gpu'] - request['gpu'] < pod_request['gpu']:
                continue

            feasible_node.append(node_name)

        return feasible_node

    def _is_over(self):
        scheduled_pod_num = self._client_thread.scheduled_pod_num()

        if scheduled_pod_num < 1024:
            return False
        else:
            return True

    def _get_reward(self, action):
        reward = 0

        if self.clock == 0:
            return reward

        resource_type = [
            'cpu', 'mem', 'gpu', 'pod',
        ]

        total_resource = self._client_thread.get_resource_status(self.clock - self.tick)
        # print(total_resource)
        avg_request_prcnt = self._get_resource_avg(total_resource, 'request')
        # print(avg_request_prcnt)
        # avg_usage_prcnt = self._get_resource_avg(total_resource, 'usage')
        avg_reward = self._resource_scale(avg_request_prcnt)
        reward += avg_reward
        
        # TODO: accummulated utilization rate for a curtain time window
        delta_time = TIME_WINDOW * self.tick
        prev_clock = self.clock - delta_time
        if prev_clock < 0:
            prev_clock = 0
        prev_resource = self._client_thread.get_resource_status(prev_clock)
        dif_resource = self._dif_resource(total_resource, prev_resource)
        time_window_request_prcnt = self._get_resource_avg(dif_resource, 'request')
        time_window_reward = self._resource_scale(time_window_request_prcnt)
        reward += time_window_reward

        return reward

    def _resource_scale(self, avg_resource_prcnt):
        # print(avg_resource_prcnt)

        score = 0
        score += avg_resource_prcnt['cpu'] * 0.8
        score += avg_resource_prcnt['mem'] * 1
        score += avg_resource_prcnt['gpu'] * 1.2

        return score

    # dif_resource = resource_1 - resource_2
    def _dif_resource(self, resource_1, resource_2):
        # print(resource_1)
        # print(resource_2)

        resource_type = [
            'cpu', 'mem', 'gpu', 'pod',
        ]
        resource_kind = [
            'allocatable', 'request', 'usage',
        ]

        dif_resource = {}
        for node_name in resource_1.keys():
            dif_resource[node_name] = {}
            for kind in resource_kind:
                dif_resource[node_name][kind] = {}
                for type in resource_type:
                    dif_resource[node_name][kind][type] = resource_1[node_name][kind][type] - resource_2[node_name][kind][type]

        return copy.copy(dif_resource)

    def _get_resource_avg(self, total_resource, consume_kind):
        if consume_kind != 'request' and consume_kind != 'usage':
            raise Exception('Resource type wrong!')

        resource_type = [
            'cpu', 'mem', 'gpu', 'pod',
        ]

        alloc_resource = {}
        consume_resource = {}
        avg_resource = {}
        for type in resource_type:
            alloc_resource[type] = 0
            consume_resource[type] = 0
            avg_resource[type] = 0

        for node_name in total_resource.keys():
            for type in resource_type:
                alloc_resource[type] += total_resource[node_name]['allocatable'][type]
                consume_resource[type] += total_resource[node_name][consume_kind][type]

        for type in resource_type:
            if alloc_resource[type] == 0:
                avg_resource[type] = 0
                continue
            avg_resource[type] = consume_resource[type]/alloc_resource[type]

        return copy.copy(avg_resource)


    def _update_status(self):
        cluster_info = self._client_thread.get_cluster_info()

        clock = cluster_info['clock']
        pod_data = cluster_info['pod_data']
        cluster_data = cluster_info['cluster_data']

        # cluster_status = []
        # for node_name in self.node_names:
        #     cluster_status.append(cluster_data[node_name])
        # cluster_status = np.array(cluster_status)

        self.status = {
            'clock': clock, 
            'pod_data': pod_data, 
            'cluster_data': copy.copy(cluster_data)
        }

        self.clock = clock

    # def _take_action(self, action):
    #     if action == 0:
    #         is_fit = client.NOTFIT
    #         node_result = 0
    #     else:
    #         is_fit = client.FIT
    #         node_result = action - 1

    #     node_name = self.node_names[node_result]
    #     node_num = len(self.node_names)
    #     feasible_node_num = len(self._feasible_node)
    #     self._client_thread.act(is_fit, node_name, node_num, feasible_node_num)

    def _take_action(self, is_fit, node_result):
        node_name = self.node_names[node_result]
        node_num = len(self.node_names)
        feasible_node_num = len(self._feasible_node)
        self._client_thread.act(is_fit, node_name, node_num, feasible_node_num)

    def _start_sim(self):
        self._threads = []
        print("Server starting")
        self._start_server()
        time.sleep(1)
        print("Client starting")
        self._start_client()

        print('_serve_thread is alive? ', self._serve_thread.is_alive())
        print('_client_thread is alive? ', self._client_thread.is_alive())

    def _stop_sim(self):
        for t in self._threads:
            t.stop()

    def _start_server(self):
        if self._serve_thread == None:
            self._serve_thread = server.ServeThread()
            self._serve_thread.start()
        else:
            self._serve_thread.restart()
            

    def _start_client(self):
        if self._client_thread == None:
            self._client_thread = client.ClientThread()
            self._client_thread.start()
        else:
            self._client_thread.restart()
        # self._client_thread = client.ClientThread()
        # self._client_thread.start()

        # self._threads.append(self._client_thread)
    
    # def _clear_threads(self):
    #     if self._client_thread != None:
    #         self._client_thread.join()
        
    #     print("all exited")

    def _set_space(self):
        yaml_data = config.read_config()

        self.tick = yaml_data['tick']
        cluster_data = yaml_data['cluster']
        
        node_names = []
        node_resources = {}
        for node_data in cluster_data:
            node_name = node_data['metadata']['name']
            node_names.append(node_name)
            node_resources[node_name] = node_data['status']['allocatable']
        
        self.node_names = node_names
        # print(self.node_names)
        node_num = len(self.node_names)

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
        
        resource_limit = [max_cpu, max_mem, max_gpu, max_pod]
        node_limit = []
        for i in range(3):
            node_limit.append(resource_limit)
        cluster_limit = []
        for i in range(node_num + 1):
            cluster_limit.append(node_limit)

        pod_resources_limit = [max_cpu, max_mem, max_gpu, 1]

        self.action_space = spaces.Discrete(node_num + 1)
        self.observation_space = spaces.Box(
            low = np.zeros((node_num + 1, 3, 4)),
            high = np.array(cluster_limit),
            dtype = np.int32,
        )

ACTION_LOOKUP = {
    0 : client.FIT,
    1 : client.NOTFIT,
}


