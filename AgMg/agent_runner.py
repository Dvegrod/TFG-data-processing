
import agent_driver
import agent_builder
import signal
import time
import agent_metrics.result_uploader as result_uploader
import sys
import db_interface

# Used by the driver to follow commands, a signal handler updates these records
command_register = {
    "experiment_id": int(sys.argv[1]),
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

if __name__ == "__main__":
    try:
        # INIT AGENT BUILDER
        builder = agent_builder.AgentBuilder(command_register)
        # START DB SESSION
        reader = db_interface.Reader("172.17.0.2", "testdb", "postgres", "burra")
        # GET DATA
        exp_data = reader.experiment_data(command_register["experiment_id"])
        agent_data = reader.agent_data(exp_data["agent_id"])
        K = reader.number_of_arms(exp_data["edition_id"])
        print(exp_data)
        print(agent_data)
        print(K)
        time.sleep(2)
        dataset = reader.edition(exp_data['edition_id'], K)
        # BUILD AGENT
        builder.add_type('gaussian')
        builder.add_vars({
            "K": K,
            "CONTEXT_DIMS": 0,
            "FRF": agent_data['full_reinforce'],
            "DATA": dataset
        })
        agent = builder.build()
        # WRITER AND METRICS
        write = db_interface.Writer("172.17.0.2", "testdb", "postgres", "burra", exp_data["edition_id"])
        execution_id = write.register_execution(command_register["experiment_id"])
        result_upload = result_uploader.ResultUploader(write)
        agent.add_result_observer(result_upload)

        while True:
            # DRIVER CHECK LOOP
            agent.run()
            if agent.episode_end:
                write.finish_execution(command_register["experiment_id"])
                break
            time.sleep(5)

        print(f"FINISHED EXPERIMENT {command_register['experiment_id']}")
    except Exception:
        print(f"AGENT RUNNER ERROR:  Experiment {command_register['experiment_id']} | Exception {Exception.args[0]}")
        write = db_interface.Writer("172.17.0.3", "testdb", "postgres", "burra", exp_data["edition_id"])
        write.finish_execution(command_register["experiment_id"])
