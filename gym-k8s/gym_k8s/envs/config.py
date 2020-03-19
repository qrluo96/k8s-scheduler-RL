import yaml

def read_config(path):
    with open(path, 'r') as stream:
        try:
            yaml_data = yaml.load(stream)
            return yaml_data
        except yaml.YAMLError as exc:
            print(exc)

if __name__ == "__main__":
    path = "./config.yaml"

    yaml_data = read_config(path)

    cluster_data = yaml_data["cluster"]

    node_resource = {}
    for node_data in cluster_data:
        node_name = node_data["metadata"]["name"]
        node_resource[node_name] = node_data["status"]["allocatable"]

    print(node_resource)