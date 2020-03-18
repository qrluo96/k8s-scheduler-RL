from concurrent import futures
import copy
import json
import logging
import os
import shlex
import signal
import subprocess
import threading
import time

import grpc

import k8s_sim_pb2
import k8s_sim_pb2_grpc

import gym_k8s.envs.RLServer

threads = []

class serveThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        gym_k8s.envs.RLServer.serve()

class clientThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        child = subprocess.Popen('go run /Users/qrluo/Documents/GitHub/k8s-scheduler-RL/remoteScheTest/*.go', shell=True, start_new_session=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        print("Tester pid: ", end = '')
        print(child.pid)

        print("Tester code: ", end = '')
        print(child.poll())

        for i in range(10):
            k8sData = gym_k8s.envs.RLServer.PODDATA
            print(len(k8sData))
            print(i)
            time.sleep(1)

        print("Kill tester")
        os.killpg(child.pid, signal.SIGTERM)
        child.wait()
        print("Tester code: ", end = '')
        print(child.poll())

if __name__ == '__main__':
    logging.basicConfig()

    serveThread = serveThread()
    clientThread = clientThread()

    serveThread.start()
    clientThread.start()

    print("all started")

    threads.append(serveThread)
    threads.append(clientThread)

    for t in threads:
        t.join()

    print("all exited")