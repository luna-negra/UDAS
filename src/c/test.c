// install libusb-1.0 from dpkg
#include <libusb-1.0/libusb.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>


static int new_device_detected_cb(libusb_context * ctx, libusb_device * device, 
                                libusb_hotplug_event event, void *user_data)
{





    return 0;
}

int main(int argc, char * argv [])
{
    libusb_context * ctx = NULL ;
    libusb_hotplug_callback_handle handler;
    
    // init libusb library context: success(0), Failure(< 0)
    if (libusb_init(&ctx) != LIBUSB_SUCCESS)
    {
        fprintf(stderr, "[ERROR] Fail to initailize libusb context\n");
        libusb_exit(ctx);
        return EXIT_FAILURE;
    }

    // Check the platform provides Hotplug or not: Support(1), Not Support(0)
    if (!libusb_has_capability(LIBUSB_CAP_HAS_CAPABILITY))
    {
        fprint(stderr, "[ERROR] This libusb library does not provide hotplug.\n");
        libusb_exit(ctx);
        return EXIT_FAILURE;
    }

    int result =libusb_hotplug_register_callback(ctx, 
                                                 LIBUSB_HOTPLUG_EVENT_DEVICE_ARRIVED, 
                                                 0, \
                                                 LIBUSB_HOTPLUG_MATCH_ANY, 
                                                 LIBUSB_HOTPLUG_MATCH_ANY, 
                                                 LIBUSB_HOTPLUG_MATCH_ANY, 
                                                 new_device_detected_cb,
                                                 NULL, \
                                                 handler);

    if (result == LIBUSB_SUCCESS)
    {
        fprintf(stderr, "Error registering hotplug callback\n");
        libusb_exit(ctx);
        return EXIT_FAILURE;
    }

    printf("Listening for USB mass storage devices...\n");

    // Event Listening.
    while (1) 
    {
        int result = libusb_handle_events_completed(ctx, NULL);
    }

    libusb_close(ctx);
    return EXIT_SUCCESS;
}


/*
static int hotplug_callback(struct libusb_context *ctx, struct libusb_device *dev,
                            libusb_hotplug_event event, void *user_data) 
{
    struct libusb_device_descriptor desc;
    libusb_device_handle *handle = NULL;
    char manufacturer[64], product[64], serial[64];

    if (event != LIBUSB_HOTPLUG_EVENT_DEVICE_ARRIVED) {
        return 0;
    }

    int r = libusb_get_device_descriptor(dev, &desc);
    if (r != LIBUSB_SUCCESS) {
        fprintf(stderr, "Failed to get device descriptor\n");
        return 0;
    }

    // Mass Storage class is 0x08
    if (desc.bDeviceClass != LIBUSB_CLASS_PER_INTERFACE) {
        return 0;
    }

    struct libusb_config_descriptor *config;
    r = libusb_get_config_descriptor(dev, 0, &config);
    if (r != LIBUSB_SUCCESS) {
        fprintf(stderr, "Failed to get config descriptor\n");
        return 0;
    }

    int is_mass_storage = 0;
    for (int i = 0; i < config->bNumInterfaces; i++) {
        const struct libusb_interface *interface = &config->interface[i];
        for (int j = 0; j < interface->num_altsetting; j++) {
            const struct libusb_interface_descriptor *altsetting = &interface->altsetting[j];
            if (altsetting->bInterfaceClass == LIBUSB_CLASS_MASS_STORAGE) {
                is_mass_storage = 1;
                break;
            }
        }
    }

    libusb_free_config_descriptor(config);

    if (!is_mass_storage) {
        return 0;
    }

    r = libusb_open(dev, &handle);
    if (r != LIBUSB_SUCCESS) {
        fprintf(stderr, "[WARNING] Need root permission or access error\n");
        return 0;
    }

    if (desc.iManufacturer)
        libusb_get_string_descriptor_ascii(handle, desc.iManufacturer, manufacturer, sizeof(manufacturer));
    else
        strcpy(manufacturer, "Unknown");

    if (desc.iProduct)
        libusb_get_string_descriptor_ascii(handle, desc.iProduct, product, sizeof(product));
    else
        strcpy(product, "Unknown");

    if (desc.iSerialNumber)
        libusb_get_string_descriptor_ascii(handle, desc.iSerialNumber, serial, sizeof(serial));
    else
        strcpy(serial, "Unknown");

    printf("\n[USB DEVICE CONNECTED]\n");
    printf("Product     : %s\n", product);
    printf("Manufacturer: %s\n", manufacturer);
    printf("Serial Num  : %s\n", serial);
    printf("VID:PID     : %04x:%04x\n", desc.idVendor, desc.idProduct);

    libusb_close(handle);
    return 0;
}

int main(void) 
{
    libusb_context *ctx = NULL;
    libusb_hotplug_callback_handle hp_handle;

    if (libusb_init(&ctx) != LIBUSB_SUCCESS) {
        fprintf(stderr, "libusb init failed\n");
        return EXIT_FAILURE;
    }

    if (!libusb_has_capability(LIBUSB_CAP_HAS_HOTPLUG)) {
        fprintf(stderr, "Hotplug not supported on this platform\n");
        libusb_exit(ctx);
        return EXIT_FAILURE;
    }

    int rc = libusb_hotplug_register_callback(ctx,
                                              LIBUSB_HOTPLUG_EVENT_DEVICE_ARRIVED,
                                              0,
                                              LIBUSB_HOTPLUG_MATCH_ANY,
                                              LIBUSB_HOTPLUG_MATCH_ANY,
                                              LIBUSB_HOTPLUG_MATCH_ANY,
                                              hotplug_callback,
                                              NULL,
                                              &hp_handle);

    if (rc != LIBUSB_SUCCESS) {
        fprintf(stderr, "Error registering hotplug callback\n");
        libusb_exit(ctx);
        return EXIT_FAILURE;
    }

    printf("Listening for USB mass storage devices...\n");

    // Main event loop
    while (1) {
        libusb_handle_events_completed(ctx, NULL);
    }

    libusb_exit(ctx);
    return EXIT_SUCCESS;
}
*/