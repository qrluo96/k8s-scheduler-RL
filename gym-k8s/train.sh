git fetch --all
git reset --hard origin/master


python -m baselines.run --alg=ppo2 --env=gym_k8s:k8s-v0 --network=mlp --num_timesteps=1e7 --num_hidden=256 --num_layers=4 --save_path=~/models/k8s_4_256_1e7_ppo2
