from concurrent import futures
import copy
import json
import logging
import threading
import time

import grpc

import k8s_sim_pb2
import k8s_sim_pb2_grpc

import gym_k8s.envs.RLServer

class serveThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        gym_k8s.envs.RLServer.serve()

threads = []

if __name__ == '__main__':
    logging.basicConfig()

    serveThread = serveThread()
    serveThread.start()

    print("Started")

    threads.append(serveThread)

    for t in threads:
        t.join()

    print("all exited")

