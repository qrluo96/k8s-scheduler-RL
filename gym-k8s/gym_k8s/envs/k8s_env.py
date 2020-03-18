import gym
import threading
from gym import error, spaces, utils
from gym.utils import seeding

import gym_k8s.envs.server as server
import gym_k8s.envs.client as client

class K8sEnv(gym.Env):
#   metadata = {'render.modes': ['human']}
    _threads = []
    _client_thread = None

    def __init__(self):
        
        self._start_sim()

    def step(self, action):
        ...

    def reset(self):
        self._stop_sim()
        self._start_sim()

#   def render(self, mode='human'):
#     ...

    def close(self):
        self._stop_sim()
        self._clear_threads()

    def _start_sim(self):
        _start_server(self)
        self._client_thread = _start_client(self)

    def _stop_sim(self):
        for t in self._threads:
            t.stop()

    def _start_server(self):
        serve_thread = server.ServeThread()
        serve_thread.start()
        self._threads.append(serve_thread)

    def _start_client(self):
        client_thread = client.ClientThread()
        client_thread.start()
        self._threads.append(client_thread)

        return client_thread
    
    def _clear_threads(self):
        for t in self._threads:
            t.join()
        
        print("all exited")
        
