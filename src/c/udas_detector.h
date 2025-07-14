/*
[ libusb.h ]
EXIT_SUCCESS: 0
EXIT_FAILURE: 1
*/

#ifndef UDAS_DETECTOR_H
#define UDAS_DETECTOR_H

    // install libusb-1.0 from dpkg
    #include <libusb-1.0/libusb.h>
    #include <unistd.h>
    #include <pthread.h>
    #include <sys/types.h>
    #include <sys/wait.h>
    #include "./udas_common.h"

    #define Q_LEN 16

    typedef struct libusb_device_descriptor libusb_device_descriptor;
    typedef struct {
        short result;
        char manufacture[32];
        char product[32];
        char serialnum[32];
        char version[32];
        uint16_t device_class;
        uint16_t manufacture_id;
        uint16_t product_id;
    } USB_INFO ;

    typedef struct {
    libusb_device * dev_list[Q_LEN];
    int front;
    int rear;
    pthread_mutex_t lock;
    } USBDEV;

#endif