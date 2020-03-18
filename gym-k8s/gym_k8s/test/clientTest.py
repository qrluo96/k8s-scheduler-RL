from concurrent import futures
import copy
import json
import logging
import os
import signal
import subprocess
import threading
import time

import grpc

import gym_k8s.envs.RLServer

threads = []

class clientThread(threading.Thread):
    childThread = None
    podData = None

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

        for i in range(8):
            k8sData = gym_k8s.envs.RLServer.PODDATA
            print(len(k8sData))
            print(i)
            time.sleep(1)

        # for i in range(10):
        #     self.podData = gym_k8s.envs.RLServer.PODDATA
        #     print(len(self.podData))
        #     print(i)
        #     time.sleep(1)

        # kill current thread
        print("Kill tester")
        os.killpg(self.childThread.pid, signal.SIGTERM)

        self.childThread.wait()
        print("Tester code: ", end = '')
        print(self.childThread.poll())
    
    def stop(self):
        print("Kill tester")
        os.killpg(self.childThread.pid, signal.SIGTERM)
        self.childThread.wait()
        print("Tester code: ", end = '')
        print(self.childThread.poll())

# class clientThread(threading.Thread):
#     def __init__(self):
#         threading.Thread.__init__(self)

#     def run(self):
#         child = subprocess.Popen('go run /Users/qrluo/Documents/GitHub/k8s-scheduler-RL/remoteScheTest/*.go', shell=True, start_new_session=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

#         print("Tester pid: ", end = '')
#         print(child.pid)

#         print("Tester code: ", end = '')
#         print(child.poll())

#         for i in range(10):
#             k8sData = gym_k8s.envs.RLServer.PODDATA
#             print(len(k8sData))
#             print(i)
#             time.sleep(1)

#         print("Kill tester")
#         os.killpg(child.pid, signal.SIGTERM)
#         child.wait()
#         print("Tester code: ", end = '')
#         print(child.poll())

if __name__ == '__main__':
    logging.basicConfig()


    clientThread = clientThread()
    clientThread.start()
    threads.append(clientThread)

    print("all started")

    for t in threads:
        t.join()

    print("all exited")

