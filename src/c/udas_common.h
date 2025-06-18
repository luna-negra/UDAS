#ifndef UDAS_COMMON_H
#define UDAS_COMMON_H

    #include <stdio.h>
    #include <stdlib.h>
    #include <string.h>
    #include <time.h>

    #define CONFIG_FILE_PATH "/etc/udas/config/config.ini"
    #define LOG_FILE_PATH "/var/log/udas/udas.log"

    void logger(char * level, char * app_name, char * log_text);
    
#endif