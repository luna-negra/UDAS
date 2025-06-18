from udas.udas_pytool import (QMainWindow,
                              QApplication,
                              ConfigIni,
                              centralise_fixed,
                              change_allow_ns,
                              change_blacklist,
                              change_loglevel,
                              clear_layout,
                              create_menubar,
                              get_rules,
                              get_rule_num,
                              get_service_status,
                              remove_registered_usb_info,
                              sys,)
from udas.udas_custom_widget import (COLOR_SEPARATE_LINE,
                                     CustomComboboxWithButton,
                                     CustomDialogPasswordChange,
                                     CustomDialogPasswordInput,
                                     CustomLabelWithButton,
                                     CustomLogViewer,
                                     CustomTableWithOneButton,
                                     custom_box_layout,
                                     custom_push_button,
                                     custom_label,
                                     custom_labels_kv,
                                     custom_separate_line,
                                     custom_splitter_fixed,
                                     custom_widget_for_layout,
                                     CustomMessageBox,
                                     partial,)


DIALOG_PASSWORD_TITLE: str = "UDAS Authentication"
DIALOG_PASSWORD_WIDTH: int = 400
DIALOG_PASSWORD_HEIGHT: int = 200
DIALOG_PASSWORD_CHANGE_WIDTH: int = 500
DIALOG_PASSWORD_CHANGE_HEIGHT: int = 200
MAIN_WINDOW_TITLE: str = "USB Docking Authentication System"
MAIN_WINDOW_WIDTH: int = 600
MAIN_WINDOW_HEIGHT: int = 450
WIDGET_SIDEBAR_WIDTH: int = 150
WIDGET_SIDEBAR_HEIGHT: int = MAIN_WINDOW_HEIGHT
WIDGET_SIDEBAR_STYLE: str = "border: 1px solid #333;"
WIDGET_MAIN_CONTENT_WIDTH: int = MAIN_WINDOW_WIDTH - WIDGET_SIDEBAR_WIDTH
WIDGET_MAIN_CONTENT_HEIGHT: int = MAIN_WINDOW_HEIGHT
BUTTON_SIDEBAR_WIDTH: int = WIDGET_SIDEBAR_WIDTH
BUTTON_SIDEBAR_HEIGHT: int = 50
BUTTON_SIDEBAR_STYLE: str = """
    QPushButton {
        border: 2px solid "#555";
        border-radius: 5px;
        font-size=25pt;
    }
    QPushButton:hover {
        background-color: #f40;
        font-weight: 600;
    }
"""
BUTTON_GENERAL_STYLE: str = BUTTON_SIDEBAR_STYLE
LAYOUT_MAIN_CONTENT_MARGIN:int = 20
LOG_WINDOW_WIDTH: int = WIDGET_MAIN_CONTENT_WIDTH - 2 * LAYOUT_MAIN_CONTENT_MARGIN
LOG_WINDOW_HEIGHT: int = 330


class MainWindow(QMainWindow):
    def __init__(self, **kwargs):
        super().__init__()

        # set window structure
        self.__init_ui(kwargs)

        # display main screen.
        self.__main()

    def __change_allow_ns_settings(self, current_value):
        cmd_result = change_allow_ns(opt="off" if current_value == 1 else "on")
        if cmd_result.returncode == 0:
            self.__settings()
        return None

    def __change_blacklist_setting(self, current_value:int):
        cmd_result = change_blacklist(opt="off" if current_value == 1 else "on")
        if cmd_result.returncode == 0:
            self.__settings()
        return None

    def __change_loglevel(self, combobox, item_list: list):
        cmd_result = change_loglevel(item_list[combobox.currentIndex()].lower())
        if cmd_result.returncode == 0:
            self.__settings()
        return None

    def __change_password(self):
        # set size
        button_width: int = 200
        height: int = 30;
        line_edit_width: int = 220

        dialog = CustomDialogPasswordChange(title="Change UDAS Password",
                                            total_width=DIALOG_PASSWORD_CHANGE_WIDTH,
                                            total_height=DIALOG_PASSWORD_CHANGE_HEIGHT,
                                            ratio=0.4,
                                            label_text="Change the UDAS Password.",
                                            label_width=line_edit_width,
                                            label_height=height,
                                            button_width=button_width,)
        dialog.exec()

    def __create_menubar(self):
        # define menubar structure
        menu: dict = {
            "icon": "",
            "menus":
                {
                    "File":
                        {
                            "icon": "",
                            "menus": {},
                            "actions": [
                                {"name": "exit", "shortcut": "Ctrl+F4", "icon": "", "status": "Exit UDAS", "connect": self.__exit},
                            ]
                        },
                    "Help":
                        {
                            "icon": "",
                            "menus": {},
                            "actions": [
                                {"name": "help", "shortcut": "F1", "icon": "", "status": "Help", "connect": None},
                                {"name": "about", "shortcut": "F2", "icon": "", "status": "About", "connect": None},
                            ]
                        }
                },
            "actions": []
        }

        # apply menu structure.
        create_menubar(p_menu=self.menuBar(), menu_structure=menu, widget=self)

    def __create_sidebar(self):
        children_widget_info: dict = {
            "MAIN": {
                "status": "Display status summary...",
                "style": BUTTON_SIDEBAR_STYLE,
                "connect": self.__main,
            },
            "MANAGEMENT": {
                "status": "Manage registered USB devices...",
                "style": BUTTON_SIDEBAR_STYLE,
                "connect": self.__mgmt,
            },
            "SETTINGS": {
                "status": "UDAS settings...",
                "style": BUTTON_SIDEBAR_STYLE,
                "connect": self.__settings,
            },
            "LOG": {
                "status": "Check process logs...",
                "style": BUTTON_SIDEBAR_STYLE,
                "connect": self.__log,
            },
        }

        children_btns = [ custom_push_button(text=text,
                                             width=BUTTON_SIDEBAR_WIDTH,
                                             height=BUTTON_SIDEBAR_HEIGHT,
                                             status_tip=config.get("status") or None,
                                             style=config.get("style") or BUTTON_SIDEBAR_STYLE,
                                             connect=config.get("connect") or None) for text, config in children_widget_info.items()]

        layout_sidebar = custom_box_layout(children=children_btns,
                                           align="top",
                                           margin_l=0,
                                           margin_t=10)

        self.widget_sidebar.setLayout(layout_sidebar)
        return None

    def __init_statusbar(self):
        menu = self.statusBar()
        menu.setStyleSheet("color: #777;")
        return

    def __init_ui(self, kwargs):
        self.setWindowTitle(kwargs.get("title"))
        centralise_fixed(self, kwargs.get("width"), kwargs.get("height"))

        self.__create_menubar()
        self.__init_statusbar()
        self.__set_layout()
        return None

    def __exit(self):
        sys.exit(0)

    def __log(self):
        clear_layout(self.widget_main_content)

        log_viewer = CustomLogViewer(total_width=LOG_WINDOW_WIDTH,
                                     total_height=WIDGET_MAIN_CONTENT_HEIGHT - 100,
                                     text_edit_height=LOG_WINDOW_HEIGHT,
                                     button_style=BUTTON_GENERAL_STYLE)

        layout = custom_box_layout(children=[log_viewer],
                                   margin_l=LAYOUT_MAIN_CONTENT_MARGIN,
                                   margin_t=LAYOUT_MAIN_CONTENT_MARGIN,)

        self.widget_main_content.setLayout(layout)
        return None

    def __main(self):
        clear_layout(self.widget_main_content)

        # get KPI data.
        status_data: dict = self.__read_status_kpi_data()
        service_data: dict = self.__read_service_kpi_data()

        # set the size of widgets
        key_width: float = 0.5
        total_width_half: int = int(WIDGET_MAIN_CONTENT_WIDTH * key_width)
        height: int = 30

        # status widgets and layout
        label_status_preamble = custom_label(text="<b>KPI of UDAS Rule</b>",
                                             width=WIDGET_MAIN_CONTENT_WIDTH,
                                             height=height)
        label_status_whitelist = custom_labels_kv(total_width=total_width_half,
                                                  height=height,
                                                  ratio=key_width,
                                                  key="Whitelist",
                                                  value=status_data.get("whitelist"),
                                                  align="center"
                                                  )
        label_status_blacklist = custom_labels_kv(total_width=total_width_half,
                                                  height=height,
                                                  ratio=key_width,
                                                  key="Blacklist",
                                                  value=status_data.get("blacklist"))
        layout_status_info = custom_box_layout(children=[label_status_whitelist, label_status_blacklist],
                                               vertical=False,
                                               margin_l=0,
                                               margin_t=0)

        # service widgets and layout
        label_service_preamble = custom_label(text="<b>Status of UDAS Service</b>",
                                             width=WIDGET_MAIN_CONTENT_WIDTH,
                                             height=height)
        label_service_status = custom_labels_kv(total_width=WIDGET_MAIN_CONTENT_WIDTH,
                                                height=height,
                                                ratio=key_width,
                                                key="STATUS",
                                                value=service_data.get("is_running"),
                                                align="center")
        label_service_start = custom_labels_kv(total_width=WIDGET_MAIN_CONTENT_WIDTH,
                                                height=height,
                                                ratio=key_width,
                                                key="START DATETIME",
                                                value=service_data.get("start_dt"),
                                                align="center")
        label_service_uptime = custom_labels_kv(total_width=WIDGET_MAIN_CONTENT_WIDTH,
                                                height=height,
                                                ratio=key_width,
                                                key="UPTIME",
                                                value=service_data.get("uptime"))

        layout_status = custom_box_layout(children=[label_status_preamble, layout_status_info], )
        layout_service = custom_box_layout(children=[label_service_preamble,
                                                     label_service_status,
                                                     label_service_start,
                                                     label_service_uptime],)
        layout = custom_box_layout(children=[layout_status,
                                             custom_separate_line(color=COLOR_SEPARATE_LINE),
                                             layout_service],
                                   margin_l=LAYOUT_MAIN_CONTENT_MARGIN,
                                   margin_t=LAYOUT_MAIN_CONTENT_MARGIN,)
        self.widget_main_content.setLayout(layout)
        return None

    def __mgmt(self):
        clear_layout(self.widget_main_content)

        # set the size of widgets
        button_width = 140
        height = 30
        margin = 20
        table_height = 100
        table_header = ["Vendor", "Product", "Serial", ]
        width = WIDGET_MAIN_CONTENT_WIDTH - LAYOUT_MAIN_CONTENT_MARGIN * 2

        widget_table_button_blacklist = CustomTableWithOneButton(
            total_width=width,
            label_height=height,
            label_text="<b>BLACKLIST</b>",
            table_height=table_height,
            table_header=table_header,
            table_data=get_rules(is_white=False),
            ratio=0.7,
            align="right",
            button_width=button_width,
            button_height=height,
            button_text="Remove Blacklist",
            button_style=BUTTON_GENERAL_STYLE,
            button_enable=False,
            button_status_tip="Remove selected blacklist...",
            button_connect=lambda: self.__remove_registered_rule(table=widget_table_button_blacklist.table, blacklist=True)
        )

        widget_table_button_whitelist = CustomTableWithOneButton(
            total_width=width,
            label_height=height,
            label_text="<b>WHITELIST</b>",
            table_height=table_height,
            table_header=table_header,
            table_data=get_rules(),
            ratio=0.7,
            align="right",
            button_width=button_width,
            button_height=height,
            button_text="Remove Whitelist",
            button_style=BUTTON_GENERAL_STYLE,
            button_enable=False,
            button_status_tip="Remove selected whitelist...",
            button_connect=lambda: self.__remove_registered_rule(table=widget_table_button_whitelist.table),
        )

        layout_test = custom_box_layout(children=[widget_table_button_blacklist,
                                                  custom_separate_line(color=COLOR_SEPARATE_LINE),
                                                  widget_table_button_whitelist],
                                        margin_l=margin,
                                        margin_t=margin,
                                        margin_r=margin,
                                        margin_b=margin)

        self.widget_main_content.setLayout(layout_test)
        return None

    def __remove_registered_rule(self, table, blacklist:bool=False) -> None:
        selected_item: list = table.selectedItems()

        if len(selected_item) == 0:
            return None

        row: int = table.currentRow()
        manufacturer, id_vendor = [text.strip("()") for text in selected_item[0].text().split()]
        product, id_product = [text.strip("()") for text in selected_item[1].text().split()]
        serial = selected_item[2].text()

        cmd_result = remove_registered_usb_info(id_vendor=id_vendor,
                                                id_product=id_product,
                                                serial=serial,
                                                manufacturer=manufacturer,
                                                product=product,
                                                blacklist=blacklist, )

        # exit_code:
        # 0 - OK,
        # 1 - Error with command usage,
        # 126 - cancelled,
        # 127 - Not exist command
        exit_code = cmd_result.returncode
        if exit_code == 0:
            table.removeRow(row)
            CustomMessageBox(msg_box_text="Success to remove registered device",
                             msg_box_type="information",).exec()

        elif exit_code == 1:
            CustomMessageBox(msg_box_text="[ERROR] Wrong command format.",
                             msg_box_type="critical").exec()

        elif exit_code == 127:
            CustomMessageBox(msg_box_text="[ERROR] Can not use UDAS command in your machine.",
                             msg_box_type="critical").exec()

        else:
            pass

        return None

    def __read_status_kpi_data(self) -> dict:
        return {
            "whitelist": get_rule_num(),
            "blacklist": get_rule_num(is_white=False),
        }

    def __read_service_kpi_data(self):
        service_data = get_service_status()
        return {
            "is_running": service_data.get("is_running"),
            "start_dt": service_data.get("start_dt"),
            "uptime": service_data.get("uptime")
        }

    def __settings(self):
        clear_layout(self.widget_main_content)

        # get data
        config = ConfigIni()
        service_data = self.__read_service_kpi_data()

        # set the size of widgets
        total_width = WIDGET_MAIN_CONTENT_WIDTH
        button_width: int = 80
        combobox_width: int = 120
        height: int = 30
        item_list: list = ["ERROR", "WARNING", "INFO", "DEBUG"]

        label_settings_preamble = custom_label(text="<b>UDAS Settings</b>",
                                               width=total_width,
                                               height=30)

        widget_layout_ctrl_service = CustomLabelWithButton(total_width=total_width,
                                                           height=height,
                                                           ratio=0.7,
                                                           label_text="UDAS Service [On / Off]",
                                                           button_width=button_width,
                                                           button_text="OFF" if "running" in service_data.get("is_running") else "On",
                                                           button_style=BUTTON_GENERAL_STYLE,
                                                           button_status_tip="Run or Stop UDAS Detecting Service...")

        widget_layout_ctrl_blacklist = CustomLabelWithButton(total_width=total_width,
                                                            height=height,
                                                            ratio=0.7,
                                                            label_text="Apply Blacklist Policy [On / Off]",
                                                            button_width=button_width,
                                                            button_text="OFF" if config.get_blacklist() else "ON",
                                                            button_style=BUTTON_GENERAL_STYLE,
                                                            button_status_tip="Edit blacklist setting...",
                                                            connect=partial(self.__change_blacklist_setting,
                                                                            current_value=config.get_blacklist()),)

        widget_layout_ctrl_allow_ns = CustomLabelWithButton(total_width=total_width,
                                                            height=height,
                                                            ratio=0.7,
                                                            label_text="Allow Non Serial Device [On / Off]",
                                                            button_width=button_width,
                                                            button_text="OFF" if config.get_allow_ns() else "ON",
                                                            button_style=BUTTON_GENERAL_STYLE,
                                                            button_status_tip="Edit allow non serial number device...",
                                                            connect=partial(self.__change_allow_ns_settings,
                                                                            current_value=config.get_allow_ns()), )

        widget_layout_ctrl_password = CustomLabelWithButton(total_width=total_width,
                                                            height=height,
                                                            ratio=0.7,
                                                            label_text="Change UDAS Password",
                                                            button_width=button_width,
                                                            button_text="Change",
                                                            button_style=BUTTON_GENERAL_STYLE,
                                                            button_status_tip="Change UDAS Password...",
                                                            connect=self.__change_password)

        label_logging_preamble = custom_label(text="<b>Logging</b>", width=total_width, height=30)

        widget_layout_ctrl_loglevel = CustomComboboxWithButton(total_width=total_width,
                                                               total_height=height,
                                                               ratio=0.4,
                                                               label_text="UDAS Log Level",
                                                               combobox_width=combobox_width,
                                                               combobox_items=item_list,
                                                               combobox_default=config.get_log_level(),
                                                               button_width=button_width,
                                                               button_text="Apply",
                                                               button_status_tip="Change log level...",
                                                               button_style=BUTTON_GENERAL_STYLE,
                                                               button_connect=lambda: self.__change_loglevel(
                                                                   combobox=widget_layout_ctrl_loglevel.combobox,
                                                                   item_list=item_list),)

        layout = custom_box_layout(children=[label_settings_preamble,
                                             widget_layout_ctrl_service,
                                             widget_layout_ctrl_allow_ns,
                                             widget_layout_ctrl_blacklist,
                                             widget_layout_ctrl_password,
                                             custom_separate_line(color=COLOR_SEPARATE_LINE),
                                             label_logging_preamble,
                                             widget_layout_ctrl_loglevel],
                                   margin_l=LAYOUT_MAIN_CONTENT_MARGIN,
                                   margin_t=LAYOUT_MAIN_CONTENT_MARGIN,)

        self.widget_main_content.setLayout(layout)
        return None

    def __set_layout(self):
        # create widget for sizing
        self.widget_sidebar = custom_widget_for_layout(width=WIDGET_SIDEBAR_WIDTH,
                                                       height=WIDGET_SIDEBAR_HEIGHT,
                                                       style=WIDGET_SIDEBAR_STYLE,)
        self.widget_main_content = custom_widget_for_layout(width=WIDGET_MAIN_CONTENT_WIDTH,
                                                            height=WIDGET_MAIN_CONTENT_HEIGHT,)

        # create sidebar
        self.__create_sidebar()

        # create and apply central widget to main layout
        central_widget = custom_splitter_fixed(widget_list=[self.widget_sidebar,
                                                            self.widget_main_content])
        self.setCentralWidget(central_widget)
        return None


if __name__ == "__main__":
    app = QApplication()

    # if cancelled , entire process will be terminated.
    pw_dialog = CustomDialogPasswordInput(title=DIALOG_PASSWORD_TITLE,
                                          width=DIALOG_PASSWORD_WIDTH,
                                          height=DIALOG_PASSWORD_HEIGHT)
    pw_dialog.exec()

    # main window.
    window = MainWindow(title="USB Docking Authentication System",
                        width=MAIN_WINDOW_WIDTH,
                        height=MAIN_WINDOW_HEIGHT)

    window.show()
    sys.exit(app.exec())