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

    #define UNKNOWN "Unknown"
    #define OPTION_DELIMITER "="
    #define OPTION_ID_VENDOER "--idVendor="
    #define OPTION_ID_PRODUCT "--idProduct="
    #define OPTION_SERIAL "--serial="
    #define OPION_MANUFACTURER "--manufacturer="
    #define OPTION_PRODUCT "--product="

#endif