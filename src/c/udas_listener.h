#ifndef UDAS_LISTENER_H
#define UDAS_LISTENER_H

    #include "./udas_common.h"
    #include <sys/socket.h>
    #include <sys/un.h>
    #include <sys/wait.h>
    #include <unistd.h>
    #include <pthread.h>

    #define BUFFER_SIZE 512
    #define SOCKET_PATH "/tmp/udas_socket"
    #define CMD_ARG_SIZE 6


#endif