from udas_pytool import (sys,
                         QApplication,
                         QMainWindow,
                         QWidget,
                         QMessageBox,
                         QVBoxLayout,
                         QHBoxLayout,
                         QMenu,
                         QAction,
                         QIcon,
                         QKeySequence,
                         QTableWidget,
                         QPushButton,
                         ConfigIni,
                         centralise,
                         PasswordInputDialog,)


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
        # create central widget for main window.
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        statusbar = self.statusBar()
        statusbar.setStyleSheet("color:#999;")

        # create menubar
        self.__create_menubar()

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

        # call menubar in window
        menubar = self.menuBar()

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
                        {"name": "exit", "shortcut": "Ctrl+F4", "icon": "", "status": "Exit UDAS", "connect": self.exit},
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
        set_menu_structure(menubar, menu)

    def exit(self):
        sys.exit(0)


if __name__ == "__main__":
    app = QApplication()

    # if cancelled , entire process will be terminated.
    pw_dialog = PasswordInputDialog()
    pw_dialog.exec()

    # main window.
    window = MainWindow()

    window.show()
    sys.exit(app.exec())