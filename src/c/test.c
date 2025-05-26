#include "./udas_detector.h"

/*
EXIT_SUCCESS: 0
EXIT_FAILURE: 1
*/



typedef struct {
    libusb_device * dev_lisb[Q_LEN];
    int front;
    int rear;
    pthread_mutex_t lock;
} USBDEV;


void dequeue()
{

}

void enqueue(libusb_device ** device, libusb_context ** ctx, USBDEV ** usb_dev)
{
    int is_mass_storage = 0;

    if (*device == NULL)
    {
        return;
    }

    (*usb_dev)->rear = (((*usb_dev)->rear) + 1) % Q_LEN;
    if ((*usb_dev)->front == (*usb_dev)->rear % Q_LEN)
    {
        fprintf(stdout, "[WARNING] Too many USB devices are connected.\n");
        return;
    }

    libusb_device_descriptor desc;
    if (libusb_get_device_descriptor(*device, &desc) != EXIT_SUCCESS)
    {
        fprintf(stdout, "[ERROR] Can not get a device descriptor\n");
        return ;
    }

    switch(desc.bDeviceClass)
    {
        case (0x00):
            struct libusb_config_descriptor * cfg_desc;            
            if (libusb_get_config_descriptor(*device, 0, &cfg_desc) != EXIT_SUCCESS) break;

            for (int i = 0; i < cfg_desc->bNumInterfaces; i++) 
            {
                const struct libusb_interface * infc = &(cfg_desc->interface)[i];
                for (int j = 0; j < infc->num_altsetting; j++)
                {
                    if (infc->altsetting->bInterfaceClass == 0x08) is_mass_storage = 1;
                    break;
                }
                if (is_mass_storage) break;
            }
            break;
        case (0x08):
            is_mass_storage = 1;
            break;
    }

    if (is_mass_storage) 
    {
        fprintf(stdout, "[INFO] New USB Storage was detected\n");
        ((*usb_dev)->dev_lisb)[(*usb_dev)->rear] = *device;
    }
    else fprintf(stdout, "[INFO] Non USB Storage was detected\n");
    return;
}

void * work_thread(void * arg)
{
    
}


int hotplug_fn(libusb_context *ctx, libusb_device *device, libusb_hotplug_event event, void *user_data)
{
    USBDEV * usb_dev = (USBDEV *)user_data;
    if (event == LIBUSB_HOTPLUG_EVENT_DEVICE_ARRIVED)
    {
        enqueue(&device, &ctx, &usb_dev);
    }

    return EXIT_SUCCESS;
}

int main(int argc, char * argv[])
{
    libusb_context * ctx = NULL;
    libusb_hotplug_callback_handle ht_cb_handler;
    pthread_t thread;
    USBDEV * usb_dev = (USBDEV *)malloc(sizeof(USBDEV));
    
    if (usb_dev != NULL)
    {
        usb_dev->front = 0;
        usb_dev->rear = 0;
    }

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

    // define hotplug callback
    if (libusb_hotplug_register_callback(ctx,
                                        LIBUSB_HOTPLUG_EVENT_DEVICE_ARRIVED,
                                        0,
                                        LIBUSB_HOTPLUG_MATCH_ANY,
                                        LIBUSB_HOTPLUG_MATCH_ANY,
                                        LIBUSB_HOTPLUG_MATCH_ANY,
                                        hotplug_fn,
                                        usb_dev, 
                                        &ht_cb_handler) != EXIT_SUCCESS)
    {
        fprintf(stderr, "[ERROR] Fail to register hotplug callback.\n");
        libusb_exit(ctx);
        return EXIT_FAILURE;
    }

    // define thread interlock and init
    if (pthread_mutex_init(&(usb_dev->lock), NULL) != EXIT_SUCCESS)
    {
        fprintf(stderr, "[ERROR] Fail to create thread.\n");
        return EXIT_FAILURE;
    }

    // create and start thread
    pthread_create(&thread, NULL, work_thread, NULL);
    fprintf(stdout, "** LISTENING USB PORT **\n");

    while(1)
    {
        // listen USB event
        libusb_handle_events_completed(ctx, NULL);
    }
    
    // destroy thread interlock
    pthread_mutex_destroy(&(usb_dev->lock));

    // leave libusb context.
    libusb_exit(ctx);
    return EXIT_SUCCESS;
}