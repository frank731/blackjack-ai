from blackjack import BlackjackEnv
from stable_baselines3 import A2C
from stable_baselines3.common.env_checker import check_env

env = BlackjackEnv("console")
model = A2C("MlpPolicy", env, verbose=1)
model.learn(total_timesteps=10_000)
check_env(env)