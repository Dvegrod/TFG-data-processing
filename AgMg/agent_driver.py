import tensorflow as tf
import tf_agents as tfa


class AgentDriver(tfa.drivers.driver.Driver):
    def __init__(self, env, policy, command_register, observers=None, transition_observers=None):
        super().__init__(env, policy, observers, transition_observers)
        self.command_register = command_register
        self.episode_end = False
        self.result_observers = []

    def add_result_observers(self, obs):
        self.result_observers.append(obs)

    def run(self, seed=0, first_observation=None):
        iteration = 0
        episode_last = False
        observation = first_observation if first_observation is not None else self.env.reset()
        policy_state = self._policy._get_initial_state(batch_size=1)
        # In order to advance the following conditions have to be met
        #  1. The active command is START or STEP
        #  2. The agent did not reach the end of the episode
        while (self.command_register['started'] and not self.episode_end):
            action = self._policy.action(observation, policy_state, seed)
            if episode_last:
                self.episode_end = True
            else:
                observation = self._env.step(action[0])
            for obs in self.result_observers:
                obs.call(iteration, action, observation.reward)
            if observation.step_type == tf.constant(tfa.trajectories.time_step.StepType.LAST):
                episode_last = True
            iteration += 1
