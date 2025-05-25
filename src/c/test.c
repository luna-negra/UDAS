#include "./udas_detector.h"

/*
EXIT_SUCCESS: 0
EXIT_FAILURE: 1
*/



typedef struct {
    libusb_device * dev_lisb[Q_LEN];
    int front;
    int rear;

} USBDEV;


void dequeue()
{

}

void enqueue(libusb_device ** device, libusb_context ** ctx)
{
    
}

void work_thread()
{
    
}


int hotplug_fn(libusb_context *ctx, libusb_device *device, libusb_hotplug_event event, void *user_data)
{
    if (event == LIBUSB_HOTPLUG_EVENT_DEVICE_ARRIVED)
    {
        enqueue(&device, &ctx);
    }

    return EXIT_SUCCESS;
}

int main(int argc, char * argv[])
{
    libusb_context * ctx = NULL;
    libusb_hotplug_callback_handle ht_cb_handler;
    pthread_mutex_t thread;
    
    // initialize libusb context
    if (libusb_init(&ctx) != EXIT_SUCCESS) 
    {
        fprintf(stderr, "[ERROR] Fail to initialize USB context.\n");
        libusb_exit(ctx);
        return EXIT_FAILURE;
    }

    // check the platform support hotplug feature. (support: 1, not support: 0)
    if (libusb_has_capability(LIBUSB_CAP_HAS_HOTPLUG) == 0)
    {
        fprintf(stderr, "[ERROR] Your libusb-1.0 libaray does not support hotplug.\n \
            You have to install libusb up t version 1.0.26\n");
        libusb_exit(ctx);
        return EXIT_FAILURE;
    }

    if (libusb_hotplug_register_callback(ctx,
                                        LIBUSB_HOTPLUG_EVENT_DEVICE_ARRIVED,
                                        0,
                                        LIBUSB_HOTPLUG_MATCH_ANY,
                                        LIBUSB_HOTPLUG_MATCH_ANY,
                                        LIBUSB_HOTPLUG_MATCH_ANY,
                                        hotplug_fn,
                                        NULL, 
                                        &ht_cb_handler) != EXIT_SUCCESS)
    {
        fprintf(stderr, "[ERROR] Fail to register hotplug callback.\n");
        libusb_exit(ctx);
        return EXIT_FAILURE;
    }

    if (pthread_mutex_init(&thread, NULL) != EXIT_SUCCESS)
    {
        fprintf(stderr, "[ERROR] Fail to create thread.\n");
        return EXIT_FAILURE;
    }

    //pthread_create(&thread, NULL, work_thread, );


    fprintf(stdout, "** LISTENING USB PORT **\n");
    while(1)
    {
        libusb_handle_events_completed(ctx, NULL);
    }
    
    libusb_exit(ctx);
    return EXIT_SUCCESS;
}