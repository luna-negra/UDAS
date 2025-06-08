from udas_pytool import (sys,
                         Qt,
                         QApplication,
                         QMainWindow,
                         QWidget,
                         QMessageBox,
                         QSplitter,
                         QVBoxLayout,
                         QHBoxLayout,
                         QMenu,
                         QAction,
                         QIcon,
                         QKeySequence,
                         QTableWidget,
                         QPushButton,
                         QLabel,
                         ConfigIni,
                         centralise,
                         PasswordInputDialog,
                         get_separate_line,)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        config = ConfigIni()

        # set title of main window
        self.setWindowTitle(f"UDAS - {config.get_version()}")

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

    @staticmethod
    def main(content_widget):
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
        print("Settings")

    @staticmethod
    def log(content_widget):
        print("Log")


if __name__ == "__main__":
    app = QApplication()

    # if cancelled , entire process will be terminated.
    #pw_dialog = PasswordInputDialog()
    #pw_dialog.exec()

    # main window.
    window = MainWindow()

    window.show()
    sys.exit(app.exec())