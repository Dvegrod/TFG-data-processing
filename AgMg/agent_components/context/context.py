import kmeans
import tensorflow as tf


class RewardSimilarityContextProvider():
    def __init__(self, alpha, beta, groups):
        self.alpha = alpha
        self.beta = beta
        self.ngroups = groups
        self.kmeans = None
        self.context_vector = None

    def get_context(self):
        if self.kmeans is None:
            raise AttributeError("There was no first update.")
        else:
            t = tf.linalg.normalize(self.context_vector)[0]
            if tf.math.reduce_any(tf.math.is_nan(t)):
                return tf.zeros()
            else:
                return t


    def update_context(self, reward_vector, value_vector, available):
        if self.kmeans is None:
            # Initialize
            self.kmeans = kmeans.ArmKMeans(self.ngroups, reward_vector, self.alpha, self.beta)
        else:
            self.kmeans.iterate(reward_vector, available)
        new_context = tf.zeros(self.ngroups)
        for i in tf.range(self.ngroups):
            group = self.kmeans.get_group(i)
            # The mean of the rewards in a group gets computed TODO redundant
            if group.shape[0] < 1:
                continue
            tf.tensor_scatter_nd_update(new_context, tf.reshape(i, [1, 1]), tf.expand_dims(tf.reduce_mean(tf.gather(value_vector, group)), axis=0))
        self.context_vector = new_context

from sklearn.cluster import KMeans
import numpy as np

class RewardSimilarityContextProviderB():
    def __init__(self, alpha, beta, groups):
        self.alpha = alpha
        self.beta = beta
        self.ngroups = groups
        self.kmeans = None
        self.context_vector = None
        self.X = None

    def get_context(self):
        if self.kmeans is None:
            raise AttributeError("There was no first update.")
        else:
            t = tf.linalg.normalize(self.context_vector)[0]
            if tf.math.reduce_any(tf.math.is_nan(t)):
                return tf.zeros(self.ngroups)
            else:
                return t

    def update_context(self, reward_vector, value_vector, available):
        self.kmeans = KMeans(self.ngroups, random_state=10)
        if self.X is None:
            self.X = np.expand_dims(reward_vector.numpy(), axis=0)
        else:
            self.X = np.concatenate([self.X, np.expand_dims(reward_vector.numpy(), axis=0)])

        self.kmeans.fit_predict(np.transpose(np.squeeze(self.X, axis=-1)))
        new_context = tf.zeros(self.ngroups)
        for i in tf.range(self.ngroups):
            group = tf.where(tf.constant(self.kmeans.labels_) == i)
            # The mean of the rewards in a group gets computed TODO redundant
            if group.shape[0] < 1:
                continue
            new_context = tf.tensor_scatter_nd_update(new_context, tf.reshape(i, [1, 1]), tf.expand_dims(tf.reduce_mean(tf.gather(value_vector, group)), axis=0))
        self.context_vector = new_context
