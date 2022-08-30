import tensorflow as tf
import tf_agents as tfa
import tf_agents.trajectories
from tf_agents.metrics.tf_metrics import TFDeque
import asyncio

class ResultUploader:

    def __init__(self, writer):
        self.performance = tf.constant(1.)
        self.writer = writer

    def call(self, iteration, action, reward):
        self.performance = self.performance * (tf.squeeze(reward) + tf.constant(1.))
        self.writer.save_step(iteration, self.performance.numpy(), tf.squeeze(reward).numpy(), action.numpy())
