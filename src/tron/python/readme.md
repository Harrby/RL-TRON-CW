Python is run using its interpreter, slower than compiled but thats fine, this is way more convenient.

# Setup

(In /python directory)

## Create virtual environment
$ python -m venv .venv 

## Activate virtual environment

LINUX: 
```
source .venv/bin/activate
```
WINDOWS:
```
.venv/Scripts/activate
```

## Install python libraries
Put the libraries you need in requirements.txt, e.g Pytorch.

$ pip install -r requirements.txt


# Information
PORT - is the port the TCP stream uses,  currently 9999. Will need to change this if your device has a program that uses this port already for some reason.

## src/tron/gGame.cpp
This is where the C++ communicates with rl_agent.py lines 3761-3835.

## RL_config.h
Contains adjustable settings for the agent such as the number of rays, and transition-rate which controls how often we skip timesteps when taking transitions (in case the model slows it down too much).