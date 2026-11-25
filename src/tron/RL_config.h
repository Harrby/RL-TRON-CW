#ifndef RL_CONFIG_H
#define RL_CONFIG_H 

#include "defs.h"
#include <chrono>
#include <iostream>
#include <thread>

#include <sys/socket.h>
#include <netinet/in.h>
#include <unistd.h>
#include <cstring>
#include <signal.h>
#include <arpa/inet.h>

#define PI 3.14159265358979323846 


// Constants
namespace RLConfig {
    const float RAY_SIZE = 50.0;     // The length of the raycast sensors for the agent
    const int N_RAYS = 5;            // The number of raycast sensors used.
    const float FAN_ANGLE = PI/2.;    // The range the sensors will be distributed at.
    
    const int PORT = 9999;
    const char* const IP_ADDR = "127.0.0.1";
    const REAL TRANSITION_RATE = 100.0; // transitions per second., change this if its running too slow / too fast based on the size of the model.
}


int send_message(const char* msg);




#endif