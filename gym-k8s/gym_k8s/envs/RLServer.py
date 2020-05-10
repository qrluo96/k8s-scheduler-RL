from concurrent import futures
import copy
import json
import logging
import threading
import time
import numpy as np

import grpc

import gym_k8s.envs.k8s_util as k8s_util
import gym_k8s.envs.k8s_sim_pb2 as k8s_sim_pb2
import gym_k8s.envs.k8s_sim_pb2_grpc as k8s_sim_pb2_grpc

CLUSTERDATA = {}
PODDATA = {}
SCHEDULERESULT = {}
INITCLOCK = -1
RESULTCLOCK = -1
INFOCLOCK = -1
FIT = 0
NOTFIT = 1
FINISHEDPOD = 0
NEWPOD = False
TIMELIST = []

def restart():
    global CLUSTERDATA
    global PODDATA
    global SCHEDULERESULT
    global INITCLOCK
    global RESULTCLOCK
    global INFOCLOCK
    global FIT
    global NOTFIT
    global FINISHEDPOD
    global NEWPOD
    global TIMELIST
    
    CLUSTERDATA = {}
    PODDATA = {}
    SCHEDULERESULT = {}
    INITCLOCK = -1
    RESULTCLOCK = -1
    INFOCLOCK = -1
    FIT = 0
    NOTFIT = 1
    FINISHEDPOD = 0
    NEWPOD = False
    TIMELIST = []

# get_cluster_data return the newest status data after send backschedule result
def get_cluster_data(clock = None):
    count = 0

    while NEWPOD != True:
        time.sleep(0.001)

    print('INFOCLOCK: ', end = '')
    print(INFOCLOCK)
    if clock == None:
        clock = INFOCLOCK
    print('clock: ', end = '')
    print(clock)
    pod_data = PODDATA[clock][-1]

    cluster_data = CLUSTERDATA[clock]

    status = {
        'clock': clock,
        'pod_data': pod_data,
        'cluster_data': cluster_data,
    }
    
    return copy.copy(status)

def add_schedule_result(is_fit, suggest_host, evaluated_nodes_num, feasible_nodes_num):
    global PODDATA
    global SCHEDULERESULT
    global INFOCLOCK
    global RESULTCLOCK
    global FINISHEDPOD
    global NEWPOD

    clock = INFOCLOCK

    if clock not in SCHEDULERESULT:
        SCHEDULERESULT[clock] = {}
        RESULTCLOCK = clock

    pod = PODDATA[clock][-1]
    pod_uid = pod['uid']

    if is_fit == FIT:
        FINISHEDPOD += 1
        result = {
            'schedule_process': is_fit,
            'suggest_host': suggest_host,
            'evaluated_nodes': evaluated_nodes_num,
            'feasible_nodes': feasible_nodes_num,
        }
    else:
        result = {
            'schedule_process': is_fit,
            'suggest_host': '',
            'evaluated_nodes': 0,
            'feasible_nodes': 0,
        }

    SCHEDULERESULT[clock][pod_uid] = result
    NEWPOD = False

class simRPCServicer(k8s_sim_pb2_grpc.simRPCServicer):
    def RecordFormattedMetrics(self, request, context):
        print("new cluster data")
        bytes = request.formatted_metrics
        cluster_data = json.loads(bytes)
        # print("Formatted metrics: ", end = '')
        # print(formattedMetrics)
        self.add_cluster_data(cluster_data)

        return k8s_sim_pb2.Result(result="1")

    def RecordPodMetrics(self, request, context):
        global PODDATA
        global NEWPOD

        print("new pod data")

        bytes = request.pod_metrics
        pod_data = json.loads(bytes)
        # print(pod_data)
        self.add_pod_data(pod_data)
        NEWPOD = True

        return k8s_sim_pb2.Result(result="1")

    def ListScheduleResult(self, request, context):
        bytes = request.pod_metrics
        pod_data = json.loads(bytes)

        schedule_result = self._get_schedule_result(pod_data)

        return schedule_result
    
    # _get_schedule_result return the protobuf formatted data
    def _get_schedule_result(self, pod_data):
        global SCHEDULERESULT

        clock_str = str(pod_data['Clock'])
        clock = self._format_clock(clock_str)

        pod_uid = pod_data['Pod']['metadata']['uid']

        while True:
            if clock not in SCHEDULERESULT:
                time.sleep(0.001)
            else:
                timestamp_results = SCHEDULERESULT[clock]
                if pod_uid not in timestamp_results:
                    time.sleep(0.001)
                else:
                    result = timestamp_results[pod_uid]
                    schedule_result = k8s_sim_pb2.ScheduleResult(
                        suggest_host = result['suggest_host'],
                        evaluated_nodes = result['evaluated_nodes'],
                        feasible_nodes = result['feasible_nodes'],
                        schedule_process = result['schedule_process']
                    )

                    print(schedule_result)

                    return schedule_result            

    # CLUSTERDATA[clock] {'node-0': {'allocatable': {'cpu': 4, 'mem': 8, 'gpu': 1, 'pod': 2}, 'request': {'cpu': 4, 'mem': 4, 'gpu': 1, 'pod': 1}, 'usage': {'cpu': 3, 'mem': 4, 'gpu': 0, 'pod': 1}}, 'node-1': {'allocatable': {'cpu': 8, 'mem': 16, 'gpu': 2, 'pod': 4}, 'request': {'cpu': 8, 'mem': 8, 'gpu': 2, 'pod': 2}, 'usage': {'cpu': 6, 'mem': 6, 'gpu': 1, 'pod': 2}}}
    def add_cluster_data(self, cluster_data):
        global CLUSTERDATA
        global INFOCLOCK
        global TIMELIST

        clock_str = str(cluster_data['Clock'])
        print(clock_str)
        clock = self._format_clock(clock_str)
        TIMELIST.append(clock)
        INFOCLOCK = clock
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
    
    def _format_clock(self, clock):
        global INITCLOCK

        clock = k8s_util.parse_clock(clock)
        if INITCLOCK == -1:
            INITCLOCK = clock

        relative_clock = clock - INITCLOCK
        relative_clock = int(relative_clock)

        return relative_clock

    # cluster_resource_config format the resource information 
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

        clock_str = str(pod_data['Clock'])
        clock = self._format_clock(clock_str)
        # print(clock_str)

        if clock not in PODDATA:
            PODDATA[clock] = []

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

        pod = {
            'uid': uid,
            'limit': {},
            'request': {},
            'priority': prio,
        }
        pod['limit'] = {
            'cpu': limit_cpu,
            'mem': limit_mem,
            'gpu': limit_gpu,
        }
        pod['request'] = {
            'cpu': request_cpu,
            'mem': request_mem,
            'gpu': request_gpu,
        }

        PODDATA[clock].append(copy.copy(pod))
        print(clock, end = ' ')
        print(PODDATA[clock][-1])

    def resource_config(self, resources):
        result = {}

        cpu = int(resources['cpu'])
        mem = resources['memory']
        mem_suffix = mem[len(mem) - 2:]
        if mem_suffix != 'Gi':
            raise Exception('The unit should be \'Gi\'')
        mem_int = int(mem[: -2])
        gpu = int(resources['nvidia.com/gpu'])

        result['cpu'] = cpu
        result['mem'] = mem_int
        result['gpu'] = gpu

        return result

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    k8s_sim_pb2_grpc.add_simRPCServicer_to_server(
        simRPCServicer(), server)
    server.add_insecure_port('[::]:50052')
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    logging.basicConfig()
    serve()
