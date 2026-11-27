import sys
import socket 
import json
from inital_Q import DoubleQNetwork
import traceback
import time
from pathlib import Path
import atexit
import torch

EVALUATE = False

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
    model = DumbAgent()
    # PORT: 9999
    server = socket.socket()
    # Allow reuse of the address after shutdown to make restarting easier
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind( ("127.0.0.1", 9999)) # > 1024 is safe
    server.listen()

    #---------- Load in model --------------
    model = DoubleQNetwork(num_sensors=7)
    checkpoint_path = (Path(__file__).resolve().parent / "checkpoints" / "double_dqn_7rays.pt")

    model.load(checkpoint_path)
    if not EVALUATE:
        atexit.register(model.save, checkpoint_path)

    print("Agent:", type(model).__name__, flush=True)
    transitions = [] ; max_transition_size = 20
    i=0 
    pending = None

    episode = 0
    episode_steps = 0
    episode_return = 0.0
    latest_loss = None
    evaluation_steps = 0
    report_started = time.perf_counter()

    # no limit for now
    while True:        
        client, addr = server.accept()
        with client: # with client ensures connection closes
            msg:str = client.recv(4096).decode("utf-8")

            if not msg:
                continue

            if msg == "hello":
                client.sendall(b"HELLO RECEIVED")
                continue
            if msg == "EXIT": # Kill the process
                client.sendall("EXIT MESSAGE RECEIVED".encode("utf-8"))
                break
            else:
                # assume it's a json object
                try: 
                    obj = json.loads(msg) # load string
                    if obj["mode"] == "GET_ACTION":
                        if EVALUATE:
                            with torch.no_grad():
                                sensors = torch.tensor(obj["sensors"], dtype=torch.float32, device=model.device).unsqueeze(0)

                                with torch.no_grad():
                                    q_values = model.online_network(sensors)
                                    action = q_values.argmax(dim=1).item()
                                
                                evaluation_steps += 1
                                if evaluation_steps % 10 == 0:
                                    print(
                                        f"[EVAL] "
                                        f"sensors={[round(x, 3) for x in obj['sensors']]} "
                                        f"Q={[round(x, 3) for x in q_values.squeeze(0).cpu().tolist()]} "
                                        f"action={action}",
                                        flush=True,
                                    )
                        else:
                                action = model.get_action(obj)
                        pending = (list(obj["sensors"]), action)
                        client.sendall(str(action).encode("utf-8"))
                        # print("transitions=", transitions)
                    elif obj["mode"] == "TRANSITION_REWARD": # This will always be received after a GET_ACTION
                        if pending is None:
                            raise RuntimeError("Received a result with no pending action")
                        sensors, action = pending
                        observe_started = time.perf_counter()

                        loss = None
                        if not EVALUATE:
                            loss = model.observe(sensors, action, obj["reward"], obj["next_sensors"], obj["terminated"])
                        
                        if not EVALUATE and model.environment_steps % 1000 == 0:
                            model.save(checkpoint_path)

                        observe_ms = (time.perf_counter() - observe_started) * 1000

                        if not EVALUATE and model.environment_steps % 100 == 0:
                            elapsed = time.perf_counter() - report_started

                            print(
                                f"[SPEED] {100 / elapsed:.1f} steps/sec "
                                f"observe={observe_ms:.1f}ms "
                                f"device={model.device} "
                                f"updates={model.learning_updates}",
                                flush=True,
                            )

                            report_started = time.perf_counter()




                        episode_steps += 1
                        episode_return += float(obj["reward"])

                        if loss is not None:
                            latest_loss = loss
                            if model.learning_updates % 100 == 0:
                                print(f"[LEARNING] updates={model.learning_updates} " f"memory={len(model.memory)} loss={loss:.5f}", flush=True)


                        if obj["terminated"]:
                            episode += 1
                            loss_text = (
                                "evaluation" if EVALUATE
                                else "warming up" if latest_loss is None
                                else f"{latest_loss:.5f}"
                            )
                            display_epsilon = 0.0 if EVALUATE else model.epsilon()

                            print(
                                f"[EPISODE {episode}] "
                                f"steps={episode_steps} "
                                f"return={episode_return:.3f} "
                                f"epsilon={display_epsilon:.3f} "
                                f"updates={model.learning_updates} "
                                f"latest_loss={loss_text}",
                                flush=True,
                            )

                            episode_steps = 0
                            episode_return = 0.0

                        pending = None

                        client.sendall(b"ACK")
                    else:
                        client.send("MESSAGE RECEIVED".encode("utf-8"))
                except Exception as e:
                    print(f"Error. Received message: {msg!r}", flush=True)
                    traceback.print_exc()
                    
                # print("Python process failed to parse json")

        # Keep the transition sizes limited
        if i > max_transition_size:
            transitions = transitions[-1:]
            i=0
        i+=1
    server.close()
    print("Python server closed", flush=True)


