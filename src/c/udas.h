#ifndef UDAS_H
#define UDAS_H

    #include <stdio.h>
    #include <stdlib.h>
    #include <string.h>

    typedef struct  
    {   
        char manufacturer[32];
        char product[32];
        char serial[32];
        char idVendor[8];
        char idProduct[8];
    } USB_DEV;

    #define CONFIG_FILE_PATH "/etc/udas/config/config.ini"
    #define CONFIG_FILE_TMP_PATH "/etc/udas/config/config.ini_tmp"
    #define CUSTOM_BLACKLIST_RULE "/etc/udev/rules.d/99-udas.blacklist.rules"
    #define CUSTOM_BLACKLIST_RULE_TMP "/etc/udev/rules.d/99-udas.blacklist.rules_tmp"
    #define CUSTOM_WHITELIST_RULE "/etc/udev/rules.d/99-udas.custom.rules"
    #define CUSTOM_WHITELIST_RULE_TMP "/etc/udev/rules.d/99-udas.custom.rules_tmp"
    #define DEFAULT_UDEV_RULE "ACTION==\"add\", SUBSYSTEM==\"block\", "
    #define OPTION_DELIMITER "="
    #define OPTION_ID_VENDOR "--idVendor"
    #define OPTION_ID_PRODUCT "--idProduct"
    #define OPTION_SERIAL "--serial"
    #define OPTION_MANUFACTURER "--manufacturer"
    #define OPTION_PRODUCT "--product"
    #define OPTION_MOUTN_ENV "ENV{UDISKS_IGNORE}=\"0\"\n"
    #define UNKNOWN "Unknown"

    int search_td(char ** rule_str, USB_DEV * usb_dev);

#endif