
import tensorflow as tf
import tf_agents as tfa
import tf_agents.environments.tf_environment as tfenv
import context as ctx

class StockMarketDynamics():
    """This is a state machine."""
    def __init__(self, data, arms, context_dim, alpha, beta):
        self.cc = ctx.RewardSimilarityContextProviderB(alpha, beta, context_dim)
        self.data = iter(data)
        self.rew = None
        self.K = arms

    def get_observation(self):
        raw = tf.concat([self.data.next(), tf.constant([[1., 0., 0.]])], axis=0)
        raw = tf.reshape(raw, [self.K + 1, 3])
        # Unpack information
        availability = tf.gather(raw, [0], axis=1)
        rewards = tf.gather(raw, [1], axis=1)
        volume = tf.gather(raw, [2], axis=1)
        # Get groups
        self.cc.update_context(rewards, rewards, availability)
        self.rew = rewards
        return tf.tuple([availability, self.cc.get_context(), self.rew])

    def get_reward(self, action):
        return self.rew[action[0]]


class StockMarketEnvironment(tfenv.TFEnvironment):
    """."""
    def __init__(self, arms, time_step_spec=None, action_spec=None, batch_size=1, data=None, ctx_dim=10, alpha=0.965, beta=2):
        super().__init__(time_step_spec=time_step_spec, action_spec=action_spec, batch_size=batch_size)
        self.data = data
        self.dynamics = StockMarketDynamics(data, arms, ctx_dim, alpha, beta)
        self.n_step = 0

    def _step(self, action):
        # Build a Time Step
        # print(f"STEP {self.n_step}")
        self.n_step += 1
        ts = tfa.trajectories.TimeStep(
            step_type=tf.constant(tfa.trajectories.time_step.StepType.MID),
            observation=self.dynamics.get_observation(),
            reward=self.dynamics.get_reward(action),
            discount=tf.constant(1.)
        )
        return ts

    def _reset(self):
        # Reset by calling dynamics constructor
        self.dynamics = StockMarketDynamics(self.data, 1000, context_dim=10, alpha=tf.constant(0.965), beta=tf.constant(2))
        self.n_step = 0
        return tfa.trajectories.TimeStep(
            step_type=tf.constant(tfa.trajectories.time_step.StepType.FIRST),
            observation=self.dynamics.get_observation(),
            reward=tf.constant([0.]),
            discount=tf.constant(1.)
        )

    def _current_time_step(self):
        return super()._current_time_step()
