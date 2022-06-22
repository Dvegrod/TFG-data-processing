
import tensorflow as tf
import tf_agents as tfa

K = 1000
context_dims = 10
num_models = 1

# SPECS
observation_spec = tf.tuple([tfa.specs.BoundedTensorSpec([K + 1, 1], dtype=tf.dtypes.float32, minimum=0., maximum=1.),
                             tfa.specs.TensorSpec([K + 1, 1], dtype=tf.dtypes.float32)])

reward_spec = tfa.specs.TensorSpec([1], dtype=tf.dtypes.float32)

timestep_spec = tfa.trajectories.time_step_spec(observation_spec, reward_spec)

# 0 means taking the action of doing nothing
action_spec = tfa.specs.BoundedTensorSpec([1], dtype=tf.dtypes.int32,
                                          minimum=tf.constant([0]), maximum=tf.constant([K + 1]))
policy_spec = action_spec

info_spec = tf.tuple([
    tfa.specs.TensorSpec([K + 1], dtype=tf.dtypes.float32),
    tfa.specs.TensorSpec([K + 1], dtype=tf.dtypes.float32),
    tfa.specs.TensorSpec([K + 1], dtype=tf.dtypes.float32),
])



