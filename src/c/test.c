#include "./udas_detector.h"


static int new_device_detected_cb(libusb_context * ctx, libusb_device * device, 
                                libusb_hotplug_event event, void *user_data)
{
    int is_mass_storage = 0;

    // declare device descriptor struct.
    struct libusb_device_descriptor desc;

    // get newly connected device' descriptor: success(0), fail(minus int)
    int r = libusb_get_device_descriptor(device, &desc);

    if ((r != LIBUSB_SUCCESS) || (&desc == NULL)) {
        fprintf(stderr, "[ERROR] Can not get a device descriptor\n");
        return EXIT_SUCCESS;
    }

    // check 0x80 for desc.bDeviceClass

    // get detail information for 0x00
    if (desc.bDeviceClass == 0x00) {
        // declare device config descriptor struct.
        struct libusb_config_descriptor * cfg_desc = NULL;

        // get device first config information (usually one config). success(0), fail(minux int)
        r = libusb_get_config_descriptor(device, 0, &cfg_desc);
        
        if ((r != LIBUSB_SUCCESS) || (cfg_desc == NULL)) {
            fprintf(stderr, "[ERROR] Can not get a device config.\n");
            return EXIT_SUCCESS; 
        }

        // loop to get USB interface information.
        for (int i = 0; i < cfg_desc->bNumInterfaces; i++) {
            // declare interface struct to get altsettings in device.
            const struct libusb_interface * inf = (&cfg_desc->interface)[i];

            // to get interface descriptor, search altsettings information.
            for (int j = 0; j < inf->num_altsetting; j++) {

                // declare interface descriptor struct
                struct libusb_interface_descriptor inf_desc = (inf->altsetting)[j];
                
                if (inf_desc.bInterfaceClass == 0x08) {
                    fprintf(stdout, "[INFO] New USB storage is connected.\n");
                    is_mass_storage = 1;
                    break;
                }
            }
        }

        libusb_free_config_descriptor(cfg_desc);
    }
    else if (desc.bDeviceClass == 0x08) {
        fprintf(stdout, "[INFO] New USB storage is connected.\n");
        is_mass_storage = 1;
    }

    if (is_mass_storage)
    {
        printf("check udev rule\n");
        // device, desc 전달인자 함수 생성
        // 해당 함수 내에서 디바이스 오픈 후, USB 정보를 출력 및 struct 저장 후 반환. 

        // 반환 struct를 인자로 하는 함수에서 rule 확인.
        // Rule이 없는 경우, Python window 실행
    }
    
    return EXIT_SUCCESS;
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
        fprintf(stderr, "[ERROR] This libusb library does not provide hotplug.\n");
        libusb_exit(ctx);
        return EXIT_FAILURE;
    }

    int result =libusb_hotplug_register_callback(ctx, 
                                                 LIBUSB_HOTPLUG_EVENT_DEVICE_ARRIVED, 
                                                 0, 
                                                 LIBUSB_HOTPLUG_MATCH_ANY, 
                                                 LIBUSB_HOTPLUG_MATCH_ANY, 
                                                 LIBUSB_HOTPLUG_MATCH_ANY, 
                                                 new_device_detected_cb,
                                                 NULL, 
                                                 &handler);

    if (result != LIBUSB_SUCCESS)
    {
        fprintf(stderr, "[ERROR] Fail to registering hotplug callback\n");
        libusb_exit(ctx);
        return EXIT_FAILURE;
    }

    printf("Listening for USB mass storage devices...\n");

    // Event Listening.
    while (1) 
    {
        int result = libusb_handle_events_completed(ctx, NULL);
    }

    libusb_exit(ctx);
    return EXIT_SUCCESS;
}


/*
static int hotplug_callback(struct libusb_context *ctx, struct libusb_device *dev,
                            libusb_hotplug_event event, void *user_data) 
{
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
*/