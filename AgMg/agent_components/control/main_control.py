import tensorflow as tf
import tf_agents as tfa
import tf_agents.trajectories as traj
import numpy as np
import tf_agents.metrics.tf_metrics as tf_metrics
import datastruct
import policy as pol
import environment as env
from control_vars import *

#SEED
#tf.random.set_seed(1)

N_STEPS = 4000
N_ARMS = 1000

# Action splitter, needed because arms may close
@tf.function
def action_splitter(observation):
    net_observation = observation[0]
    split = observation[1:]
    return tf.tuple(net_observation, split)

# Get selected files whose arm codes are in the candidates.npy document
file_list = np.load("../../pruebas/modelo_experimental_A/candidates.npy")
file_list = ["../../pruebas/modelo_experimental_A/arms3/" + str(i) + ".csv" for i in file_list]
data = datastruct.read_data(file_list, N_ARMS)

environment = env.ControlEnvironment(N_ARMS, timestep_spec, action_spec, 1, data)


@tf.function
def optimal(observation):
    return tf.reduce_max(observation[-1])


# METRICS
hist = tf_metrics.ChosenActionHistogram(dtype=tf.dtypes.int32, buffer_size=N_STEPS)
env_steps = tf_metrics.EnvironmentSteps()
epi_length = tf_metrics.AverageEpisodeLengthMetric()
ave_return = tf_metrics.AverageReturnMetric()
regret = tfa.bandits.metrics.tf_metrics.RegretMetric(optimal)
from src.metrics import RegretOverTimeAnalytics, DebuggerMetric
regret = RegretOverTimeAnalytics(N_STEPS)
debug = DebuggerMetric(N_STEPS)
observers = [hist, regret, debug]



graphs = []
ban = []
for i in range(50):
    data = datastruct.read_data(file_list, N_ARMS)
    environment.data = iter(data)
    policy = pol.ControlPolicy(context_dims, K, timestep_spec, action_spec,
                               observation_and_action_constraint_splitter=action_splitter,
                               policy_state_spec=policy_spec, info_spec=info_spec, automatic_state_reset=False)
    driver = tfa.drivers.dynamic_step_driver.DynamicStepDriver(environment, policy, observers=observers, num_steps=4000)
    driver.run(environment.reset())
    ban.append(regret.roi())
    graphs.append(regret)
    observers.remove(regret)
    regret = RegretOverTimeAnalytics(N_STEPS)
    observers.append(regret)

print(sum(ban))
