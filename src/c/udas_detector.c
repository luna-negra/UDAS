#include "./udas_detector.h"


libusb_device * dequeue(USBDEV ** usb_dev)
{
    libusb_device * pop_data = (*usb_dev)->dev_list[(*usb_dev)->front];
    if (pop_data != NULL)
    {
         // obtain lock and pop up new device from list.
        pthread_mutex_lock(&((*usb_dev)->lock));
        (*usb_dev)->dev_list[(*usb_dev)->front] = NULL;
        (*usb_dev)->front = ((*usb_dev)->front + 1) % Q_LEN;
        // return lock.
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
    // return lock.
    pthread_mutex_unlock(&((*usb_dev)->lock));
    return;
}

USB_INFO get_usb_dev(libusb_device * device, libusb_device_descriptor * desc)
{
    libusb_device_handle * handler = NULL;
    USB_INFO usb_info ;
    usb_info.result = 0;

    // open libusb for checking newly connected USB storage.
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
        "[INFO] New USB Storage (%04x: %04x) is connected: Vendor - %s, Product: %s Serial: %s\n", 
        usb_info.manufacture_id, usb_info.product_id, usb_info.manufacture, usb_info.product, usb_info.serialnum
    );

    // close libusb.
    libusb_close(handler);
    return usb_info;
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

    // open pipe and file pointre for command execution.
    FILE * cmd = popen(command, "r");
    while (fgets(buffer, sizeof(buffer), cmd) != NULL)
    {
        if (strcmp(buffer, "success to regiser new trusted USB storage.\n") == 0) return EXIT_SUCCESS;
    }
    // close pipe and remove file pointre.
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

    // open pipe and file pointre for command execution.
    FILE * cmd = popen(command, "r");
    while (fgets(return_print, sizeof(return_print), cmd) != NULL)
    {
        if (strcmp(return_print, "[INFO] registered device\n") == 0)
        {
            cmd_result = 0;
            break;
        }
    }

    // close pipe and remove file pointre.
    pclose(cmd);

    if (cmd_result != 0)
    {
        fprintf(stdout, "[INFO] Not a registered USB storage\n");
        return EXIT_SUCCESS;
    }
    
    fprintf(stdout, "[INFO] Already registered USB storage\n");
    return EXIT_FAILURE;
}

void * call_gui_alert_thread(USB_INFO * usb_info)
{
    // search_device: if there is no search data, return NULL.
    if (search_device(usb_info) == EXIT_FAILURE) return NULL;

    fprintf(stdout, "[INFO] Start calling subprocess for udas_alert.\n");

    // create child process for udas_alert
    pid_t child_proc = fork();
    if (child_proc == -1)
    {
        fprintf(stderr, "[ERROR] Fail to create subprocess\n");
        return NULL;
    }

    if (child_proc == 0)
    {
        // child process for udas_alert
        char idVendor[64], idProduct[64], serial[64], manufacturer[64], product[64];        

        fprintf(stdout, "[INFO] (udas_alert) Asking about new USB storage...\n");
        snprintf(idVendor, sizeof(idVendor), "--idVendor=%04x", usb_info->manufacture_id);
        snprintf(idProduct, sizeof(idProduct), "--idProduct=%04x", usb_info->product_id);
        snprintf(serial, sizeof(serial), "--serial=%s", usb_info->serialnum);
        snprintf(manufacturer, sizeof(manufacturer), "--manufacturer=%s", usb_info->manufacture);
        snprintf(product, sizeof(product), "--product=%s", usb_info->product);
        execl(UDAS_ALERT_PATH, UDAS_ALERT_PATH, idVendor, idProduct, serial, manufacturer, product, NULL);
        
        // exit child process with error code.
        exit(-2);
    }
    else
    {
        // parent process
        int status, exit_code;
        waitpid(child_proc, &status, 0);

        if (WIFEXITED(status))
        {
            exit_code = WEXITSTATUS(status);

            // 0: Success, 255: Cancel
            if (exit_code == 0)
            {
                (register_device(usb_info) == EXIT_SUCCESS) ?
                fprintf(stdout, "[INFO] Success to register new USB storage as a trusted device.\n"):
                fprintf(stderr, "[ERROR] Fail to register new USB storage as a trusted device.\n");
            }
            else if (exit_code == 254) fprintf(stderr, "[ERROR] Can not find the udas_alert.\n");
            else fprintf(stderr, "[INFO] New USB storage is not registered as a trusted device.\n") ;
        }
        else if (WIFSIGNALED(status)) fprintf(stderr, "[ERROR] udas_alert is terminated by signal.\n");
    }
    return NULL;
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

            // convert to thread: 2025.06.03
            pthread_t grand_thread;

            // create grand_thread
            pthread_create(&grand_thread, NULL, (void *)call_gui_alert_thread, &usb_info);
        }
        else sleep(1);
    }

    fprintf(stderr, "[ERROR] Thread for real time detecting was terminated.\n");
    exit(-1);
}

// executed by libusb_hotplug_register_callback and libusb_handle_events_completed
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