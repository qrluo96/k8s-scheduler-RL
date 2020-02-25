from gym.envs.registration import register

register(
    id='k8s-v0',
    entry_point='gym_k8s.envs:K8sEnv',
)
# register(
#     id='foo-extrahard-v0',
#     entry_point='gym_foo.envs:FooExtraHardEnv',
# )