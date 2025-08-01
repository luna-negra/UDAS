#include "./udas_listener.h"


int get_blacklist_setting()
{
    // if there is no config file, set blacklist as 0;
    FILE * config_file = fopen(CONFIG_FILE_PATH, "r");
    if (config_file == NULL) return 0;

    char buffer[256];
    while (fgets(buffer, sizeof(buffer), config_file) != NULL)
    {
        if (strncmp(buffer, "blacklist", strlen("blacklist")) == 0)
        {
            char * token = strtok(buffer, "=");
            token = strtok(NULL, "=");
            if (strncmp(token, "1", 1) == 0) return 1;
            break;
        }
    }

    return 0;
}

int get_cmd_arg(char ** store, char * buffer)
{
    int i = 0;
    *(store + i++) = strtok(buffer, " ");

    for (i ; i < CMD_ARG_SIZE; i++)
    {
        char * tmp = strtok(NULL, " ");
        *(store + i) = tmp;
    }

    return EXIT_SUCCESS;
}

int main(int argc, char argv)
{
    // unlink pre-exist socket
    unlink(SOCKET_PATH);

    // create socket
    int client_fd = 0;
    int socket_fd = socket(AF_LOCAL, SOCK_STREAM, 0);
    if (socket_fd == -1)
    {
        printf("[ERROR] Fail to create socket descriptor.\n");
        exit(1);
    }

    // create socket address
    struct sockaddr_un srv_addr;
    srv_addr.sun_family = AF_LOCAL;
    strncpy(srv_addr.sun_path, SOCKET_PATH, sizeof(srv_addr.sun_path));

    // bind
    if (bind(socket_fd, (struct sockaddr * )&srv_addr, sizeof(srv_addr)) == -1)
    {
        printf("[ERROR] Fail to bind socket address.\n");
        close(socket_fd);
        exit(1);
    }

    // listen
    if (listen(socket_fd, 1) == -1)
    {
        printf("[ERROR] Fail to maintain listen status...");
        close(socket_fd);
        exit(1);
    }

    // accept client
    while (1)
    {
        struct sockaddr_un clnt_addr;
        int clnt_addr_len = sizeof(clnt_addr);
        client_fd = accept(socket_fd, (struct sockaddr *)&clnt_addr, (socklen_t *)&clnt_addr_len);
        
        // if fail to accept client.
        if (client_fd == -1) continue;

        if (write(client_fd, "connect to listener...", strlen("connect to listener...")) < 0)
        {
            printf("[ERROR] Fail to send echo ACK to detector.\n");
            continue;
        }

        char buffer[BUFFER_SIZE] = {'\0'};
        char * cmd_args[CMD_ARG_SIZE] = {""};
        if (read(client_fd, buffer, BUFFER_SIZE) < 0)
        {
            write(client_fd, "[ERROR]Fail to get a data from detector", strlen("[ERROR]Fail to get a data from detector"));
            continue;
        }

        if (get_cmd_arg(cmd_args, buffer) == EXIT_FAILURE)
        {
            write(client_fd, "[ERROR]Listener got an invalid signal.", strlen("[ERROR]Listener got an invalid signal."));
            continue;
        }
        
        // create subprocess
        pid_t subprocess_pid = fork();

        // subprocess
        if (subprocess_pid == 0)
        {
            printf("%s\n", *(cmd_args + 0));
            printf("%s\n", *(cmd_args + 1));
            printf("%s\n", *(cmd_args + 2));
            printf("%s\n", *(cmd_args + 3));
            printf("%s\n", *(cmd_args + 4));                    
            printf("%s\n", *(cmd_args + 5));
            /*write(client_fd, *(cmd_args + 0), strlen(*cmd_args + 0));
            write(client_fd, *(cmd_args + 1), strlen(*cmd_args + 1));
            write(client_fd, *(cmd_args + 2), strlen(*cmd_args + 2));
            write(client_fd, *(cmd_args + 3), strlen(*cmd_args + 3));
            write(client_fd, *(cmd_args + 4), strlen(*cmd_args + 4));
            write(client_fd, *(cmd_args + 5), strlen(*cmd_args + 5));*/

            execlp(*(cmd_args + 0), *(cmd_args + 0), *(cmd_args + 1), *(cmd_args + 2), *(cmd_args + 3), *(cmd_args + 4), *(cmd_args + 5), NULL);
            write(client_fd, "[ERROR]Fail to execute udas_alert.", strlen("[ERROR]Fail to execute udas_alert."));
        }
        // main process
        else
        {
            int status, exit_code;
            waitpid(subprocess_pid, &status, 0);

            if (WIFEXITED(status))
            {
                exit_code = WEXITSTATUS(status);

                // 0: Success, 255: Cancel
                if (exit_code == 0) write(client_fd, "REGISTER WHITELIST", strlen("REGISTER WHITELIST"));
                else if (exit_code == 253) write(client_fd, "[ERROR]Fail to get a config file.", strlen("[ERROR]Fail to get a config file."));
                else if (exit_code == 254) write(client_fd, "[ERROR]udas_alert is not exit.", strlen("[ERROR]udas_alert is not exit."));
                else if (exit_code == 255)
                {
                    if (get_blacklist_setting() == 1) write(client_fd, "REGISTER BLACKLIST", strlen("REGISTER BLACKLIST"));
                    else write(client_fd, "new device was not registered as a whitelist nor a blacklist device.", strlen("new device was not registered as a whitelist nor a blacklist device."));
                }
                else write(client_fd, "[ERROR] unknown error", strlen("[ERROR] unknown error"));
            }
            else write(client_fd, "[ERROR]udas_alert is terminated by signal.", strlen("[ERROR]udas_alert is terminated by signal."));
        }
    }

    // remove socket
    unlink(SOCKET_PATH);
    return 0;
}