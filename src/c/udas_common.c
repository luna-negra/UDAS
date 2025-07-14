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
                for (int i = 0 ; i < strlen(token); i++)
                {
                    if (token[i] != '\n') token[i] -= 32;
                    else
                    {
                        token[i] = '\0';
                        break;
                    }
                }

                strncpy(tmp_level, token, strlen(token));
                tmp_level[strlen(tmp_level)] = '\0';
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

    char config_level[16] = "", current_time[32] = "", log[512] = "", print_out[1024] = "";

    get_loglevel(config_level, sizeof(config_level));
    strftime(current_time, sizeof(current_time), "%Y-%m-%d %H:%M:%S %s", localtime(&now));
    snprintf(log, sizeof(log), "%s: [%s - %s]  %s\n", current_time, app_name, level, log_text);
    snprintf(print_out, sizeof(print_out), "[%s] %s", level, log_text);

    int config_level_num = 0, log_level_num = 0;
    for (int i = 0 ; i < 4; i++)
    {
        if (strncmp(config_level, level_num[i], strlen(level_num[i])) == 0) config_level_num = i;
        if (strncmp(level, level_num[i], strlen(level_num[i])) == 0) log_level_num = i;
    }

    if (config_level_num >= log_level_num) 
    {
        fputs(log, log_file);
        fprintf(stdout, "%s\n", print_out);
    }
    fclose(log_file);
    return ;
}
