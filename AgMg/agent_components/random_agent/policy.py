import tensorflow as tf
import tf_agents as tfa
import tensorflow_probability as tfp


class RandomPolicy(tfa.policies.TFPolicy):

    def __init__(self, context_dims, arms, time_step_spec, action_spec, policy_state_spec=(), info_spec=(), clip=True,
                 emit_log_probability=False, automatic_state_reset=True,
                 observation_and_action_constraint_splitter=None, validate_args=True, name=None):
        super().__init__(time_step_spec, action_spec, policy_state_spec=policy_state_spec, info_spec=info_spec,
                         clip=clip, emit_log_probability=emit_log_probability,
                         automatic_state_reset=automatic_state_reset,
                         observation_and_action_constraint_splitter=observation_and_action_constraint_splitter,
                         validate_args=validate_args, name=name)
        self.arms = arms

    def _action(self, time_step: tfa.trajectories.TimeStep, policy_state, seed):
        # Return
        action = tf.random.uniform(shape=(), minval=0, maxval=1001, dtype=tf.dtypes.int32)
        void = tf.zeros([self.arms])
        # Set state
        action_step = tfa.trajectories.PolicyStep(tf.expand_dims(action, axis=0), tf.expand_dims(action, axis=0),
                                              tf.tuple([void, void, void]))
        return action_step


    def _get_initial_state(self, batch_size: int):
        return tf.zeros([batch_size], dtype=tf.dtypes.int32)
