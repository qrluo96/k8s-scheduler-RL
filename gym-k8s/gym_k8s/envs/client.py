import os
import signal
import subprocess
import threading
import time

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

        for i in range(8):
            print(len(self._pod_data))
            print(i)
            time.sleep(1)

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

def set_schedule_result(node_name):
    RLServer.AddScheduleResult(node_name)

        


def act(is_fit, node_name, node_num, feasible_node_num):
    if is_fit == FIT:
        
        pass
    else:
        pass
