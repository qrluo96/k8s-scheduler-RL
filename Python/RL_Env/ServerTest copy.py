from concurrent import futures
import copy
import json
import logging
import threading
import time

import grpc

import k8s_sim_pb2
import k8s_sim_pb2_grpc

class simRPCServicer(k8s_sim_pb2_grpc.simRPCServicer):
    def RecordMetrics(self, request, context):
        metrics = request
        clock = metrics.clock.clock_metrics_Key
        node = metrics.nodes.nodes_metrics_key
        pods = metrics.pods.pods_metrics_key
        queue = metrics.queue.queue_metrics_key

        print(clock)
        print(node)
        print(pods)
        print(queue)

        return k8s_sim_pb2.Result(result="1")

    def RecordFormattedMetrics(self, request, context):
        metric = request.formatted_metrics

        formattedMetrics = json.loads(metric)
        print("Formatted metrics: ", end = '')
        print(formattedMetrics)

        return k8s_sim_pb2.Result(result="1")
    
    def RecordPodMetrics(self, request, context):
        Metric = request.pod_metrics

        formattedMetrics = json.loads(Metric)
        # print(formattedMetrics)

        clock = formattedMetrics['Clock']
        print('Clock: ', end = '')
        print(clock)
        podMetrics = formattedMetrics['Pods']
        containers = podMetrics['spec']['containers']

        containersResources = []
        for container in containers:
            formattedContainer = {}
            formattedContainer['name'] = container['name']
            formattedContainer['image'] = container['image']
            formattedContainer['resource'] = container['resources']
            print('Formattede container: ', end = '')
            print(formattedContainer)
            containersResources.append(formattedContainer)

        return k8s_sim_pb2.Result(result="1")

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    k8s_sim_pb2_grpc.add_simRPCServicer_to_server(
        simRPCServicer(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()
            
if __name__ == '__main__':
    serve()

    
