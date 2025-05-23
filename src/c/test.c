
// install from apt-get: libusb-1.0.0-dev
#include <libusb-1.0/libusb.h> 
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <string.h>


#define TRUSTED_FILE "trusted_devices.txt"


void usb_device_detected()
{
    libusb_device ** devices;
    libusb_context *context;
    int r;
    ssize_t cnt;

    r = libusb_init(&context);
    if (r < 0)
    {
        printf("Fail to initialize libusb.\n");
        return;
    }

    cnt = libusb_get_device_list(context, &devices);
    if (cnt < 0) {
        printf("Error getting device list\n");
        return;
    }

    for (ssize_t i = 0; i < cnt; i++) 
    {
        struct libusb_device_descriptor desc;
        libusb_device *device = devices[i];
        r = libusb_get_device_descriptor(device, &desc);
        if (r < 0) continue;

        int is_mass_storage = 0;

        if (desc.bDeviceClass == LIBUSB_CLASS_MASS_STORAGE) {
            is_mass_storage = 1;
        } 
        else if (desc.bDeviceClass == 0x00) {
            // Device class unspecified, 확인 필요
            struct libusb_config_descriptor *config;
            r = libusb_get_config_descriptor(device, 0, &config);
            if (r == 0) {
                for (int i = 0; i < config->bNumInterfaces && !is_mass_storage; i++) {
                    const struct libusb_interface *interface = &config->interface[i];
                    for (int j = 0; j < interface->num_altsetting && !is_mass_storage; j++) {
                        const struct libusb_interface_descriptor *inter_desc = &interface->altsetting[j];
                        if (inter_desc->bInterfaceClass == LIBUSB_CLASS_MASS_STORAGE) {
                            printf("TEST\n");
                            is_mass_storage = 1;
                            break;
                        }
                    }
                }
                libusb_free_config_descriptor(config);
            }
        }

        if (is_mass_storage) 
        {
            printf("Mass Storage USB device detected (Vendor ID: %04x, Product ID: %04x)\n", desc.idVendor, desc.idProduct);
        }
    }
}


int main(int argc, char * argv []) 
{
    usb_device_detected();
    return 0;
}


/*
void save_trusted_device(uint16_t vendor_id, uint16_t product_id) {
    FILE *fp = fopen(TRUSTED_FILE, "a");
    if (fp != NULL) {
        fprintf(fp, "%04x:%04x\n", vendor_id, product_id);
        fclose(fp);
        printf("Device saved to trusted list.\n");
    } else {
        printf("Failed to save trusted device.\n");
    }
}

void usb_device_detected() {
    libusb_device **devices;
    libusb_context *context = NULL;
    int r;
    ssize_t cnt;

    r = libusb_init(&context);
    if (r < 0) {
        printf("libusb initialization failed\n");
        return;
    }

    cnt = libusb_get_device_list(context, &devices);
    if (cnt < 0) {
        printf("Error getting device list\n");
        return;
    }

    for (ssize_t i = 0; i < cnt; i++) {
        struct libusb_device_descriptor desc;
        libusb_device *device = devices[i];

        r = libusb_get_device_descriptor(device, &desc);
        if (r < 0) {
            continue;
        }

        printf("USB device detected (Vendor ID: %04x, Product ID: %04x)\n", desc.idVendor, desc.idProduct);

        char response;
        printf("Do you trust this device? (y/n): ");
        scanf(" %c", &response);

        if (response == 'y' || response == 'Y') {
            printf("Launching password verification...\n");

            // Python 또는 Ruby 버전 중 택1
            int pw_result = system("python3 check_password.py"); // Python
            // int pw_result = system("ruby check_password.rb"); // Ruby

            if (pw_result == 0) {
                save_trusted_device(desc.idVendor, desc.idProduct);
            } else {
                printf("Password incorrect. Device not trusted.\n");
            }
        } else {
            printf("Device not trusted. Access denied.\n");
        }
    }

    libusb_free_device_list(devices, 1);
    libusb_exit(context);
}

int main() {
    while (1) {
        usb_device_detected();
        sleep(5);
    }
    return 0;
}


*/