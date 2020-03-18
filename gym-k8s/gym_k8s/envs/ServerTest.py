from concurrent import futures
import copy
import ctypes
import inspect
import json
import logging
import os
import shlex
import signal
import subprocess
import threading
import time

import gym_k8s.envs.server as server
import gym_k8s.envs.client as client

threads = []

def start_env():
    '''start server and client

    Returns:
        The instance of client thread
    '''

    global threads

    serve_thread = server.ServeThread()
    serve_thread.start()
    threads.append(serve_thread)

    client_thread = client.ClientThread()
    client_thread.start()
    threads.append(client_thread)

    return client_thread
    
def stop_env():
    global threads

    for t in threads:
        t.stop()

if __name__ == '__main__':
    logging.basicConfig()

    client_thread = start_env()

    print("all started")

    for i in range(8):
        k8sData = client_thread.get_pod_data()
        if k8sData == None:
            time.sleep(1)
            continue
        print(len(k8sData))
        print(i)
        time.sleep(1)

    stop_env()

    for t in threads:
        t.join()

    print("all exited")

