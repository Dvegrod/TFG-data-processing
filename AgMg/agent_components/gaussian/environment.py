import tensorflow as tf
import tf_agents as tfa
import tf_agents.environments.tf_environment as tfenv

class Environment(tfenv.TFEnvironment):
    """."""
    def __init__(self, arms, time_step_spec=None, action_spec=None, batch_size=1, data=None, ctx_dim=10, alpha=0.965, beta=2):
        super().__init__(time_step_spec=time_step_spec, action_spec=action_spec, batch_size=batch_size)
        self.data = data.__iter__()
        next = self.data.next()
        self.stacked_data = tf.transpose(
            tf.cast(tf.stack([next["enabled"], next["reward"], next["float8"]]), dtype=tf.dtypes.float32))
        self.n_step = 0
        self.K = arms

    def _step(self, action):
        # Build a Time Step
        print(f"(CONTROL) STEP {self.n_step}")
        self.n_step += 1
        raw = tf.concat([self.stacked_data, tf.constant([[1., 0., 0.]])], axis=0)
        raw = tf.reshape(raw, [self.K + 1, 3])
        # Unpack information
        availability = tf.gather(raw, [0], axis=1)
        rewards = tf.gather(raw, [1], axis=1)
        volume = tf.gather(raw, [2], axis=1)

        try:
            ts = tfa.trajectories.TimeStep(
                step_type=tf.constant(tfa.trajectories.time_step.StepType.MID),
                observation=tf.tuple([availability, rewards]),
                reward=rewards[action[0]],
                discount=tf.constant(1.)
            )
            next = self.data.next()
            self.stacked_data = tf.transpose(
                tf.cast(tf.stack([next["enabled"], next["reward"], next["float8"]]), dtype=tf.dtypes.float32))
        except Exception:
            ts = tfa.trajectories.TimeStep(
                step_type=tf.constant(tfa.trajectories.time_step.StepType.LAST),
                observation=tf.tuple([availability, rewards]),
                reward=rewards[action[0]],
                discount=tf.constant(1.)
            )
        return ts

    def _reset(self):
        self.data = self.data.__iter__()
        next = self.data.next()
        stacked_data = tf.transpose(tf.cast(tf.stack([next["enabled"], next["reward"], next["float8"]]), dtype=tf.dtypes.float32))
        raw = tf.concat([stacked_data, tf.constant([[1., 0., 0.]])], axis=0)
        raw = tf.reshape(raw, [self.K + 1, 3])
        # Unpack information
        availability = tf.gather(raw, [0], axis=1)
        rewards = tf.gather(raw, [1], axis=1)
        volume = tf.gather(raw, [2], axis=1)
        next = self.data.next()
        self.stacked_data = tf.transpose(
            tf.cast(tf.stack([next["enabled"], next["reward"], next["float8"]]), dtype=tf.dtypes.float32))
        return tfa.trajectories.TimeStep(
            step_type=tf.constant(tfa.trajectories.time_step.StepType.FIRST),
            observation=tf.tuple([rewards, availability]),
            reward=tf.constant([0.]),
            discount=tf.constant(1.)
        )

    def _current_time_step(self):
        return super()._current_time_step()
