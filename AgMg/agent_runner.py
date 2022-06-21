
import agent_driver
import signal
import time
import sys

# Used by the driver to follow commands, a signal handler updates these records
command_register = {
    "experiment_id": sys.argv[1],
    "started": True,
    "current_step": 0,
    "desired_step": 0,
}


# Handles signals sent by AgMg
def signal_handler_startstop(signum, _):
    print(f"<E-{command_register['experiment_id']}> RECEIVED START/STOP")
    command_register['started'] = False if command_register['started'] else True


def signal_handler_step(signum, _):
    print(f"<E-{command_register['experiment_id']}> RECEIVED STEP")
    command_register['desired_step'] += 1


signal.signal(signal.SIGUSR1, signal_handler_startstop)
signal.signal(signal.SIGUSR2, signal_handler_step)

# AGENT VARIABLES AND CLASSES START FROM HERE

environment = 0
policy = 0

if __name__ == "__main__":
    while True:
        time.sleep(1)

#agent_driver.AgentDriver(environment, policy, command_register)