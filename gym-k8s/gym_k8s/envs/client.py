import os
import signal
import subprocess
import threading
import time
import numpy as np

import gym_k8s.envs.RLServer as RLServer
import gym_k8s.envs.threading_extender as threading_extender

FIT = RLServer.FIT
NOTFIT = RLServer.NOTFIT

class ClientThread(threading.Thread):
    childThread = None
    _pod_data = None
    _cluster_data = None

    def __init__(self):
        threading.Thread.__init__(self, daemon=True)
        self.childThread = None

    def run(self):
        self.childThread = subprocess.Popen(
            'go run /Users/qrluo/Documents/GitHub/k8s-scheduler-RL/remoteScheTest/*.go', 
            shell=True, 
            start_new_session=True, 
            stdout=subprocess.DEVNULL, 
            stderr=subprocess.DEVNULL
            )
        
        print("Tester pid: ", end = '')
        print(self.childThread.pid)

        print("Tester code: ", end = '')
        print(self.childThread.poll())

        self._pod_data = RLServer.PODDATA
        self._cluster_data = RLServer.CLUSTERDATA
        self._scheduled_pod_num = RLServer.FINISHEDPOD

        self.childThread.wait()
        print("Tester code: ", end = '')
        print(self.childThread.poll())
    
    def stop(self):
        if self.childThread == None:
            return 0
        print("Kill client")
        os.killpg(self.childThread.pid, signal.SIGTERM)
        self.childThread.wait()
        print("Tester code: ", end = '')
        print(self.childThread.poll())

    def get_pod_data(self):
        return self._pod_data

    # act send back the schedule result to simulator
    def act(self, is_fit, suggest_host, evaluated_nodes_num, feasible_nodes_num):
        RLServer.add_schedule_result(is_fit, suggest_host, evaluated_nodes_num, feasible_nodes_num)

    # get status returns the newest cluster info
    def get_cluster_info(self):
        cluster_info = RLServer.get_cluster_data()

        pod_data = cluster_info['pod_data']
        cluster_data = cluster_info['cluster_data']

        pod_limit = pod_data['limit']
        pod_request = pod_data['request']
        pod_status = np.array([
            [pod_limit['cpu'], pod_limit['mem'], pod_limit['gpu']],
            [pod_request['cpu'], pod_request['mem'], pod_request['gpu']]
        ])
        cluster_info['pod_data'] = pod_status

        for node_name in cluster_data.keys():
            node_data = cluster_data[node_name]
            keyword = ['cpu', 'mem', 'gpu', 'pod']
            node_alloc = self.dict_format(keyword, node_data['allocatable'])
            node_request = self.dict_format(keyword, node_data['request'])
            node_usage = self.dict_format(keyword, node_data['usage'])
            node_status = [
                node_alloc,
                node_request,
                node_usage
            ]
            cluster_data[node_name] = node_status

        return cluster_info

    def dict_format(self, key_order, dict):
        result = []

        for key in key_order:
            result.append(dict[key])

        return result

    def scheduled_pod_num(self):
        return self._scheduled_pod_num