#include "./udas.h"


void manual()
{
	printf("[ udas ]\n");
	printf("\n** This is a Manual **\n");
	return;
}

USB_DEV get_dev_info(int argc, char * argv[])
{
	USB_DEV usb_dev = {"", "", "", "", ""};

	for (int i = 3; i < argc; i++)
	{
		if (strstr(argv[i], OPTION_ID_VENDOER) != NULL)
		{
			char * token = strtok(argv[i], OPTION_DELIMITER);
			token = strtok(NULL, OPTION_DELIMITER);
			if (strncmp(token, UNKNOWN, sizeof(UNKNOWN)) != 0) strcpy(usb_dev.idVendor, token);	
		}
		else if (strstr(argv[i], OPTION_ID_PRODUCT) != NULL)
		{
			char * token = strtok(argv[i], OPTION_DELIMITER);
			token = strtok(NULL, OPTION_DELIMITER);
			if (strncmp(token, UNKNOWN, sizeof(UNKNOWN)) != 0) strcpy(usb_dev.idProduct, token);	
		}
		else if (strstr(argv[i], OPTION_SERIAL) != NULL)
		{
			char * token = strtok(argv[i], OPTION_DELIMITER);
			token = strtok(NULL, OPTION_DELIMITER);
			if (strncmp(token, UNKNOWN, sizeof(UNKNOWN)) != 0) strcpy(usb_dev.serial, token);	
		}
		else if (strstr(argv[i], OPION_MANUFACTURER) != NULL)
		{
			char * token = strtok(argv[i], OPTION_DELIMITER);
			token = strtok(NULL, OPTION_DELIMITER);
			if (strncmp(token, UNKNOWN, sizeof(UNKNOWN)) != 0) strcpy(usb_dev.manufacturer, token);	
		}
		else if (strstr(argv[i], OPTION_PRODUCT) != NULL)
		{
			char * token = strtok(argv[i], OPTION_DELIMITER);
			token = strtok(NULL, OPTION_DELIMITER);
			if (strncmp(token, UNKNOWN, sizeof(UNKNOWN)) != 0) strcpy(usb_dev.product, token);	
		}
	}

	return usb_dev;
}

int add_td(USB_DEV * usb_dev_ptr)
{
	fprintf(
		stdout, 
		"Try to register new device (%s:%s) as a trusted: Vendor - %s, Product - %s, SerialNumber - %s\n", 
		usb_dev_ptr->idVendor,
		usb_dev_ptr->idProduct,
		usb_dev_ptr->manufacturer,
		usb_dev_ptr->product,
		(strlen(usb_dev_ptr->serial)) ? usb_dev_ptr->serial: "Unknown"
	);

	USB_DEV tmp = *usb_dev_ptr;
	FILE * rule_file = fopen("/etc/udev/rules.d/99-udas.custom.rules", "a");
	char rule_line[512] = "ACTION==\"add\", SUBSYSTEM==\"block\", ";
	char tmpstr[128];

	if (strlen(usb_dev_ptr->idVendor))
	{
		snprintf(tmpstr, sizeof(tmpstr), "ATTRS{idVendor}==\"%s\", ", usb_dev_ptr->idVendor);
		strcat(rule_line, tmpstr);
	}

	if (strlen(usb_dev_ptr->idProduct))
	{
		snprintf(tmpstr, sizeof(tmpstr), "ATTRS{idProduct}==\"%s\", ", usb_dev_ptr->idProduct);
		strcat(rule_line, tmpstr);
	}

	if (strlen(usb_dev_ptr->serial))
	{
		snprintf(tmpstr, sizeof(tmpstr), "ATTRS{serial}==\"%s\", ", usb_dev_ptr->serial);
		strcat(rule_line, tmpstr);
	}

	if (strlen(usb_dev_ptr->manufacturer))
	{
		snprintf(tmpstr, sizeof(tmpstr), "ATTRS{manufacturer}==\"%s\", ", usb_dev_ptr->manufacturer);
		strcat(rule_line, tmpstr);
	}

	if (strlen(usb_dev_ptr->product))
	{
		snprintf(tmpstr, sizeof(tmpstr), "ATTRS{product}==\"%s\", ", usb_dev_ptr->product);
		strcat(rule_line, tmpstr);
	}

	strcat(rule_line, "ENV{UDISKS_IGNORE}=\"0\"\n");
	int result = fputs(rule_line, rule_file);
	(result == EOF) ?
	fprintf(stderr, "[ERROR] Fail to register new USB storage device as a trusted.\n"):
	fprintf(stdout, "Success to register new USB storage as a trusted\n");

	fclose(rule_file);
	return EXIT_SUCCESS;
}

int main (int argc, char * argv[])
{
	if (argc < 3)
	{
		manual();
		return EXIT_FAILURE;
	}
	
	if (!(strcmp(argv[1], "td")))
	{
		USB_DEV usb_dev;

		if (argc >= 5)
		{
			usb_dev = get_dev_info(argc, argv);
		}

		// udas td add --idVendor=abcd --idProduct=0123 --manufacturer="SMI Corporation" --product="usb disk" --model="usb disk        " --serial=ABCDEFGEHIDKF
		if (!(strcmp(argv[2], "add")))
		{
			if (add_td(&usb_dev) == EXIT_SUCCESS) return 0;
			
		}
		// udas td search --idVendor=abcd --idProduct=0123 --manufacturer="SMI Corporation" --product="usb disk" --serial=ABCDEFGEHIDKF
		else if (!(strcmp(argv[2], "search")))
		{
			printf("01\n");
			return 0;
		}
		// udas td remove --idVendor=abcd --idProduct=0123 --manufacturer="SMI Corporation" --product="usb disk" --serial=ABCDEFGEHIDKF
		else if (!(strcmp(argv[2], "remove")))
		{
			printf("02\n");
			return 0;
		}
	}
	
	else if (!(strcmp(argv[1], "set")))
	{	
		if (argc >= 5)
		{
			if (!(strcmp(argv[2], "loglevel")))
			{
				printf("10\n");
				return 0;
			}
			else if (!(strcmp(argv[2], "mount")))
			{
				printf("11\n");
				return 0;
			}
			else if (!(strcmp(argv[2], "mod")))
			{
				printf("12\n");
				return 0;
			}
		}
	}

	manual();
	return EXIT_SUCCESS;
}