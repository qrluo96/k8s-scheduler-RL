import copy
import numpy as np
import os
import signal
import subprocess
import threading
import time

import gym_k8s.envs.RLServer as RLServer
# import gym_k8s.envs.threading_extender as threading_extender

FIT = RLServer.FIT
NOTFIT = RLServer.NOTFIT

class ClientThread(threading.Thread):
    childThread = None
    _pod_data = None
    _cluster_data = None

    def __init__(self):
        threading.Thread.__init__(self, daemon=True)

    def _variable_init(self):
        self.childThread = None
        self._sum_resource = {}
        self._resource_log = {}
        self.cluster_info = {}

    def run(self):
        self.restart()

    def restart(self):
        self._variable_init()

        # print(os.getcwd())

        module_path = os.path.abspath(__file__)
        parent_folder = 
            os.path.dirname(
                os.path.dirname(
                    os.path.dirname(
                        os.path.dirname(
                            module_path)))))
        folder_path = parent_folder + '/remoteScheTest'
        go_file = folder_path + '/*.go'
        config_path = parent_folder + '/gym-k8s/gym_k8s/config/'

        cmd = 'go run ' + go_file + ' --config ' + config_path

        self.childThread = subprocess.Popen(
            cmd
            # 'go run /Users/qrluo/Documents/GitHub/k8s-scheduler-RL/remoteScheTest/*.go --config /Users/qrluo/Documents/GitHub/k8s-scheduler-RL/gym-k8s/gym_k8s/config/', 
            # 'go run /Users/qrluo/Documents/GitHub/k8s-scheduler-RL/remoteScheTest/*.go', 
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
        # self._scheduled_pod_num = RLServer.FINISHEDPOD
        self._clock_list = RLServer.TIMELIST
        self._info_clock = 0

        # self.childThread.wait()
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

    # def get_pod_data(self):
    #     return self._pod_data

    def get_resource_status(self, clock):
        if clock < 0:
            clock = 0

        # print('debug ', clock)
        # print(self._resource_log[clock])
        # print(self._resource_log)

        return copy.copy(self._resource_log[clock])

    # update the latest resource data
    def _update_usage(self):
        prev_clock = self._info_clock
        self._info_clock = RLServer.INFOCLOCK
        # print('prev_clock: ', end = '')
        # print(prev_clock)
        # print('info_clock: ', end = '')
        # print(self._info_clock)

        # if the simulator is just started
        # use add_usage function to initial sum_resource var
        if self._info_clock == 0:
            self._add_usage(prev_clock)
        # if function is called at the same time stamp
        elif prev_clock == self._info_clock:
            pass
        else:
            i_start = self._clock_list.index(prev_clock)
            for clock in self._clock_list[i_start:-1]:
                self._add_usage(clock)

    
    def _add_usage(self, clock):
        cluster_data_raw = RLServer.get_cluster_data(clock)

        cluster_data = cluster_data_raw['cluster_data']

        resource_type = [
            'cpu', 'mem', 'gpu', 'pod',
        ]
        resource_kind = [
            'allocatable', 'request', 'usage',
        ]
        for node_name in cluster_data.keys():
            if node_name not in self._sum_resource:
                self._sum_resource[node_name] = {}
                for kind in resource_kind:
                    self._sum_resource[node_name][kind] = {}
                    for type in resource_type:
                        self._sum_resource[node_name][kind][type] = cluster_data[node_name][kind][type]
            else:
                for kind in resource_kind:
                    for type in resource_type:
                        self._sum_resource[node_name][kind][type] += cluster_data[node_name][kind][type]

        self._resource_log[clock] = self._sum_resource.copy()

    # act send back the schedule result to simulator
    def act(self, is_fit, suggest_host, evaluated_nodes_num, feasible_nodes_num):
        # update cluster info
        if is_fit == FIT:
            self._update_cluster_info(suggest_host)

        RLServer.add_schedule_result(is_fit, suggest_host, evaluated_nodes_num, feasible_nodes_num)

    # update cluster info after schedule
    def _update_cluster_info(self, suggest_host):
        pod_data = self.cluster_info['pod_data']
        cluster_data = self.cluster_info['cluster_data']

        keywords = ['cpu', 'mem', 'gpu']

        for key in keywords:
            cluster_data[suggest_host]['request'][key] += pod_data['request'][key]
        
        cluster_data[suggest_host]['request']['pod'] += 1

    # returns the newest cluster info
    def get_cluster_info(self):
        cluster_info = RLServer.get_cluster_data()

        # if the cluster info not update yet
        # return the updated cluster data
        if cluster_info['clock'] == 0:
            self.cluster_info = copy.copy(cluster_info)
            return self.cluster_info
        elif cluster_info['clock'] == self.cluster_info['clock']:
            return self.cluster_info
        # return the cluster info of the new time stamp
        # also update the resource data
        else:
            self.cluster_info = copy.copy(cluster_info)
            self._update_usage()
            return self.cluster_info

    def scheduled_pod_num(self):
        return RLServer.FINISHEDPOD

# if __name__ == '__main__':
#     client_thread = ClientThread()
#     client_thread.start()

#     time.sleep(8)

#     client_thread.stop()