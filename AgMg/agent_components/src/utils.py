import tensorflow as tf

def ordered_intersection(a : tf.Tensor, b : tf.Tensor):
    # a_pointer = tf.Variable([0])
    # b_pointer = tf.Variable([0])
    # a_limit = a.shape[0]
    # b_limit = b.shape[0]
    # first = tf.constant(False)
    # while a_pointer < a_limit and b_pointer < b_limit:
    #     a_elem = tf.gather(a, a_pointer)
    #     b_elem = tf.gather(b, b_pointer)
    #     if a_elem == b_elem:
    #         a_pointer.assign_add([1])
    #         b_pointer.assign_add([1])
    #         o
    #     else:
    pass

# @tf.function
def index_boolean_intersection_to_index(index, boolean):
    """Receives:
        index : a [n,1] shaped, integer tensor
        boolean : a [k,1] shaped numeric tensor (where 1 means true and everything else false)
        Where n < k and k is the number of arms
       Returns:
        A [m] shaped, int32 tensor
        Where m < k.
       Does:
        Given a list of indexes and a mask of bools, it returns a list of indexes which are present in the previous one
        and have a 1 in the position given by said index in the boolean tensor.
    """
    index = index.to_tensor(shape=(None, 1))
    print(f"Index: {index.shape}, Boolean: {boolean.shape}")
    inter = tf.zeros(boolean.shape, dtype=tf.dtypes.int32)
    inter = tf.tensor_scatter_nd_update(inter, index, tf.ones([index.shape[0], 1], dtype=tf.dtypes.int32))
    inter = tf.einsum('j,j -> j', tf.squeeze(inter), tf.cast(tf.squeeze(boolean), dtype=tf.dtypes.int32))
    return tf.where(inter)