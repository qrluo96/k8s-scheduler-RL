import os
import yaml

def read_config():
    module_path = os.path.abspath(__file__)
    file_dir = os.path.dirname(os.path.dirname(module_path)) + '/config'

    print(
        os.path.dirname(
            os.path.dirname(
                os.path.dirname(
                    os.path.dirname(
                        module_path)))))

    file_path = file_dir + '/config.yaml'

    with open(file_path, 'r') as stream:
        try:
            yaml_data = yaml.load(stream)
            return yaml_data
        except yaml.YAMLError as exc:
            print(exc)

if __name__ == "__main__":
    yaml_data = read_config()

    cluster_data = yaml_data["cluster"]

    node_resource = {}
    for node_data in cluster_data:
        node_name = node_data["metadata"]["name"]
        node_resource[node_name] = node_data["status"]["allocatable"]

    print(node_resource)

    print(node_resource['node-0'])

    cpu = node_resource['node-0']['cpu']
    mem = node_resource['node-0']['memory']
    mem_suffix = mem[len(mem) - 2:]
    if mem_suffix != 'Gi':
        raise Exception('The unit should be \'Gi\'')
    mem_int = int(mem[:-2])
    gpu = node_resource['node-0']['nvidia.com/gpu']
    pod = node_resource['node-0']['pods']

    print(cpu)
    print(type(cpu))
    # print(mem)
    # print(type(mem))
    print(mem_int)
    print(type(mem_int))
    print(gpu)
    print(type(gpu))
    print(pod)
    print(type(pod))
