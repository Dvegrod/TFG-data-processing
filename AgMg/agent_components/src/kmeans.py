import tensorflow as tf
from src.utils import index_boolean_intersection_to_index

class ArmKMeans:
    """ Important things to note:
          - Usually sample_vector refers to a reward vector, that is, the rewards of all arms in a specific instant.
          - Not actually kmeans
        Attributes and their meanings:
          - Y: ([m, k] shaped tensor) see dissertation.
          - m: (integer) number of groups.
          - alpha: (float32) a parameter used to discount value to knowledge obtained in previous iterations
    """

    def __init__(self, groups, initial_sample_vector, alpha=tf.constant(0.965, dtype=tf.dtypes.float64), center_calibrations_per_iteration=tf.constant(1)):
        # Construct X
        R = tf.squeeze(tf.repeat(tf.expand_dims(initial_sample_vector, 0), initial_sample_vector.shape[0], 0))
        X = tf.math.abs(tf.subtract(R, tf.transpose(R)))
        # Construct Y
        choices = tf.random.uniform_candidate_sampler(tf.expand_dims(tf.range(0, initial_sample_vector.shape[0], dtype=tf.dtypes.int64), 0),
                                                      initial_sample_vector.shape[0], groups, True, initial_sample_vector.shape[0])
        self.Y = tf.gather(X, tf.cast(choices.sampled_candidates, dtype=tf.int32))
        # Save number of groups
        self.m = groups
        # Generate groups
        self._group_elements_by_distance()
        # Reset Y since the first centers can now be calculated
        self.Y = tf.zeros((groups, initial_sample_vector.shape[0]), dtype=tf.dtypes.float32)
        # Save other params
        self.alpha = alpha
        self.beta = center_calibrations_per_iteration
        # Centers
        self.centers = tf.random.stateless_normal([groups], tf.constant([1, 1]), mean=0.0, stddev=0.2, dtype=tf.dtypes.float32)
        # Empty, a [0,1] shape is needed at first
        self.empty = tf.transpose(tf.constant([[]], dtype=tf.dtypes.int32))

    def _group_elements_by_distance(self):
        # Classify arms
        results = tf.argmin(self.Y, output_type=tf.dtypes.int32)
        # Gather groups
        self.groups = tf.map_fn((lambda idx: tf.RaggedTensor.from_tensor(
            tf.cast(tf.where(tf.equal(results, idx)), dtype=tf.dtypes.int32))),
                                tf.range(0, self.m), parallel_iterations=True,
                                fn_output_signature=tf.RaggedTensorSpec((None, 1), tf.dtypes.int32))
        print(self.groups.row_splits)
        self.empty = tf.where(tf.map_fn((lambda c: 1 if c.shape[0] == 0 else 0), self.groups, fn_output_signature=tf.TensorSpec([], dtype=tf.dtypes.int32)))

    def _calculate_centers(self, sample_vector, enabled):
        """Receives:
            Sample vector: a [k] shaped, float32 tensor
            Enabled: a [k] shaped, float32 tensor
            Where k is the number of arms
           Returns:
            Nothing
           Does:
            Reduce reward values from k to m.
        """
        temp = tf.map_fn((lambda grp: tf.reduce_mean(tf.gather(sample_vector, index_boolean_intersection_to_index(grp, enabled)))), self.groups, fn_output_signature=tf.TensorSpec((), tf.dtypes.float32), name="CACA")
        # In case of nan (empty group) the value of the center will be sustained
        self.centers = tf.where(tf.math.is_nan(temp), self.centers, temp)

    def _calculate_Y(self, sample_vector, enabled):
        """Receives:
            Sample vector: a [k] shaped, float32 tensor
            Enabled: a [k] shaped, float32 tensor
            Where k is the number of arms
           Returns:
            Nothing
           Does:
            .
        """
        # print(f"{sample_vector.dtype} {enabled.dtype}")
        backup = tf.transpose(tf.identity(self.Y))
        # Normal operation
        self.Y = tf.add((self.alpha * self.Y), tf.math.abs(tf.subtract(tf.squeeze(tf.repeat(tf.expand_dims(sample_vector, 0), self.m, 0)), tf.expand_dims(self.centers, 1))))
        # The following is needed to compute the values for the closed arms
        temp = tf.transpose(self.Y)
        tf.tensor_scatter_nd_update(temp, tf.where(tf.squeeze(enabled - 1)), tf.squeeze((tf.gather(backup, tf.where(tf.squeeze(enabled) - 1), axis=0))))
        # The following is needed to split groups when there are empty ones
        temp = tf.transpose(temp)
        # Getting the biggest group (there is junk after the first element of the result)
        biggest_group = tf.argmax(tf.map_fn((lambda g: g.shape), self.groups, fn_output_signature=tf.TensorSpec([None], dtype=tf.dtypes.int32)))
        # Repeating index as many times as empty groups
        indexes = tf.repeat(biggest_group[0], self.empty.shape[0])
        print(f"Index: {indexes} Empty {self.empty}")
        # print(f"DET: {tf.reduce_sum(self.Y)}")
        print(temp.shape)
        temp = tf.tensor_scatter_nd_update(temp, self.empty, tf.gather(temp, indexes) * tf.random.stateless_normal([temp.shape[1]], tf.constant([1, 1]), mean=1., stddev=0.03, dtype=tf.dtypes.float32))
        self.Y = temp

    def iterate(self, sample_vector, enabled):
        # Apply averages to disabled arms
        for _ in range(self.beta):
            self._calculate_centers(sample_vector, enabled)
            self._calculate_Y(sample_vector, enabled)
            self._group_elements_by_distance()

    def get_group(self, i):
        return self.groups[i]
