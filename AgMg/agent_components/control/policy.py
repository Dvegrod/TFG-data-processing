import tensorflow as tf
import tf_agents as tfa
import tensorflow_probability as tfp


class ControlPolicy(tfa.policies.TFPolicy):

    def __init__(self, context_dims, arms, time_step_spec, action_spec, policy_state_spec=(), info_spec=(), clip=True,
                 emit_log_probability=False, automatic_state_reset=True,
                 observation_and_action_constraint_splitter=None, validate_args=True, name=None):
        super().__init__(time_step_spec, action_spec, policy_state_spec=policy_state_spec, info_spec=info_spec,
                         clip=clip, emit_log_probability=emit_log_probability,
                         automatic_state_reset=automatic_state_reset,
                         observation_and_action_constraint_splitter=observation_and_action_constraint_splitter,
                         validate_args=validate_args, name=name)
        self.nu = tf.zeros([arms], dtype=tf.dtypes.float32)
        self.arms = arms
        self.number_of_plays = tf.ones([arms], dtype=tf.dtypes.float32)

    def _update(self, policy_state, time_step):
        # Update
        self.number_of_plays += 1
        self.nu = self.nu / self.number_of_plays * (
            self.number_of_plays - 1) + tf.squeeze(time_step.observation[0])[0:-1] / self.number_of_plays

    def _action(self, time_step: tfa.trajectories.TimeStep, policy_state, seed):
        self._update(policy_state, time_step)
        stdevs = 1 / (self.number_of_plays + 1)
        dists = tfp.distributions.Normal(self.nu, stdevs)
        # Return
        samples = dists.sample([], seed)
        action = tf.argmax(samples, output_type=tf.dtypes.int32)
        # Set state
        action_step = tfa.trajectories.PolicyStep(tf.expand_dims(action, axis=0), tf.expand_dims(action, axis=0),
                                              tf.tuple([self.nu, stdevs, samples]))
        return action_step


    def _get_initial_state(self, batch_size: int):
        return tf.zeros([batch_size], dtype=tf.dtypes.int32)
