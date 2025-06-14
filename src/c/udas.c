#include "./udas_common.h"
#include "./udas.h"


void manual()
{
	printf("\033[0;31m[WARNING] This command can not be run by user command.\033[0;0m\n");
	return;
}

USB_DEV get_dev_info(int argc, char * argv[])
{
	USB_DEV usb_dev = {"", "", "", "", ""};

	for (int i = 3; i < argc; i++)
	{
		if (strstr(argv[i], OPTION_ID_VENDOR) != NULL)
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
		else if (strstr(argv[i], OPTION_MANUFACTURER) != NULL)
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

	fprintf(stdout, "[INFO] Successfully parsing USB storage information.\n");
	return usb_dev;
}

void create_udev_rule(USB_DEV * usb_dev, char ** rule_str)
{
	char rule_line[512] = DEFAULT_UDEV_RULE;
	char idVendor[64], idProduct[64], serial[64], manufacturer[64], product[64];
	
	if (strcmp(usb_dev->idVendor, "") != 0) 
	{
		snprintf(idVendor, sizeof(idVendor), "ATTRS{idVendor}==\"%s\", ", usb_dev->idVendor);
		strcat(rule_line, idVendor);
	}
	if (strcmp(usb_dev->idProduct, "") != 0) 
	{
		snprintf(idProduct, sizeof(idProduct), "ATTRS{idProduct}==\"%s\", ", usb_dev->idProduct);
		strcat(rule_line, idProduct);
	}
	if (strcmp(usb_dev->serial, "") != 0) 
	{
		snprintf(serial, sizeof(serial), "ATTRS{serial}==\"%s\", ", usb_dev->serial);
		strcat(rule_line, serial);
	}
	if (strcmp(usb_dev->manufacturer, "") != 0) 
	{
		snprintf(manufacturer, sizeof(manufacturer), "ATTRS{manufacturer}==\"%s\", ", usb_dev->manufacturer);
		strcat(rule_line, manufacturer);
	}
	if (strcmp(usb_dev->product, "") != 0) 
	{
		snprintf(product, sizeof(product), "ATTRS{product}==\"%s\", ", usb_dev->product);
		strcat(rule_line, product);
	}

	strncpy(*rule_str, rule_line, strlen(rule_line));
	fprintf(stdout, "[INFO] Successfully create draft rule string for newly connected USB storage.\n");
}

int register_td(char ** rule_str, USB_DEV * usb_dev, int blacklist)
{
	strncat(*rule_str, (blacklist == 0) ? "ENV{UDISKS_IGNORE}=\"0\"\n" : "ENV{UDISKS_IGNORE}=\"1\"\n", strlen("ENV{UDISKS_IGNORE}=\"0\"\n"));
	fprintf(stdout, (blacklist == 1) ? "[INFO] Start registering blacklist USB Storage " : "[INFO] Start registering whitelist USB Storage ");
	fprintf(
		stdout,
		"(%s:%s): vendor - %s, produdct - %s, serial - %s\n",
		usb_dev->idVendor,
		usb_dev->idProduct,
		usb_dev->manufacturer,
		usb_dev->product,
		(strlen(usb_dev->serial) == 0) ? "Unknown": usb_dev->serial
	);
	
	FILE * rule_file = fopen((blacklist == 1) ? CUSTOM_BLACKLIST_RULE : CUSTOM_WHITELIST_RULE, "a");
	if (rule_file == NULL)
	{
		fprintf(stderr, "[ERROR] Fail to open UDAS rule file.\n");
		return EXIT_FAILURE;
	}

	// add new rule to file.
	if (fputs(*rule_str, rule_file) < 0)
	{
		fprintf(stderr, (blacklist == 1) ? "[ERROR] Fail to register blacklist device.\n" : "[ERROR] Fail to register whitelist device for new USB storage.\n");
		return EXIT_FAILURE;
	}

	fprintf(stdout, (blacklist == 1) ? "success to register blacklist device.\n" : "success to register new whitelist USB storage.\n");
	fclose(rule_file);
	return EXIT_SUCCESS;
}

int remove_td(char ** rule_str, USB_DEV * usb_dev, int blacklist)
{
	strcat(*rule_str, (blacklist == 0) ? "ENV{UDISKS_IGNORE}=\"0\"\n" : "ENV{UDISKS_IGNORE}=\"1\"\n");
	fprintf(stdout, (blacklist == 1) ? "[INFO] Start removing registered blacklist USB Storage " : "[INFO] Start removing registered whitelist USB Storage ");

	fprintf(
		stdout,
		"(%s:%s): vendor - %s, produdct - %s, serial - %s\n",
		usb_dev->idVendor,
		usb_dev->idProduct,
		usb_dev->manufacturer,
		usb_dev->product,
		(strlen(usb_dev->serial) == 0) ? "Unknown": usb_dev->serial
	);

	char buffer[512];
	char * rule_file_name = (blacklist == 0) ? CUSTOM_WHITELIST_RULE : CUSTOM_BLACKLIST_RULE ;
	char * rule_file_tmp_name = (blacklist == 0) ? CUSTOM_WHITELIST_RULE_TMP : CUSTOM_BLACKLIST_RULE_TMP ;

	FILE * rule_file = fopen(rule_file_name, "r");
	
	if (rule_file == NULL)
	{
		fprintf(stderr, "[ERROR] Can not read custom rule file.\n");
		return EXIT_FAILURE;
	}

	FILE * tmp_file = fopen(rule_file_tmp_name, "w");
	if (rule_file == NULL)
	{
		fprintf(stderr, "[ERROR] Can not open tmp rule file.\n");
		return EXIT_FAILURE;
	}

	while (fgets(buffer, sizeof(buffer), rule_file) != NULL)
	{
		if (strcmp(buffer, *rule_str) != 0)	fputs(buffer, tmp_file);
	}

	remove(rule_file_name);
	rename(rule_file_tmp_name, rule_file_name);

	fclose(rule_file);
	fclose(tmp_file);

	return EXIT_SUCCESS;
}

int search_td(char ** rule_str, USB_DEV * usb_dev)
{
	fprintf(
		stdout,
		"[INFO] Start searching registered USB Storage (%s:%s): vendor - %s, produdct - %s, serial - %s\n",
		usb_dev->idVendor,
		usb_dev->idProduct,
		usb_dev->manufacturer,
		usb_dev->product,
		(strlen(usb_dev->serial) == 0) ? "Unknown": usb_dev->serial
	);

	int match_flag = 0;
	char buffer[512];
	FILE * whitelist_file = fopen(CUSTOM_WHITELIST_RULE, "r");
	FILE * blacklist_file = fopen(CUSTOM_BLACKLIST_RULE, "r");

	if (whitelist_file == NULL)
	{
		fprintf(stderr, "[ERROR] Fail to open UDAS whitelist rule file.\n");
		return EXIT_FAILURE;
	}

	while (fgets(buffer, sizeof(buffer), whitelist_file) != NULL)
	{	
		if (strncmp(buffer, *rule_str, strlen(*rule_str)) == 0)
		{
			match_flag = 1;
			break;
		}
	}

	if (blacklist_file == NULL)
	{
		fprintf(stderr, "[ERROR] Fail to open UDAS blacklist rule file.\n");
		return EXIT_FAILURE;
	}

	while (fgets(buffer, sizeof(buffer), blacklist_file) != NULL)
	{
		if (strncmp(buffer, *rule_str, strlen(*rule_str)) == 0)
		{
			match_flag = -1;
			break;
		}
	}

	if (match_flag == 0) fprintf(stdout, "[INFO] Device is not registered in whitelist and blacklist.\n");
	else if (match_flag == 1) fprintf(stdout, "[INFO] Device is registered as whitelist.\n");
	else if (match_flag == -1) fprintf(stdout, "[INFO] Device is registered as blacklist.\n");
	return EXIT_SUCCESS;
}

int main (int argc, char * argv[])
{
	int not_filtered = -1;

	if (argc < 4)
	{
		manual();
		return EXIT_FAILURE;
	}

	if (strncmp(argv[1], "td", 2) == 0)
	{
        if ((argc != 8) && (argc != 9))
        {
            manual();
            return EXIT_FAILURE;
        }

		USB_DEV usb_dev = get_dev_info(argc, argv);
		char * rule_str = malloc(sizeof(char) * 512); 
		create_udev_rule(&usb_dev, &rule_str);
		
		if (strcmp(rule_str, DEFAULT_UDEV_RULE) != 0)
		{
			// udas td register blacklist(whitelist)
			if ((strncmp(argv[2], "register", strlen("register"))) == 0)
			{
				int types = -1 ;
				if (strncmp(argv[3], "blacklist", strlen("blacklist")) == 0) types = 1 ;
				else if(strncmp(argv[3], "whitelist", strlen("whitelist")) == 0) types = 0 ;
				
				if (types != -1)
				{
					if (register_td(&rule_str, &usb_dev, types) == EXIT_SUCCESS) not_filtered = 0;
				}
			}
			else if ((strncmp(argv[2], "search", strlen("search"))) == 0)
			{
				if (search_td(&rule_str, &usb_dev) == EXIT_SUCCESS) not_filtered = 0;
			}
			// udas td remove blacklist(whitelist)
			else if ((strncmp(argv[2], "remove", strlen("remove"))) == 0)
			{
				int types = -1 ;
				if (strncmp(argv[3], "blacklist", strlen("blacklist")) == 0) types = 1 ;
				else if(strncmp(argv[3], "whitelist", strlen("whitelist")) == 0) types = 0 ;
				if (types != -1)
				{
					if (remove_td(&rule_str, &usb_dev, types) == EXIT_SUCCESS) not_filtered =0;
				}
			}
		}

		free(rule_str);
	}
	
	else if (strncmp(argv[1], "set", 3) == 0)
	{	
		FILE * config_file = fopen(CONFIG_FILE_PATH, "r");
		FILE * config_file_tmp = fopen(CONFIG_FILE_TMP_PATH, "w");

		if ((config_file == NULL) || (config_file_tmp == NULL))
		{
			fprintf(stdout, "[ERROR] Fail to open UDAS config file.");
			return EXIT_FAILURE;
		}

		if ((strncmp(argv[2], "loglevel", strlen("loglevel"))) == 0)
		{
			if (argc == 4)
			{
				//Loglevel: Debug, Info, Warning, Critical
				char * loglevel = *(argv + 3);

				if ((strncmp(loglevel, "debug", 5) == 0) || (strncmp(loglevel, "info", 4) == 0)|| (strncmp(loglevel, "warning", 7) == 0) || (strncmp(loglevel, "critical", 8) == 0))
				{
					char buffer[256];
					while (fgets(buffer, sizeof(buffer), config_file) != NULL)
					{
						if (strncmp(buffer, "level=", 6) == 0) 
						{
							char tmp[32];
							sprintf(tmp, "level=%s\n", loglevel);
							fputs(tmp, config_file_tmp);
							continue;
						}

						fputs(buffer, config_file_tmp);
					}

					not_filtered = 0;
				}
			}
		}
		else if ((strncmp(argv[2], "passwd", strlen("passwd"))) == 0)
		{
			if (argc == 5)
			{
				// udas set passwd --old-password=pw --new-password=newpw
				char * old_password = *(argv + 3);
				char * new_password = *(argv + 4);
				
				char * token_old_pw = strtok(old_password, "=");
				token_old_pw = strtok(NULL, "=");
				sprintf(old_password, "auth_str=%s\n", token_old_pw);

				char * token_new_pw = strtok(new_password, "=");
				token_new_pw = strtok(NULL, "=");
				sprintf(new_password, "auth_str=%s\n", token_new_pw);

				char buffer[256];
				while (fgets(buffer, sizeof(buffer), config_file) != NULL)
				{
					if (strncmp(buffer, old_password, strlen(old_password)) == 0)
					{
						fputs(new_password, config_file_tmp);
						continue;
					}
					fputs(buffer, config_file_tmp);
				}

				not_filtered = 0;
			}
		}
		else if ((strncmp(argv[2], "blacklist", strlen("blacklist"))) == 0)
		{
			if (argc == 4)
			{
				/* udas set blacklist on , udas set blacklist off */
				char * blacklist = *(argv + 3);

				if ((strncmp(blacklist, "on", 2) == 0) || (strncmp(blacklist, "off", 3) == 0))
				{
					char buffer[256];
					while (fgets(buffer, sizeof(buffer), config_file) != NULL)
					{
						if (strncmp(buffer, "blacklist=", 10) == 0) 
						{
							char tmp[32];
							sprintf(tmp, "blacklist=%d\n", (strncmp(blacklist, "off", 3) == 0) ? 0 : 1 );
							fputs(tmp, config_file_tmp);
							continue;
						}

						fputs(buffer, config_file_tmp);
					}

					not_filtered = 0;
				}
			}
		}

		fclose(config_file);
		fclose(config_file_tmp);

        if (not_filtered == 0)
        {
            remove(CONFIG_FILE_PATH);
            rename(CONFIG_FILE_TMP_PATH, CONFIG_FILE_PATH);
        }
	}

	if (not_filtered == -1)
	{
	    manual();
	    return EXIT_FAILURE;
	}
	return EXIT_SUCCESS;
}
