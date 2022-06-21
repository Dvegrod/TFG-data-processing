import tensorflow as tf
import tf_agents as tfa
import numpy as np
import datastruct
import observation
import tf_agents.trajectories as traj

K = 4000
context_dim = 10
num_models = 1

time_spec = traj.time_step.time_step_spec(observation_spec=tf.tuple([tfa.specs.BoundedTensorSpec([K])]),
                                          reward_spec=tfa.specs.TensorSpec([K], dtype=tf.dtypes.float32))

# 0 means taking the action of doing nothing
action_spec = tfa.specs.BoundedTensorSpec([], dtype=tf.dtypes.int32,
                                          minimum=tf.constant(0), maximum=tf.constant(K + 1))

# Action splitter, needed because arms may close
@tf.function
def action_splitter(observation):
    net_observation = observation[0]
    split = observation[1]
    return (net_observation, split)

# VARIABLE COLLECTION
vc = tfa.bandits.agents.linear_bandit_agent.LinearBanditVariableCollection(context_dim, num_models)

bandit = tfa.bandits.agents.linear_thompson_sampling_agent.LinearThompsonSamplingAgent(time_spec, action_spec, vc,
                                                                                 observation_and_action_constraint_splitter=None,
                                                                                 debug_summaries=True)


# Get selected files whose arm codes are in the candidates.npy document
file_list = np.load("../../pruebas/modelo_experimental_A/candidates.npy")
file_list = ["../../pruebas/modelo_experimental_A/arms3/" + str(i) + ".csv" for i in file_list]
data = datastruct.read_data(file_list, 1000)

for i in range(4000):
    obs = observation.observationAssembler(data, 0.975, 2, 10)
    bandit.train(obs)