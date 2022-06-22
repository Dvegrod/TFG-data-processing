import tensorflow as tf


@tf.function
def action_splitter(observation):
    net_observation = observation[0]
    split = observation[1:]
    return tf.tuple(net_observation, split)