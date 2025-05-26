#include "./udas_detector.h"


libusb_device * dequeue(USBDEV ** usb_dev)
{
    libusb_device * pop_data = (*usb_dev)->dev_list[(*usb_dev)->front];
    if (pop_data != NULL)
    {
        pthread_mutex_lock(&((*usb_dev)->lock));
        (*usb_dev)->dev_list[(*usb_dev)->front] = NULL;
        (*usb_dev)->front = ((*usb_dev)->front + 1) % Q_LEN;
        pthread_mutex_unlock(&((*usb_dev)->lock));
    }
    return pop_data ;
}

void enqueue(libusb_device ** device, libusb_context ** ctx, USBDEV ** usb_dev)
{
    if (*device == NULL) return;

    if ((*usb_dev)->front == ((*usb_dev)->rear + 1) % Q_LEN)
    {
        fprintf(stdout, "[WARNING] Too many USB devices are connected simultaneously.\n");
        return;
    }
    
    // obtain lock and add new device to list.
    pthread_mutex_lock(&((*usb_dev)->lock));
    (*usb_dev)->dev_list[(*usb_dev)->rear] = *device;
    (*usb_dev)->rear = (((*usb_dev)->rear) + 1) % Q_LEN;
    pthread_mutex_unlock(&((*usb_dev)->lock));
    return;
}

void * work_thread(void * arg)
{
    USBDEV ** usb_dev = (USBDEV**)&(arg);

    while (1)
    {
        int is_mass_storage = 0;
        libusb_device * device = dequeue(usb_dev);
        libusb_device_handle * handler = NULL;
        libusb_device_descriptor desc ;
        struct libusb_config_descriptor * cfg_desc = NULL;
        const struct libusb_interface * infc = NULL;
        USB_INFO usb_info; 
        usb_info.result = 0;
        
        if (device != NULL)
        {            
            // read descriptor or USB device
            if (libusb_get_device_descriptor(device, &desc) != EXIT_SUCCESS)
            {
                fprintf(stdout, "[WARNING] Fail to read descriptor of USB Device.\n");
                continue;
            }
            
            if (desc.bDeviceClass == 0x08) is_mass_storage = 1;
            else if (desc.bDeviceClass == 0x00) 
            {
                if (libusb_get_config_descriptor(device, 0, &cfg_desc) != EXIT_SUCCESS)
                {
                    fprintf(stdout, "[WARNING] Fail to read config descriptor of USB Device.\n");
                    continue;
                }

                for (int i = 0 ; i < cfg_desc->bNumInterfaces ; i++)
                {
                    infc = &((cfg_desc->interface)[i]);
                    for (int j = 0 ; j < infc->num_altsetting; j++)
                    {
                        if ((infc->altsetting->bInterfaceClass == 0x08) || (infc->altsetting->bInterfaceClass == 0x06))
                        {
                            is_mass_storage = 1;
                            break;
                        }
                    }
                    if (is_mass_storage) break;
                }
            }

            if (!is_mass_storage) 
            {
                (infc != NULL) ?  
                fprintf(stdout, "[INFO] Non Storage USB device (%04x) is connected.\n", infc->altsetting->bInterfaceClass): 
                fprintf(stdout, "[INFO] Non Storage USB device (%04x) is connected.\n", desc.bDeviceClass);
                continue;
            }

            // open libusb for newly connected USB storage.
            int r = libusb_open(device, &handler);
            
            // check libusb status.
            if (r == LIBUSB_ERROR_ACCESS)
            {
                fprintf(stderr, "[ERROR] Need root or sudo privilege to check USB device. Process will be terminated.\n");
                exit(-1);
            }
            else if (r != 0)
            {
                fprintf(stdout, "[WARNING] Can not open libusb for new USB storage\n");
                continue;
            }

            if (libusb_get_string_descriptor_ascii(handler, desc.iManufacturer, usb_info.manufacture, sizeof(usb_info.manufacture)) < 2)
            {
                strcpy(usb_info.manufacture, "Unknown");
            }
            if (libusb_get_string_descriptor_ascii(handler, desc.iProduct, usb_info.product, sizeof(usb_info.product)) < 2)
            {
                strcpy(usb_info.product, "Unknown");
            }
            if (libusb_get_string_descriptor_ascii(handler, desc.iSerialNumber, usb_info.serialnum, sizeof(usb_info.serialnum)) < 2)
            {
                strcpy(usb_info.serialnum, "Unknown");
            }
            if (libusb_get_string_descriptor_ascii(handler, desc.bcdUSB, usb_info.version, sizeof(usb_info.version)) < 2)
            {
                strcpy(usb_info.version, "Unknown");
            }
            usb_info.product_id = desc.idProduct;
            usb_info.manufacture_id = desc.idVendor;
            usb_info.result = 1;
            
            fprintf(
                stdout, 
                "[INFO] New USB Storage is connected - Vendor: %s (%04x), Product: %s (%04x), SerialNum: %s\n", 
                usb_info.manufacture, usb_info.manufacture_id, usb_info.product, usb_info.product_id, usb_info.serialnum
            );

            // close libusb.
            libusb_close(handler);
            // read udev rules.
        }
        else sleep(1);
    }

    fprintf(stderr, "[ERROR] Thread for real time detecting was terminated.\n");
    exit(-1);
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
    pthread_create(&thread, NULL, work_thread, usb_dev);
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

    // remove dynamic memory allocation.
    free(usb_dev);
    return EXIT_SUCCESS;
}