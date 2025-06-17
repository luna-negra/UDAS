#include "./udas_common.h"


void get_loglevel(char * tmp_level, int size)
{
    FILE * config_file = fopen(CONFIG_FILE_PATH, "r");
    if (config_file == NULL)
    {
        fprintf(stdout, "\033[0;31m[ERROR] Can not find UDAS Config file.\033[0;0m\n") ;
        return ;
    }

    char buffer[256];
    while (fgets(buffer, sizeof(buffer), config_file) != NULL)
    {
        if (strncmp(buffer, "level=", strlen("level=")) == 0)
        {
            char * token = strtok(buffer, "=");
            token = strtok(NULL, "=");
            if (token != NULL) 
            {
                for (int i = 0 ; i < strlen(token) - 1; i++) token[i] -= 32;

                strcpy(tmp_level, token);
                break;
            }
        }
    }

    fclose(config_file);
    return ;
}

void logger(char * level, char * app_name, char * log_text)
{   
    time_t now = time(NULL);
    FILE * log_file = fopen(LOG_FILE_PATH, "a");
    char * level_num[4] = {"ERROR", "WARNING", "INFO", "DEBUG"};

    if (log_file == NULL)
    {
        fprintf(stdout, "\033[0;31m[ERROR] Can not find UDAS Log file.\033[0;0m\n") ;
        return ;
    }

    char tmp_level[16], current_time[32], log[512] = "", print_out[256];

    get_loglevel(tmp_level, sizeof(tmp_level));
    strftime(current_time, sizeof(current_time), "%Y-%m-%d %H:%M:%S %s", localtime(&now));
    snprintf(log, sizeof(log), "%s: [%s - %s]  %s\n", current_time, app_name, level, log_text);

    int tmp_level_num, log_level_num;

    for (int i = 0; i < 4; i++)
    {
        if (*(level_num + i) == tmp_level) tmp_level_num = i;
        if (*(level_num + i) == level) log_level_num = i;
    }

    if (tmp_level_num >= log_level_num) fputs(log, log_file);
    fprintf(stdout, "[%s] %s\n", level, log_text);

    fclose(log_file);
    return ;
}
