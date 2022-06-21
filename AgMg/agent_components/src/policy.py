import tensorflow as tf
import tf_agents as tfa
import tensorflow_probability as tfp


class StockMarketPolicy(tfa.policies.TFPolicy):
    """"""

    def __init__(self, context_dims, arms, time_step_spec, action_spec, policy_state_spec=(), info_spec=(), clip=True,
                 emit_log_probability=False, automatic_state_reset=True,
                 observation_and_action_constraint_splitter=None, validate_args=True, name=None):
        super().__init__(time_step_spec, action_spec, policy_state_spec=policy_state_spec, info_spec=info_spec,
                         clip=clip, emit_log_probability=emit_log_probability,
                         automatic_state_reset=automatic_state_reset,
                         observation_and_action_constraint_splitter=observation_and_action_constraint_splitter,
                         validate_args=validate_args, name=name)
        self.B = tf.eye(context_dims, batch_shape=[arms])
        self.B = tf.eye(context_dims)
        self.nu = tf.zeros([arms, context_dims])
        self.f = tf.zeros([arms, context_dims])
        self.context_dims = context_dims
        self.eps = 0.5
        self.lam = 0.5
        self.arms = arms

    def _update(self, observation):
        for ac in tf.range(self.arms):
            action = tf.expand_dims(ac, axis=0)
            b_a = observation[1]
            # B_a = tf.squeeze(tf.gather(self.B, action))
            # B_a = B_a + tf.einsum('i,j -> ij', b_a, b_a)
            self.B = self.B + tf.einsum('i,j -> ij', b_a, b_a)
            f_a = tf.gather(self.f, action)
            f_a = f_a + b_a * observation[-1][action[0]]
            nu_a = tf.linalg.cholesky_solve(self.B, tf.transpose(f_a))
            # SCATTER
            # self.B = tf.tensor_scatter_nd_update(self.B, [action], [B_a])
            self.f = tf.tensor_scatter_nd_update(self.f, [action], f_a)
            self.nu = tf.tensor_scatter_nd_update(self.nu, [action], tf.transpose(nu_a))
        #

    def _action(self, time_step: tfa.trajectories.TimeStep, policy_state, seed):
        # Extract observation
        observation = tf.expand_dims(time_step.observation[1], axis=1)
        # Update the policy using the reward values of the previous iteration
        # TODO pruebas deshabilitar cuando accion es 0
        self._update(time_step.observation)
        # Fill distributions
        # TODO
        v = 0.8 * tf.math.sqrt(24 / self.eps * self.context_dims * tf.math.log(1 / self.lam))
        means = tf.vectorized_map((lambda nu: tf.einsum('i,ij->', nu, observation)), self.nu)
        # stdevs = tf.vectorized_map((lambda arm_B: tf.einsum('ij,ij->', observation, tf.linalg.cholesky_solve(arm_B, observation)) * v), self.B)
        stdevs = tf.einsum('ij,ij->', observation, tf.linalg.cholesky_solve(self.B, observation)) * v
        dists = tfp.distributions.Normal(means, stdevs)
        #print(means)
        # Return
        samples = dists.sample([], seed)
        action = tf.argmax(samples, output_type=tf.dtypes.int32)
        # Set state
        action_step = tfa.trajectories.PolicyStep(tf.expand_dims(action, axis=0), tf.expand_dims(action, axis=0), tf.tuple([means, stdevs, samples]))
        return action_step

    def _get_initial_state(self, batch_size: int):
        return tf.zeros([batch_size], dtype=tf.dtypes.int32)
