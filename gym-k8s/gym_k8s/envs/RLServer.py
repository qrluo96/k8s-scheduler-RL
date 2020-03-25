from concurrent import futures
import copy
import json
import logging
import threading
import time

import grpc

import k8s_sim_pb2
import k8s_sim_pb2_grpc

CLUSTERDATA = {}
PODDATA = {}

def ___init___():
    global CLUSTERDATA
    global PODDATA

    CLUSTERDATA = {}
    PODDATA = {}

def GetClusterData():
    return CLUSTERDATA

def GetPodData():
    return PODDATA
def AddPodData(key, value):
    PODDATA[key] = value

class simRPCServicer(k8s_sim_pb2_grpc.simRPCServicer):
    def RecordFormattedMetrics(self, request, context):
        global CLUSTERDATA

        metric = request.formatted_metrics

        formattedMetrics = json.loads(metric)
        # print("Formatted metrics: ", end = '')
        # print(formattedMetrics)

        # print("Clock: ", end = '')


        return k8s_sim_pb2.Result(result="1")
    
    def RecordPodMetrics(self, request, context):
        global PODDATA

        Metric = request.pod_metrics

        formattedMetrics = json.loads(Metric)
        print(formattedMetrics)

        # clock = formattedMetrics['Clock']
        # # print('Clock: ', end = '')
        # clock = str(clock)
        # # print(clock)
        # podMetrics = formattedMetrics['Pods']
        # containers = podMetrics['spec']['containers']

        # containersResources = []
        # for container in containers:
        #     formattedContainer = {}
        #     formattedContainer['name'] = container['name']
        #     formattedContainer['image'] = container['image']
        #     formattedContainer['resource'] = container['resources']
        #     # print('Formattede container: ', end = '')
        #     # print(formattedContainer)
        #     containersResources.append(formattedContainer)

        # PODDATA[clock] = [podMetrics, containersResources]
        # # print(len(PODDATA))

        return k8s_sim_pb2.Result(result="1")

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    k8s_sim_pb2_grpc.add_simRPCServicer_to_server(
        simRPCServicer(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()