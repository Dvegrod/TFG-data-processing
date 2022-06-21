import numpy as np
import tensorflow as tf
import tf_agents.trajectories
from tf_agents.metrics import tf_metric
from tf_agents.metrics.tf_metrics import TFDeque
import matplotlib.pyplot as plt
import scipy.stats as stats


class RegretOverTimeAnalytics(tf_metric.TFStepMetric):
    """ Stores reward and oracle statistics in order to compute reward metrics. """

    def __init__(self, max_len, name="RegretAnalytics", prefix="Metrics", dtype=tf.dtypes.float32, shape=[1]):
        super(RegretOverTimeAnalytics, self).__init__(name=name, prefix=prefix)
        self.individual_oracle = TFDeque(max_len, dtype, shape=shape)
        self.average_reward = TFDeque(max_len, dtype, shape=shape)
        self.individual_rewards = TFDeque(max_len, dtype, shape=shape)

    def call(self, trajectory: tf_agents.trajectories.Trajectory):
        self.individual_rewards.add(trajectory.reward)
        self.average_reward.add(tf.reduce_mean(trajectory.observation[-1]))
        self.individual_oracle.add(tf.reduce_max(trajectory.observation[-1]))

    def result(self):
        return self.individual_oracle.data - self.individual_rewards.data

    def get_total_regret(self):
        return tf.reduce_sum(self.result())

    def get_graphics(self):
        plt.plot(np.linspace(0, self.individual_rewards.length - 1, self.individual_rewards.length),
                 self.individual_rewards.data)
        plt.plot(np.linspace(0, self.individual_rewards.length - 1, self.individual_rewards.length),
                 self.average_reward.data)
        plt.show()
        plt.plot([tf.reduce_prod(self.individual_rewards.data[0:i] + 1) for i in range(self.individual_rewards.length)])
        plt.plot([tf.reduce_prod(self.average_reward.data[0:i] + 1) for i in range(self.individual_rewards.length)])
        plt.show()

    def reset(self):
        self.individual_oracle.clear()
        self.individual_rewards.clear()

    def roi(self):
        return tf.reduce_prod(self.individual_rewards.data + tf.ones(self.individual_rewards.data.shape, dtype=tf.dtypes.float32))

    def avg_roi(self):
        return tf.reduce_prod(self.average_reward.data + tf.ones(self.individual_rewards.data.shape, dtype=tf.dtypes.float32))


class DebuggerMetric(tf_metric.TFStepMetric):
    """Used to trace the performance of the model whilst working"""

    def __init__(self, max_len, name="RegretAnalytics", prefix="Metrics", dtype=tf.dtypes.float32):
        super(DebuggerMetric, self).__init__(name=name, prefix=prefix)
        self.means = TFDeque(max_len, dtype, shape=[1000])
        self.stdevs = TFDeque(max_len, dtype, shape=[1000])
        self.samples = TFDeque(max_len, dtype, shape=[1000])
        self.action = TFDeque(max_len, tf.dtypes.int32, shape=[1])
        self.oracle = TFDeque(max_len, tf.dtypes.int64, shape=[1])
        self.rewards = TFDeque(max_len, tf.dtypes.float32, shape=[1001, 1])
        self.max_len = max_len

    def call(self, trajectory: tf_agents.trajectories.Trajectory):
        self.means.add(trajectory.policy_info[0])
        self.stdevs.add(trajectory.policy_info[1])
        self.samples.add(trajectory.policy_info[2])
        self.action.add(trajectory.action[0])
        self.oracle.add(tf.argmax(trajectory.observation[-1]))
        self.rewards.add(trajectory.observation[-1])
        print(tf.reduce_max(trajectory.observation[-1]))

    def result(self):
        for i in range(self.means.length):
            means = self.means.data[i]
            stdevs = self.stdevs.data[i]
            samples = self.samples.data[i]
            action = self.action.data[i][0]
            oracle = self.oracle.data[i][0]
            rewards = tf.squeeze(self.rewards.data[i])
            X = tf.linspace(tf.constant(-1.), tf.constant(1.), tf.constant(300))
            plt.plot(X, stats.norm(means[action], stdevs[action]).pdf(X), c="blue")
            plt.plot(X, stats.norm(means[oracle], stdevs[oracle]).pdf(X), c="yellow")
            plt.axvline(samples[action], c="blue")
            plt.axvline(samples[oracle], c="yellow")
            plt.title("Azul bandido, amarillo oráculo.")
            plt.figtext(0.5, 0.02, f"Samples: Action: {samples[action]} Oracle: {samples[oracle]}")
            plt.figtext(0.5, 0.04, f"Returns: Action: {rewards[action]} Oracle: {rewards[oracle]}")
            plt.show()
