import sys
import socket 
import json
from inital_Q import DoubleQNetwork, DontCrashAgent


# An agent that just turns right if it gets close to a wall
class DumbAgent():
    def __init__(self):
        pass 

    # Action 0: nothing
    # Action 1: left
    # Action 2: right
    def get_action(self, state) -> int:
        if min(state["sensors"]) < 0.6:
            return 2
        else:
            return 0



if __name__ == "__main__":
    model = DontCrashAgent()
    # PORT: 9999
    server = socket.socket()
    # Allow reuse of the address after shutdown to make restarting easier
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind( ("127.0.0.1", 9999)) # > 1024 is safe
    server.listen()

    #---------- Load in model --------------
    model = DontCrashAgent()


    transitions = [] ; max_transition_size = 20
    i=0 
    while True:
        
        client, addr = server.accept()
        with client: # with client ensures connection closes
            msg:str = client.recv(4096).decode("utf-8")
            if msg == "EXIT": # Kill the process
                client.send("EXIT MESSAGE RECEIVED".encode("utf-8"))
                break
            else:
                # assume it's a json object
                try: 
                    obj = json.loads(msg) # load string
                    if obj["mode"] == "GET_ACTION":
                        action = model.get_action(obj)

                        #state = obj["sensors"]; reward = None; # Reward gets defined when TRANSITION_REWARD is received.

                        #transitions.append([state, reward])

                        client.sendall(str(action).encode("utf-8"))
                        # print("transitions=", transitions)
                    elif obj["mode"] == "TRANSITION_REWARD": # This will always be received after a GET_ACTION
                        #reward = obj["reward"]

                        #transitions[-1][1] = reward

                        # print("python r=", reward)
                        client.sendall(b"ACK")
                    else:
                        client.send("MESSAGE RECEIVED".encode("utf-8"))
                except Exception as e:
                    print("Error", e)
                    # print("Python process failed to parse json")

        # Keep the transition sizes limited
        if i > max_transition_size:
            transitions = [transitions[-1]]
            i=0
        i+=1
    server.close()
    print("Python server closed", flush=True)


