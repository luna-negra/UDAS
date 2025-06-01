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

USB_INFO get_usb_dev(libusb_device * device, libusb_device_descriptor * desc)
{
    libusb_device_handle * handler = NULL;
    USB_INFO usb_info ;
    usb_info.result = 0;

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
        return usb_info;
    }

    if (libusb_get_string_descriptor_ascii(handler, desc->iManufacturer, usb_info.manufacture, sizeof(usb_info.manufacture)) < 2) strcpy(usb_info.manufacture, "Unknown");
    if (libusb_get_string_descriptor_ascii(handler, desc->iProduct, usb_info.product, sizeof(usb_info.product)) < 2) strcpy(usb_info.product, "Unknown");
    if (libusb_get_string_descriptor_ascii(handler, desc->iSerialNumber, usb_info.serialnum, sizeof(usb_info.serialnum)) < 2) strcpy(usb_info.serialnum, "Unknown");
    if (libusb_get_string_descriptor_ascii(handler, desc->bcdUSB, usb_info.version, sizeof(usb_info.version)) < 2) strcpy(usb_info.version, "Unknown");
    usb_info.product_id = desc->idProduct;
    usb_info.manufacture_id = desc->idVendor;
    usb_info.result = 1;
    
    fprintf(
        stdout, 
        "[INFO] New USB Storage is connected - Vendor: %s (%04x), Product: %s (%04x), SerialNum: %s\n", 
        usb_info.manufacture, usb_info.manufacture_id, usb_info.product, usb_info.product_id, usb_info.serialnum
    );

    // close libusb.
    libusb_close(handler);
    return usb_info;
}

int call_gui_alert(USB_INFO * usb_info)
{
    int cmd_result = -1;
    char command[256];

    // requires to be checked duplication execution.



    // create command to popup gui for checking new device.
    if (snprintf(command, 
            sizeof(command), 
            "/home/luna-negra/projects/UDAS/src/python/udas_alert --idVendor=%04x --idProduct=%04x --serial=%s --manufacturer=%s --product=%s",
            usb_info->manufacture_id,
            usb_info->product_id,
            usb_info->serialnum,
            usb_info->manufacture,
            usb_info->product) < 0)
    {
        fprintf(stderr, "[ERROR] Fail to create alert command\n");
        return EXIT_FAILURE;
    }

    // Abnormal: 65280
    // Normal: 30720
    FILE * cmd = popen(command, "r");
    cmd_result = pclose(cmd);
    printf("CALL_GUI: %d\n", cmd_result);
    return (cmd_result != 65280) ? 0 : -1 ;
}

int register_device(USB_INFO * usb_info)
{
    int cmd_result = -1;
    char command[256];
    char buffer[64];

    // create command to register new usb storage device to udev rule file
    if (snprintf(command,
            sizeof(command),
            "./udas td register --idVendor=%04x --idProduct=%04x --serial=%s --manufacturer=%s --product=%s",
            usb_info->manufacture_id,
            usb_info->product_id,
            usb_info->serialnum,
            usb_info->manufacture,
            usb_info->product) < 0)
    {
        fprintf(stderr, "[ERROR] Fail to create register command\n");
        return EXIT_FAILURE;
    }

    FILE * cmd = popen(command, "r");
    while (fgets(buffer, sizeof(buffer), cmd) != NULL)
    {
        if (strcmp(buffer, "success\n") == 0) return EXIT_SUCCESS;
    }
    pclose(cmd);
    return EXIT_FAILURE;
}

int search_device(USB_INFO * usb_info)
{
    int cmd_result = -1;
    char command[256];
    char return_print[64];

    // create command to register new usb storage device to udev rule file
    if (snprintf(command, 
            sizeof(command), 
            "./udas td search --idVendor=%04x --idProduct=%04x --serial=%s --manufacturer=%s --product=%s", 
            usb_info->manufacture_id,
            usb_info->product_id,
            usb_info->serialnum,
            usb_info->manufacture,
            usb_info->product) < 0)
    {
        fprintf(stderr, "[ERROR] Fail to create UDAS command\n");
        return EXIT_FAILURE;
    }

    FILE * cmd = popen(command, "r");
    while (fgets(return_print, sizeof(return_print), cmd) != NULL)
    {
        if (strcmp(return_print, "[INFO] registered device\n") == 0)
        {
            cmd_result = 0;
            break;
        }
    }
    pclose(cmd);

    if (cmd_result != 0)
    {
        fprintf(stdout, "[INFO] Not a registered USB storage\n");
        return EXIT_SUCCESS;
    }
    
    fprintf(stdout, "[INFO] Already registered USB storage\n");
    return EXIT_FAILURE;
}

void * work_thread(void * arg)
{
    USBDEV ** usb_dev = (USBDEV**)&(arg);

    while (1)
    {
        int is_mass_storage = 0;
        libusb_device * device = dequeue(usb_dev);
        libusb_device_descriptor desc ;
        struct libusb_config_descriptor * cfg_desc = NULL;
        const struct libusb_interface * infc = NULL;
        USB_INFO usb_info; 
        
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

            // fprint the device info.
            usb_info = get_usb_dev(device, &desc);
            usb_info.device_class = infc->altsetting->bInterfaceClass;

            // read udev rules and find
            // create udas process to search newly connected USB device in udev rule file.
            pid_t process_udas = fork();
            int cmd_result = -1;            
            
            if (process_udas == -1) fprintf(stderr, "[ERROR] Fail to create child process\n");
            else if (process_udas == 0)
            {
                cmd_result = search_device(&usb_info);
                sleep(1);

                if (cmd_result == 0)
                {
                    // Register Check.
                    if (call_gui_alert(&usb_info) == 0)
                    {
                        if (register_device(&usb_info) == 0)
                        {
                            fprintf(stdout, "[INFO] New device is registered as a trusted device.\n") :
                            // reload udev rule
                            // udevadm trigger
                        }
                        else
                        {
                            fprintf(stderr, "[ERROR] Fail to register new device as a trusted device.\n") ;
                        }
                    }
                }
                else {}
            }
            // DO NOTHING IN MAIN PROCESS

        }
        else sleep(1);
    }

    fprintf(stderr, "[ERROR] Thread for real time detecting was terminated.\n");
    exit(-1);
}

int hotplug_fn(libusb_context *ctx, libusb_device *device, libusb_hotplug_event event, void *user_data)
{
    USBDEV * usb_dev = (USBDEV *)user_data;
    if (event == LIBUSB_HOTPLUG_EVENT_DEVICE_ARRIVED) enqueue(&device, &ctx, &usb_dev);
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