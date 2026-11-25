
#include "RL_config.h"
#include <sys/socket.h>
#include <netinet/in.h>
#include <unistd.h>
#include <cstring>
#include <arpa/inet.h>


// send_messsage
// Credit https://www.geeksforgeeks.org/cpp/socket-programming-in-cpp/
// Sends a message to localhost:9999 (for the python process to pick up)
int send_message(const char* msg) {
    // 1. Create server socket
    // AF_INET: IPv4 protocol,    SOCKET_STREAM: TCP socket
    int port =  RLConfig::PORT; 
    int clientSocket = socket(AF_INET, SOCK_STREAM, 0);
    // std::cout << "Client socket = " << clientSocket << std::endl;
    // std::cout << "Message from client: " << std::endl;
    
    // 2. Define server address
    // htons() : converts port to network byte order
    sockaddr_in serverAddress;
    serverAddress.sin_family = AF_INET;  
    serverAddress.sin_port = htons(port);
    serverAddress.sin_addr.s_addr = inet_addr(RLConfig::IP_ADDR);

    // Make connection requiest
    int connectStatus= connect(clientSocket, (struct sockaddr*)&serverAddress, sizeof(serverAddress));
    // std::cout << "Connect status:" << connectStatus << std::endl;

    // Send message 
    send(clientSocket, msg, strlen(msg), 0);
    // Receive response
    char buf[1024] = { 0 };
    recv(clientSocket, buf, sizeof(buf), 0);
    // std::cout << "Message from client: " << buf << std::endl;
    close(clientSocket);

    // Convert string to integer
    try {
        int action = std::stoi(buf);
        return action;
    }catch (const std::exception& e) {
        return -1;
    }
}
