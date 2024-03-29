import threading

import gym_k8s.envs.RLServer as RLServer
import gym_k8s.envs.threading_extender as threading_extender

class ServeThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self, daemon=True)

    def run(self):
        RLServer.serve()

    def stop(self):
        RLServer.restart()
        print("Kill server")

    def restart(self):
        RLServer.restart()