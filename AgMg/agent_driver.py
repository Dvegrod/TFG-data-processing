import tensorflow as tf
import tf_agents as tfa


class AgentDriver(tfa.drivers.driver.Driver):
    def __init__(self, env, policy, command_register, observers=None, transition_observers=None):
        super.__init__(env, policy, observers, transition_observers)
        self.command_register = command_register

    def run(self, first_observation, seed):
        episode_end = False
        episode_last = False
        observation = first_observation
        policy_state = self._policy._get_initial_state(batch_size=1)
        # In order to advance the following conditions have to be met
        #  1. The active command is START or STEP
        #  2. The agent did not reach the end of the episode
        while (self.command_register['started'] and not episode_end):
            action = self._policy.action(observation, policy_state, seed)
            if episode_last:
                episode_end = True
            else:
                observation = self._env.step(action)
            if observation.step_type == tf.constant(tfa.trajectories.time_step.StepType.LAST):
                episode_last = True
