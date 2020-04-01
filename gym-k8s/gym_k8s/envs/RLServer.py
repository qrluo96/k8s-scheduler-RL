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

        bytes = request.formatted_metrics
        cluster_data = json.loads(bytes)
        # print("Formatted metrics: ", end = '')
        # print(formattedMetrics)
        self.add_cluster_data(cluster_data)

        return k8s_sim_pb2.Result(result="1")

    def RecordPodMetrics(self, request, context):
        global PODDATA

        bytes = request.pod_metrics
        pod_data = json.loads(bytes)
        # print(pod_data)
        self.add_pod_data(pod_data)

        return k8s_sim_pb2.Result(result="1")

    # CLUSTERDATA[clock] {'node-0': {'allocatable': {'cpu': 4, 'mem': 8, 'gpu': 1, 'pod': 2}, 'request': {'cpu': 4, 'mem': 4, 'gpu': 1, 'pod': 1}, 'usage': {'cpu': 3, 'mem': 4, 'gpu': 0, 'pod': 1}}, 'node-1': {'allocatable': {'cpu': 8, 'mem': 16, 'gpu': 2, 'pod': 4}, 'request': {'cpu': 8, 'mem': 8, 'gpu': 2, 'pod': 2}, 'usage': {'cpu': 6, 'mem': 6, 'gpu': 1, 'pod': 2}}}
    def add_cluster_data(self, cluster_data):
        global CLUSTERDATA

        clock = str(cluster_data['Clock'])
        CLUSTERDATA[clock] = {}

        nodes = cluster_data['Nodes']
        # print(nodes.keys())
        for node_name in nodes.keys():
            CLUSTERDATA[clock][node_name] = {}
            node = nodes[node_name]
            # print(node_name)
            # print(node)

            pod_num = node['RunningPodsNum']

            allocatable = node['Allocatable']
            allocatable = self.allocatable_resource_config(allocatable)
            request = node['TotalResourceRequest']
            request = self.cluster_resource_config(request, pod_num)
            usage = node['TotalResourceUsage']
            usage = self.cluster_resource_config(usage, pod_num)

            CLUSTERDATA[clock][node_name]['allocatable'] = allocatable
            CLUSTERDATA[clock][node_name]['request'] = request
            CLUSTERDATA[clock][node_name]['usage'] = usage

        print(clock, end = ' ')
        print(CLUSTERDATA[clock])

    def cluster_resource_config(self, resources, pod_num):
        result = {}

        if len(resources.keys()) == 0:
            result['cpu'] = 0
            result['mem'] = 0
            result['gpu'] = 0
            result['pod'] = pod_num

            return result

        cpu = int(resources['cpu'])
        mem = resources['memory']
        mem_suffix = mem[len(mem) - 2:]
        if mem_suffix != 'Gi':
            raise Exception('The unit should be \'Gi\'')
        mem_int = int(mem[:-2])
        gpu = int(resources['nvidia.com/gpu'])

        result['cpu'] = cpu
        result['mem'] = mem_int
        result['gpu'] = gpu
        result['pod'] = pod_num

        return result

    def allocatable_resource_config(self, resources):
        cpu = int(resources['cpu'])
        mem = resources['memory']
        mem_suffix = mem[len(mem) - 2:]
        if mem_suffix != 'Gi':
            raise Exception('The unit should be \'Gi\'')
        mem_int = int(mem[:-2])
        gpu = int(resources['nvidia.com/gpu'])
        pod = int(resources['pods'])

        result = {}
        result['cpu'] = cpu
        result['mem'] = mem_int
        result['gpu'] = gpu
        result['pod'] = pod

        return result

    # PODDATA[uid] = {'limits': {'cpu': 6, 'mem': 6, 'gpu': 1}, 'requests': {'cpu': 4, 'mem': 4, 'gpu': 1}, 'priority': 0}
    def add_pod_data(self, pod_data):
        global PODDATA

        clock = str(pod_data['Clock'])
        # print(clock)

        uid = pod_data['Pod']['metadata']['uid']
        spec = pod_data['Pod']['spec']
        containers = spec['containers']

        limit_cpu = 0
        limit_mem = 0
        limit_gpu = 0

        request_cpu = 0
        request_mem = 0
        request_gpu = 0

        for container in containers:
            limits = container['resources']['limits']
            limits = self.resource_config(limits)
            limit_cpu += limits['cpu']
            limit_mem += limits['mem']
            limit_gpu += limits['gpu']

            requests = container['resources']['requests']
            requests = self.resource_config(requests)
            request_cpu += requests['cpu']
            request_mem += requests['mem']
            request_gpu += requests['gpu']

        prio = spec['priority']

        PODDATA[uid] = {}
        PODDATA[uid]['limits'] = {}
        PODDATA[uid]['limits']['cpu'] = limit_cpu
        PODDATA[uid]['limits']['mem'] = limit_mem
        PODDATA[uid]['limits']['gpu'] = limit_gpu
        PODDATA[uid]['requests'] = {}
        PODDATA[uid]['requests']['cpu'] = request_cpu
        PODDATA[uid]['requests']['mem'] = request_mem
        PODDATA[uid]['requests']['gpu'] = request_gpu
        PODDATA[uid]['priority'] = prio

        print(uid, end = ' ')
        print(PODDATA[uid])

    def resource_config(self, resources):
        result = {}

        cpu = int(resources['cpu'])
        mem = resources['memory']
        mem_suffix = mem[len(mem) - 2:]
        if mem_suffix != 'Gi':
            raise Exception('The unit should be \'Gi\'')
        mem_int = int(mem[:-2])
        gpu = int(resources['nvidia.com/gpu'])

        result['cpu'] = cpu
        result['mem'] = mem_int
        result['gpu'] = gpu

        return result

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    k8s_sim_pb2_grpc.add_simRPCServicer_to_server(
        simRPCServicer(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()