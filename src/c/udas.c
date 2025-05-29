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

	return usb_dev;
}

void create_udev_rule(int argc, char * argv [], char ** rule_str)
{
	char rule_line[512] = DEFAULT_UDEV_RULE;
	char tmpstr[128];

	for (int i = 3; i < argc ; i++)
	{
		char * token = strtok(argv[i], OPTION_DELIMITER);
		char buffer[64];

		if (strcmp(token, OPTION_ID_VENDOR) == 0) 
		{
			token = strtok(NULL, OPTION_DELIMITER);
			if (strncmp(token, "Unknown", sizeof("Unknown")) == 0)  continue;

			snprintf(buffer, sizeof(buffer), "ATTRS{idVendor}==\"%s\", ", token);
			strcat(rule_line, buffer);
		}
		else if (strcmp(token, OPTION_ID_PRODUCT) == 0)
		{
			token = strtok(NULL, OPTION_DELIMITER);
			if (strncmp(token, "Unknown", sizeof("Unknown")) == 0) continue;
			
			snprintf(buffer, sizeof(buffer), "ATTRS{idProduct}==\"%s\", ", token);
			strcat(rule_line, buffer);
		}
		else if (strcmp(token, OPTION_SERIAL) == 0)
		{
			token = strtok(NULL, OPTION_DELIMITER);
			if (strncmp(token, "Unknown", sizeof("Unknown")) == 0) continue;
			
			snprintf(buffer, sizeof(buffer), "ATTRS{serial}==\"%s\", ", token);
			strcat(rule_line, buffer);
		}
		else if (strcmp(token, OPTION_MANUFACTURER) == 0)
		{
			token = strtok(NULL, OPTION_DELIMITER);
			if (strncmp(token, "Unknown", sizeof("Unknown")) == 0)  continue;

			snprintf(buffer, sizeof(buffer), "ATTRS{manufacturer}==\"%s\", ", token);
			strcat(rule_line, buffer);
		}
		else if (strcmp(token, OPTION_PRODUCT) == 0)
		{
			token = strtok(NULL, OPTION_DELIMITER);
			if (strncmp(token, "Unknown", sizeof("Unknown")) == 0) continue;

			snprintf(buffer, sizeof(buffer), "ATTRS{product}==\"%s\", ", token);
			strcat(rule_line, buffer);
		}
	}

	strncat(rule_line, OPTION_MOUTN_ENV, sizeof(OPTION_MOUTN_ENV));
	strncpy(*rule_str, rule_line, sizeof(rule_line));	
}

int register_td(char ** rule_str)
{
	FILE * rule_file = fopen(CUSTOM_DEFAULT_RULE, "a");
	if (rule_file == NULL)
	{
		fprintf(stderr, "[ERROR] Fail to open UDAS rule file.\n");
		return EXIT_FAILURE;
	}

	int result = fputs(*rule_str, rule_file);
	if (result < 0)
	{
		fprintf(stderr, "[ERROR] Fail to register trusted device for new USB storage\n");
		return EXIT_FAILURE;
	}

	fprintf(stdout, "success\n");
	fclose(rule_file);	
	return EXIT_SUCCESS;
}

int remove_td(char ** rule_str)
{

	return EXIT_SUCCESS;
}

int search_td(char ** rule_str)
{
	int match_flag = -1;
	char buffer[512];
	FILE * rule_file = fopen(CUSTOM_DEFAULT_RULE, "r");
	if (rule_file == NULL)
	{
		fprintf(stderr, "[ERROR] Fail to open UDAS rule file.\n");
		return EXIT_FAILURE;
	}

	while (fgets(buffer, sizeof(buffer), rule_file) != NULL)
	{	
		if (strcmp(*rule_str, buffer) == 0)
		{
			match_flag = 0;
			break;
		}
	}

	(match_flag == -1) ? fprintf(stdout, "[INFO] device not found\n") : fprintf(stdout, "[INFO] registered device\n");
	return EXIT_SUCCESS;
}

int main (int argc, char * argv[])
{
	int not_filtered = -1;

	if (argc < 3)
	{
		manual();
		return EXIT_FAILURE;
	}
	
	if (strcmp(argv[1], "td") == 0)
	{
		char * rule_str = malloc(sizeof(char) * 512); 			// 2025.05.29 : change logic
		create_udev_rule(argc, argv, &rule_str);    			// 2025.05.29 : change logic
		
		if (strcmp(rule_str, DEFAULT_UDEV_RULE) != 0)
		{
			if ((strcmp(argv[2], "register")) == 0)
			{
				if (register_td(&rule_str) == EXIT_SUCCESS)	not_filtered = 0;
			}
			else if (!(strcmp(argv[2], "search")))
			{
				if (search_td(&rule_str) == EXIT_SUCCESS) not_filtered = 0;
			}
			else if (!(strcmp(argv[2], "remove")))
			{
				if (remove_td(&rule_str) == EXIT_SUCCESS) not_filtered =0;
			}
		}

		free(rule_str);
	}
	
	else if (strcmp(argv[1], "set") == 0)
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

	if (not_filtered == -1) manual();
	return EXIT_SUCCESS;
}