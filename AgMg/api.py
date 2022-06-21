
import os
import signal
from fastapi import FastAPI
import subprocess

app = FastAPI()

# Key: experiment id Value: process
active_experiments = {}
# Key: experiment id Value: supossed status
orders_sent = {}


@app.get("/start/{experiment_id}")
def start_experiment(experiment_id : int):
    print(f"RECEIVED: START {experiment_id}")
    if experiment_id in active_experiments:
        print(f"CURRENT STATE {orders_sent[experiment_id]}")
        # Send signal
        # IF STOPPED
        if orders_sent[experiment_id] == 0:
            active_experiments[experiment_id].send_signal(signal.SIGUSR1)
            orders_sent[experiment_id] = 1
    else:
        print(f"INITIALIZING {experiment_id}")
        # Create process for experiment
        active_experiments[experiment_id] = subprocess.Popen(["python3", "./agent_runner.py", f"{experiment_id}"])
        orders_sent[experiment_id] = 1


@app.get("/stop/{experiment_id}")
def stop_experiment(experiment_id : int):
    print(f"RECEIVED: STOP {experiment_id}")
    if experiment_id in active_experiments:
        # Send signal
        if orders_sent[experiment_id] == 1:
            active_experiments[experiment_id].send_signal(signal.SIGUSR1)
            orders_sent[experiment_id] = 0


@app.get("/step/{experiment_id}")
def step_experiment(experiment_id : int):
    print(f"RECEIVED: STEP {experiment_id}")
    if experiment_id in active_experiments:
        # Send signal
        active_experiments[experiment_id].send_signal(signal.SIGUSR2)
    else:
        # Create process for experiment
        active_experiments[experiment_id] = subprocess.Popen(["python3", "./agent_runner.py", f"{experiment_id}"])