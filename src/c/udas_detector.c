#include "./udas_common.h"
#include "./udas_detector.h"


char * APP_NAME = "UDAS_DETECTOR";

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
        logger("WARNING", APP_NAME, "Too many USB devices are connected simultaneously.");
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
        logger("ERROR", APP_NAME, "Need root or sudo privilege to check USB device. Process will be terminated.");
        exit(-1);
    }
    else if (r != 0)
    {
        logger("WARNING", APP_NAME, "Can not open libusb for new USB storage.");
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
        "[INFO] USB Storage (%04x: %04x) is connected: Vendor - %s, Product: %s Serial: %s\n",
        usb_info.manufacture_id, usb_info.product_id, usb_info.manufacture, usb_info.product, usb_info.serialnum
    );

    char tmp[256] = "";
    snprintf(
        tmp, 
        sizeof(tmp), 
        "USB Storage (%04x: %04x) is connected: Vendor - %s, Product: %s Serial: %s",
        usb_info.manufacture_id, usb_info.product_id, usb_info.manufacture, usb_info.product, usb_info.serialnum);
    logger("INFO", APP_NAME, tmp);

    // close libusb.
    libusb_close(handler);
    return usb_info;
}

int get_blacklist_setting()
{
    FILE * config_file = fopen(CONFIG_FILE_PATH, "r");
    if (config_file == NULL) return 0;

    char buffer[256];
    while (fgets(buffer, sizeof(buffer), config_file) != NULL)
    {
        if (strncmp(buffer, "blacklist", strlen("blacklist")) == 0)
        {
            char * token = strtok(buffer, "=");
            token = strtok(NULL, "=");
            if (strncmp(token, "1", 1) == 0) return 1;
            break;
        }
    }

    return 0;
}

int register_device(USB_INFO * usb_info, int blacklist)
{
    int cmd_result = -1;
    char command[256] = "";
    char buffer[64] = "";
    char reg_opt[16] = "";
    (blacklist == 0) ? strncpy(reg_opt, "whitelist", sizeof("whitelist")) : strncpy(reg_opt, "blacklist", sizeof("blacklist")) ;

    // create command to register new usb storage device to udev rule file
    if (snprintf(command,
            sizeof(command),
            "udas td register %s --idVendor=%04x --idProduct=%04x --serial=%s --manufacturer=%s --product=%s",
            reg_opt,
            usb_info->manufacture_id,
            usb_info->product_id,
            usb_info->serialnum,
            usb_info->manufacture,
            usb_info->product) < 0)
    {
        logger("ERROR", APP_NAME, "Fail to create register command.");
        return EXIT_FAILURE;
    }

    // open pipe and file pointre for command execution.
    FILE * cmd = popen(command, "r");
    while (fgets(buffer, sizeof(buffer), cmd) != NULL)
    {
        if ((strstr(buffer, "success to register new whitelist USB storage.") != NULL) || \
            (strstr(buffer, "success to register blacklist device.") != NULL)) return EXIT_SUCCESS;
    }
    // close pipe and remove file pointre.
    pclose(cmd);
    return EXIT_FAILURE;
}

int search_device(USB_INFO * usb_info)
{
    int cmd_result = 0;
    char command[256] = "";
    char return_print[64] = "";

    // create command to register new usb storage device to udev rule file
    if (snprintf(command, 
            sizeof(command), 
            "udas td search --idVendor=%04x --idProduct=%04x --serial=%s --manufacturer=%s --product=%s",
            usb_info->manufacture_id,
            usb_info->product_id,
            usb_info->serialnum,
            usb_info->manufacture,
            usb_info->product) < 0)
    {
        logger("ERROR", APP_NAME, "Fail to create UDAS command.");
        return EXIT_FAILURE;
    }

    // open pipe and file pointre for command execution.
    FILE * cmd = popen(command, "r");
    while (fgets(return_print, sizeof(return_print), cmd) != NULL)
    {
        if (strstr(return_print, "Device is registered as whitelist.") != NULL)
        {
            cmd_result = 1;
            break;
        }
        else if (strstr(return_print, "Device is registered as blacklist.") != NULL)
        {
            cmd_result = -1;
            break;
        }
    }

    // close pipe and remove file pointre.
    pclose(cmd);
    
    if (cmd_result == 0)
    {
        logger("INFO", APP_NAME, "Not a registered USB storage.");
        return EXIT_SUCCESS;
    }
    else if (cmd_result == 1) logger("INFO", APP_NAME, "Already registered USB storage as whitelist.");
    else if (cmd_result == -1) logger("INFO", APP_NAME, "Already registered USB storage as blacklist.");
    return EXIT_FAILURE;
}

int is_udas_alert_run(USB_INFO * usb_info)
{
    int line = 0;
    char command[256] = "ps -aux | grep udas_alert ";
    char option_idVendor[64] = "", option_idproduct[64] = "", option_serial[64] = "", buffer[512] = "";

    snprintf(option_idVendor, sizeof(option_idVendor), "| grep %04x ", usb_info->manufacture_id);
    snprintf(option_idproduct, sizeof(option_idproduct), "| grep %04x ", usb_info->product_id);
    snprintf(option_serial, sizeof(option_serial), "| grep %s ", usb_info->serialnum);

    strcat(command, option_idVendor);
    strcat(command, option_idproduct);
    strcat(command, option_serial);
    
    FILE * cmd = popen(command, "r");

    if (cmd != NULL)
    {   
        while (fgets(buffer, sizeof(buffer), cmd) != NULL)
        {
            if (strlen(buffer) != 0) line += 1;        
        }
        pclose(cmd);
    }

    return (line <= 1) ? EXIT_SUCCESS : EXIT_FAILURE ;
}

void * call_gui_alert_thread(USB_INFO * usb_info)
{
    // search_device: if there is no search data, return NULL.
    if (search_device(usb_info) == EXIT_FAILURE) return NULL;

    // check duplicate execution for udas_alert
    if (is_udas_alert_run(usb_info) != EXIT_SUCCESS)
    {
        logger("WARNING", APP_NAME, "Process for the same USB storage is already Running.");
        return NULL;
    }

    logger("INFO", APP_NAME, "Start calling subprocess for udas_alert.");

    // create child process for udas_alert
    pid_t child_proc = fork();
    if (child_proc == -1)
    {
        logger("ERROR", APP_NAME, "Fail to create subprocess.");
        return NULL;
    }

    // child process for udas_alert
    char idVendor[64], idProduct[64], serial[64], manufacturer[64], product[64];
    logger("INFO", APP_NAME, "Asking about new USB storage...");
    snprintf(idVendor, sizeof(idVendor), "--idVendor=%04x", usb_info->manufacture_id);
    snprintf(idProduct, sizeof(idProduct), "--idProduct=%04x", usb_info->product_id);
    snprintf(serial, sizeof(serial), "--serial=%s", usb_info->serialnum);
    snprintf(manufacturer, sizeof(manufacturer), "--manufacturer=%s", usb_info->manufacture);
    snprintf(product, sizeof(product), "--product=%s", usb_info->product);

    if (child_proc == 0)
    {
        execlp("udas_alert", "udas_alert", idVendor, idProduct, serial, manufacturer, product, NULL);
        
        // exit child process with error code if fail to execute command.
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
                (register_device(usb_info, 0) == EXIT_SUCCESS) ?
                logger("INFO", APP_NAME, "Success to register new USB storage as whitelist."):
                logger("ERROR", APP_NAME, "Fail to register new USB storage as whitelist.");
            }
            else if (exit_code == 253) logger("ERROR", APP_NAME, "Config file is not exist.");
            else if (exit_code == 254) logger("ERROR", APP_NAME, "Can not find the udas_alert."); 
            else 
            {
                int blacklist = get_blacklist_setting();                
                if (blacklist == 0) logger("INFO", APP_NAME, "New USB storage is not registered as whitelist.");
                else
                {
                    (register_device(usb_info, 1) == EXIT_SUCCESS) ?
                    logger("INFO", APP_NAME, "New USB storage is registered as blacklist."):
                    logger("ERROR", APP_NAME, "Fail to register new USB storage as blacklist.");
                }                
            }
        }
        else if (WIFSIGNALED(status)) logger("ERROR", APP_NAME, "udas_alert is terminated by signal.");
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
                logger("WARNING", APP_NAME, "Fail to read descriptor of USB Device.");
                continue;
            }
            
            if (desc.bDeviceClass == 0x08) is_mass_storage = 1;
            else if (desc.bDeviceClass == 0x00) 
            {
                if (libusb_get_config_descriptor(device, 0, &cfg_desc) != EXIT_SUCCESS)
                {
                    logger("WARNING", APP_NAME, "Fail to read config descriptor of USB Device.");
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
                if (infc != NULL) 
                {
                    char tmp[128];
                    snprintf(tmp, sizeof(tmp), "Non Storage USB device (%04x) is connected.", infc->altsetting->bInterfaceClass);
                    logger("INFO", APP_NAME, tmp);
                }
                else
                {
                    char tmp[128];
                    snprintf(tmp, sizeof(tmp), "Non Storage USB device (%04x) is connected.", desc.bDeviceClass);
                    logger("INFO", APP_NAME, tmp);
                }
                continue;
            }

            // fprint the device info.
            usb_info = get_usb_dev(device, &desc);

            // if the usb connection is unstable.
            if (usb_info.result == 0)
            {
                logger("WARNING", APP_NAME, "Has a problem during reading USB Storage information.");
                continue;
            }

            usb_info.device_class = infc->altsetting->bInterfaceClass;

            // convert to thread: 2025.06.03
            pthread_t grand_thread;

            // create grand_thread
            pthread_create(&grand_thread, NULL, (void *)call_gui_alert_thread, &usb_info);
        }
        else sleep(1);
    }

    logger("ERROR", APP_NAME, "Thread for real time detecting was terminated.");
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
        logger("ERROR", APP_NAME, "Fail to initialize USB context.");
        libusb_exit(ctx);
        return EXIT_FAILURE;
    }

    // check the platform support hotplug feature. (support: 1, not support: 0)
    if (libusb_has_capability(LIBUSB_CAP_HAS_HOTPLUG) == 0)
    {
        logger("ERROR", APP_NAME, "Your libusb-1.0 libaray does not support hotplug.\nYou have to install libusb up t version 1.0.26");
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
        logger("ERROR", APP_NAME, "Fail to register hotplug callback.");
        libusb_exit(ctx);
        return EXIT_FAILURE;
    }

    // define thread interlock and init
    if (pthread_mutex_init(&(usb_dev->lock), NULL) != EXIT_SUCCESS)
    {
        logger("ERROR", APP_NAME, "Fail to create thread.");
        return EXIT_FAILURE;
    }

    // create and start thread
    pthread_create(&thread, NULL, work_thread, usb_dev);
    logger("INFO", APP_NAME, "Start Listening USB port...");
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