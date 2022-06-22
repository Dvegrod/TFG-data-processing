import tensorflow as tf
import context as ctx

class observationAssembler():
    def __init__(self, data, alpha, beta, groups):
        self.data = iter(data)
        self.provider = ctx.RewardSimilarityContextProvider(alpha, beta, groups)

    def get_observation(self):
        raw = self.data.next()
        raw = tf.gather(raw, [0], axis=tf.constant(0))
        availability = tf.concat([raw, tf.constant(1.0)], axis=0)
        rewards = tf.gather(raw, [1], axis=tf.constant(0))
        context = self.provider.update_context(rewards, rewards)
        return [context, availability]