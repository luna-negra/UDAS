"""
from udas.udas_pytool import (sys,
                             Qt,
                             QApplication,
                             QMainWindow,
                             QWidget,
                             QSplitter,
                             QVBoxLayout,
                             QHBoxLayout,
                             QMenu,
                             QAction,
                             QIcon,
                             QKeySequence,
                             QPushButton,
                             QLabel,
                             BUTTON_STYLE,
                             ConfigIni,
                             centralise,
                             clear_layout,
                             get_separate_line,
                             )


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # set title of main window
        self.setWindowTitle("UDAS")

        # centralize
        centralise(self, 600, 400)

        # set ui
        self.__init_ui()

    def __init_ui(self):
        # create menu bar
        self.__create_menubar()

        # set status bar
        self.statusBar().setStyleSheet("color: #888;")

        # create central widget for main window.
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.__create_layout()
        self.__create_sidebar()

    def __create_menubar(self):
        def set_menu_structure(p_menu, menu_structure):
            menus = menu_structure["menus"]
            actions = menu_structure["actions"]

            for menu_name, menu_info in menus.items():
                icon = menu_info.get("icon")
                sub_menu = QMenu(menu_name, icon=QIcon(icon))
                p_menu.addMenu(sub_menu)
                set_menu_structure(sub_menu, menu_info)

            for action in actions:
                if action.get("name") == "sep":
                    p_menu.addSeparator()
                    continue

                sub_action = QAction(QIcon(action.get("icon")), action.get("name"), self)

                if action.get("connect") is not None:
                    sub_action.triggered.connect(action.get("connect"))

                sub_action.setShortcut(QKeySequence(action.get("shortcut")))
                sub_action.setStatusTip(action.get("status"))
                p_menu.addAction(sub_action)

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
                        {"name": "reload", "shortcut": "Ctrl+r", "icon": "", "status": "Update data", "connect": None},
                        {"name": "sep", "shortcut": "", "icon": "", "status": "", "connect": None},
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
        set_menu_structure(self.menuBar(), menu)
        return None

    def __create_layout(self):
        # create main layout to store splitter
        main_layout = QHBoxLayout()

        # create splitter
        splitter = QSplitter()

        # settings for splitter
        splitter.setOrientation(Qt.Horizontal)
        #splitter.setEnabled(False)
        splitter.setStyleSheet("border: 1px solid #333;")

        self.sidebar_widget = QWidget()
        self.sidebar_widget.setFixedWidth(150)
        self.content_widget = QWidget()
        self.content_widget.setStyleSheet("border: none")

        # set main content
        MainContent.main(self.content_widget)

        splitter.addWidget(self.sidebar_widget)
        splitter.addWidget(self.content_widget)

        main_layout.addWidget(splitter)
        self.centralWidget().setLayout(main_layout)
        return None

    def __create_sidebar(self):
        # create sidebar layout
        sidebar_layout = QVBoxLayout()

        # create buttons in sidebar
        btn_main = QPushButton("Main")
        btn_mgmt = QPushButton("Management")
        btn_settings = QPushButton("Settings")
        btn_log = QPushButton("Logging")

        # btn size
        btn_main.setFixedSize(150, 50)
        btn_mgmt.setFixedSize(150, 50)
        btn_settings.setFixedSize(150, 50)
        btn_log.setFixedSize(150, 50)

        btn_main.setStyleSheet(BUTTON_STYLE)
        btn_mgmt.setStyleSheet(BUTTON_STYLE)
        btn_settings.setStyleSheet(BUTTON_STYLE)
        btn_log.setStyleSheet(BUTTON_STYLE)

        # btn set status bar
        btn_main.setStatusTip("Main")
        btn_mgmt.setStatusTip("USB Management")
        btn_settings.setStatusTip("Config UDAS setting")
        btn_log.setStatusTip("Show UDAS log")

        # connect slot
        btn_main.clicked.connect(lambda: MainContent.main(self.content_widget))
        btn_mgmt.clicked.connect(lambda: MainContent.management(self.content_widget))
        btn_settings.clicked.connect(lambda: MainContent.settings(self.content_widget))
        btn_log.clicked.connect(lambda: MainContent.log(self.content_widget))

        # add btns to layout
        sidebar_layout.addWidget(btn_main)
        sidebar_layout.addWidget(btn_mgmt)
        sidebar_layout.addWidget(btn_settings)
        sidebar_layout.addWidget(btn_log)

        # etc settings
        sidebar_layout.addStretch()
        sidebar_layout.setContentsMargins(0, 0, 0, 0)

        self.sidebar_widget.setLayout(sidebar_layout)
        return None

    def __exit(self):
        sys.exit(0)


class MainContent:
    _CONFIG = ConfigIni()

    @staticmethod
    def main(content_widget):
        clear_layout(content_widget)

        layout = QVBoxLayout()
        layout.setContentsMargins(20, 10, 20, 10)

        # status area
        widget_status = QWidget()
        widget_status.setFixedSize(360, 90)

        layout_status = QVBoxLayout()
        layout_status_info = QHBoxLayout()
        layout_status_info.setContentsMargins(0, 10, 0, 0)

        # status area: create labels
        label_title_status = QLabel("<b>USB Storage Registration Status</b>")
        label_whitelist = QLabel(" * WHITELIST : 2")
        label_blacklist = QLabel(" * BLACKLIST : 7")

        # status area: set size of labels
        label_title_status.setFixedSize(360, 25)
        label_whitelist.setFixedSize(180, 25)
        label_blacklist.setFixedSize(180, 25)

        # status area: add info labels into layout_status_info
        layout_status_info.addWidget(label_whitelist)
        layout_status_info.addWidget(label_blacklist)
        layout_status_info.addStretch()

        # status area: end
        layout_status.addWidget(label_title_status)
        layout_status.addLayout(layout_status_info)
        layout_status.addStretch()
        widget_status.setLayout(layout_status)

        # service area
        widget_service = QWidget()
        widget_service.setFixedSize(360, 90)

        layout_service = QVBoxLayout()
        layout_service_info = QHBoxLayout()
        layout_service_info.setContentsMargins(0, 10, 0, 0)

        # service area: create widget
        label_title_service = QLabel(f"<b>UDAS Service</b>")
        label_service_status = QLabel(" * STATUS : Running")
        label_service_uptime = QLabel(" * UPTIME : 30 Min")

        # service area: set size of widgets
        label_title_service.setFixedSize(360, 25)
        label_service_status.setFixedSize(180, 25)
        label_service_uptime.setFixedSize(180, 25)

        # service area: add info labels into layout_service_info
        layout_service_info.addWidget(label_service_status)
        layout_service_info.addWidget(label_service_uptime)
        layout_service_info.addStretch()
        widget_service.setLayout(layout_service)

        # service area: end
        layout_service.addWidget(label_title_service)
        layout_service.addLayout(layout_service_info)

        layout.addWidget(widget_status)
        layout.addWidget(get_separate_line(color="#555"))
        layout.addWidget(widget_service)
        layout.addStretch()
        content_widget.setLayout(layout)
        return

    @staticmethod
    def management(content_widget):
        print("Management")

    @staticmethod
    def settings(content_widget):
        clear_layout(content_widget)

        layout = QVBoxLayout()
        layout.setContentsMargins(20, 10, 20, 10)

        # widget for version information
        widget_version = QWidget()
        widget_version.setFixedSize(360, 90)

        layout_version = QVBoxLayout()
        layout_version_info = QHBoxLayout()
        layout_version_info.setContentsMargins(0, 10, 0, 0)

        label_version = QLabel("<b>Version Information</b>")
        label_version_info = QLabel(f" * UDAS VERSION {MainContent._CONFIG.get_version()} BETA")
        label_version.setFixedSize(360, 25)
        label_version_info.setFixedSize(360, 25)

        layout_version_info.addWidget(label_version_info)
        layout_version.addWidget(label_version)
        layout_version.addLayout(layout_version_info)
        layout_version.addStretch()
        widget_version.setLayout(layout_version)

        # widget for
        widget_service = QWidget()
        widget_service.setFixedSize(360, 90)

        layout_service = QVBoxLayout()
        layout_service_ctrl = QHBoxLayout()

        label_service = QLabel("<b>UDAS Service</b>")
        label_service_info = QLabel(" Service Control")
        btn_service_sw = QPushButton()
        btn_service_sw.setFlat(False)
        btn_service_sw.setFixedSize(100, 25)
        btn_service_sw.setStyleSheet(BUTTON_STYLE)

        text = "On" if True else "Off"
        btn_service_sw.setText(text)

        label_service.setFixedSize(360, 25)
        label_service_info.setFixedSize(240, 25)

        layout_service_ctrl.addWidget(label_service_info)
        layout_service_ctrl.addWidget(btn_service_sw)
        layout_service_ctrl.addStretch()

        layout_service.addWidget(label_service)
        layout_service.addLayout(layout_service_ctrl)
        layout_service.addStretch()
        widget_service.setLayout(layout_service)




        layout.addWidget(widget_version)
        layout.addWidget(get_separate_line(color="#555"))
        layout.addWidget(widget_service)
        layout.addStretch()
        content_widget.setLayout(layout)
        return

    @staticmethod
    def log(content_widget):
        print("Log")
"""

from udas.udas_pytool import (QMainWindow,
                              QApplication,
                              centralise_fixed,
                              clear_layout,
                              create_menubar,
                              get_blacklist_num,
                              get_service_status,
                              get_whitelist_num,
                              sys)
from udas.udas_custom_widget import (CustomDialogPasswordInput,
                                     custom_box_layout,
                                     custom_fixed_push_button,
                                     custom_label,
                                     custom_labels_kv,
                                     custom_label_button_for_control,
                                     custom_separate_line,
                                     custom_splitter_fixed,
                                     custom_widget_for_layout)


COLOR_SEPARATE_LINE: str = "#333"
DIALOG_PASSWORD_TITLE: str = "UDAS Authentication"
DIALOG_PASSWORD_WIDTH: int = 400
DIALOG_PASSWORD_HEIGHT: int = 200
MAIN_WINDOW_TITLE: str = "USB Docking Authentication System"
MAIN_WINDOW_WIDTH: int = 600
MAIN_WINDOW_HEIGHT: int = 400
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


class MainWindow(QMainWindow):
    def __init__(self, **kwargs):
        super().__init__()
        # set window structure
        self.__init_ui(kwargs)

        # display main screen.
        self.__main()

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
                                {"name": "reload", "shortcut": "Ctrl+r", "icon": "", "status": "Update data",
                                 "connect": None},
                                {"name": "sep", "shortcut": "", "icon": "", "status": "", "connect": None},
                                {"name": "exit", "shortcut": "Ctrl+F4", "icon": "", "status": "Exit UDAS",
                                 "connect": self.__exit},
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
                "connect": lambda: self.__main(),
            },
            "MANAGEMENT": {
                "status": "Manage registered USB devices...",
                "style": BUTTON_SIDEBAR_STYLE,
                "connect": lambda: self.__mgmt(),
            },
            "SETTINGS": {
                "status": "UDAS settings...",
                "style": BUTTON_SIDEBAR_STYLE,
                "connect": lambda: self.__settings(),
            },
            "LOG": {
                "status": "Check process logs...",
                "style": BUTTON_SIDEBAR_STYLE,
                "connect": lambda: self.__log(),
            },
        }

        children_btns = [ custom_fixed_push_button(text=text,
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
        return None

    def __main(self):
        clear_layout(self.widget_main_content)

        # get KPI data.
        status_data: dict = self.__read_status_kpi_data()
        service_data: dict = self.__read_service_kpi_data()

        # set the size of widgets
        total_width_half: int = int(WIDGET_MAIN_CONTENT_WIDTH / 2)
        key_width: float = 0.4
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
                                   margin_l=20,
                                   margin_t=20,)
        self.widget_main_content.setLayout(layout)
        return None

    def __mgmt(self):
        clear_layout(self.widget_main_content)
        return None

    def __read_status_kpi_data(self) -> dict:
        return {
            "whitelist": get_whitelist_num(),
            "blacklist": get_blacklist_num(),
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
        service_data = self.__read_service_kpi_data()

        # set the size of widgets
        total_width = WIDGET_MAIN_CONTENT_WIDTH
        button_width: int = 50
        height: int = 30

        label_settings_preamble = custom_label(text="<b>UDAS Settings</b>",
                                               width=total_width,
                                               height=30)
        widget_layout_ctrl_service = custom_label_button_for_control(total_width=total_width,
                                                                     height=height,
                                                                     ratio=0.7,
                                                                     info_text="UDAS Service On / Off",
                                                                     button_width=button_width,
                                                                     button_text="OFF" if "running" in service_data.get("is_running") else "ON",
                                                                     button_style=BUTTON_GENERAL_STYLE,
                                                                     )

        layout = custom_box_layout(children=[label_settings_preamble,
                                             widget_layout_ctrl_service,
                                             custom_separate_line(color=COLOR_SEPARATE_LINE)],
                                   margin_l=20,
                                   margin_t=20,)
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
    """
    pw_dialog = CustomDialogPasswordInput(title=DIALOG_PASSWORD_TITLE,
                                          width=DIALOG_PASSWORD_WIDTH,
                                          height=DIALOG_PASSWORD_HEIGHT)
    pw_dialog.exec()
    """

    # main window.
    window = MainWindow(title="USB Docking Authentication System",
                        width=MAIN_WINDOW_WIDTH,
                        height=MAIN_WINDOW_HEIGHT)

    window.show()
    sys.exit(app.exec())