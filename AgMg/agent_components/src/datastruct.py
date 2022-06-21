
import tensorflow as tf


def preprocess(line):
    defs = [0.] * 3
    fields = tf.io.decode_csv(line, defs, select_cols=[2, 3, 4])
    fields = tf.stack(fields)
    return fields


def read_data(filepaths, arms):
    files = tf.data.Dataset.list_files(filepaths, shuffle=False)
    dataset = files.interleave(
        (lambda path: tf.data.TextLineDataset(path).skip(15763)),
        cycle_length=arms, num_parallel_calls=tf.data.AUTOTUNE)
    dataset = dataset.map(preprocess, num_parallel_calls=tf.data.AUTOTUNE)
    return dataset.batch(arms).prefetch(1)
