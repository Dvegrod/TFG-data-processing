import tensorflow as tf
import tf_agents as tfa
import tf_agents.trajectories as traj
import numpy as np
import tf_agents.metrics.tf_metrics as tf_metrics
import agent_components
from agent_components.gaussian.control_vars import *
import agent_driver
from agent_components.action_splitter import action_splitter

class AgentBuilder():
    def __init__(self, command_register):
        self._comm = command_register
        self._agent_module = None
        self.type = None
        self.vars = None
        self.metrics = []

    def add_type(self, ttype : str):
        print("COSA")
        if ttype == "gaussian":
            self._agent_module = agent_components.gaussian
        self.type = ttype

    def add_vars(self, vars : dict):
        if self.type is None:
            raise AttributeError("AgentBuilder.add_vars: The builder did not receive a type yet")
        self.vars = vars

    def add_metrics(self, metrics : list):
        self.metrics.append(metrics)

    def build(self):
        if self.vars is None:
            raise AttributeError("AgentBuilder.build: The builder did not receive parameters yet")
        # Number of arms
        K = self.vars['K']
        context_dims = self.vars['CONTEXT_DIMS'] if self.type == "context" else 0
        frf = self.vars['FRF']

        # SPECS
        observation_spec = tf.tuple(
            [tfa.specs.BoundedTensorSpec([K + 1, 1], dtype=tf.dtypes.float32, minimum=0., maximum=1.),
             tfa.specs.TensorSpec([K + 1, 1], dtype=tf.dtypes.float32)])

        reward_spec = tfa.specs.TensorSpec([1], dtype=tf.dtypes.float32)

        timestep_spec = tfa.trajectories.time_step_spec(observation_spec, reward_spec)

        # 0 means taking the action of doing nothing
        action_spec = tfa.specs.BoundedTensorSpec([1], dtype=tf.dtypes.int32,
                                                  minimum=tf.constant([0]), maximum=tf.constant([K + 1]))
        policy_spec = action_spec

        info_spec = tf.tuple([
            tfa.specs.TensorSpec([K + 1], dtype=tf.dtypes.float32),
            tfa.specs.TensorSpec([K + 1], dtype=tf.dtypes.float32),
            tfa.specs.TensorSpec([K + 1], dtype=tf.dtypes.float32),
        ])

        # DATA
        data = self.vars['DATA']
        # Seed
        #tf.random.set_seed(self.vars['SEED'])

        # ENVIRONMENT
        environment = self._agent_module.Environment(K, timestep_spec, action_spec, 1, data)
        # POLICY
        policy = self._agent_module.Policy(context_dims, frf, K, timestep_spec, action_spec,
                                observation_and_action_constraint_splitter=action_splitter,
                                policy_state_spec=policy_spec, info_spec=info_spec, automatic_state_reset=False)
        # DRIVER
        driver = agent_driver.AgentDriver(environment, policy, command_register=self._comm)

        return driver
