import sys
import configparser
from subprocess import (run,
                        PIPE,)
from PySide6.QtCore import Qt
from PySide6.QtGui import (QScreen,
                           QAction,
                           QIcon,
                           QKeySequence,)
from PySide6.QtWidgets import (QApplication,
                               QMainWindow,
                               QWidget,
                               QDialog,
                               QMessageBox,
                               QMenu,
                               QSplitter,
                               QVBoxLayout,
                               QHBoxLayout,
                               QListWidget,
                               QTableWidget,
                               QCheckBox,
                               QLineEdit,
                               QPushButton,
                               QLabel,
                               QFrame,)


# need to convert absolute
BLACKLIST_PATH: str = "/etc/udev/rules.d/99-udas.blacklist.rules"
ENCODING: str ="utf-8"
CONFIG_PATH: str = "../../config/config.ini"
WHITELIST_PATH: str = "/etc/udev/rules.d/99-udas.custom.rules"

def centralise_fixed(obj, width: int, height: int):
    screen = QScreen.availableGeometry(QApplication.primaryScreen())
    window_x = int((screen.width() - width) / 2)
    window_y = int((screen.height() - height) / 2)
    obj.move(window_x, window_y)
    obj.setFixedSize(width, height)
    return None

def clear_layout(widget):
    old_layout = widget.layout()
    if old_layout:
        tmp_widget = QWidget()
        tmp_widget.setLayout(old_layout)
        del tmp_widget
    return None

def create_menubar(p_menu, menu_structure, widget):
    menus = menu_structure["menus"]
    actions = menu_structure["actions"]

    for menu_name, menu_info in menus.items():
        icon = menu_info.get("icon")
        sub_menu = QMenu(menu_name, icon=QIcon(icon))
        p_menu.addMenu(sub_menu)
        create_menubar(sub_menu, menu_info, widget)

    for action in actions:
        if action.get("name") == "sep":
            p_menu.addSeparator()
            continue

        sub_action = QAction(QIcon(action.get("icon")), action.get("name"), widget)

        if action.get("connect") is not None:
            sub_action.triggered.connect(action.get("connect"))

        sub_action.setShortcut(QKeySequence(action.get("shortcut")))
        sub_action.setStatusTip(action.get("status"))
        p_menu.addAction(sub_action)

    return None

def get_blacklist_num() -> str:
    run_result = run(f"wc -l {BLACKLIST_PATH}", stdout=PIPE, stderr=PIPE, shell=True)
    if run_result.returncode == 0:
        result = run_result.stdout.decode(ENCODING).split()[0]
        return result
    return "None"

def get_service_status() -> dict:
    ret_value = {"is_running": "ERROR", "start_dt": "ERROR",  "uptime": "ERROR"}
    run_result = run("systemctl status docker | head -n 3 | tail -n 1", stdout=PIPE, stderr=PIPE, shell=True)
    if run_result.returncode == 0:
        tmp = run_result.stdout.decode(ENCODING).split()
        ret_value["is_running"] = f"{tmp[2].strip('()')} ({tmp[1]})"
        ret_value["start_dt"] = f"{tmp[5]} {tmp[6]} {tmp[7].strip(';')}"
        ret_value["uptime"] = f"{tmp[-3]} {tmp[-2]}"
    return ret_value


def get_whitelist_num() -> str:
    run_result = run(f"wc -l {WHITELIST_PATH}", stdout=PIPE, stderr=PIPE, shell=True)
    if run_result.returncode == 0:
        result = run_result.stdout.decode(ENCODING).split()[0]
        return result
    return "ERROR"

class ConfigIni:
    def __init__(self):
        self.__config = configparser.ConfigParser()
        self.__config.read(CONFIG_PATH)

        try:
            if len(self.__config.sections()) != 3:
                raise FileExistsError("[ERROR] Config file is not a proper.")
        except FileExistsError:
            self.reject()

        self.__version = self.__config["Version"].get("version")
        self.__auth_str = self.__config["Management"].get("auth_str")
        self.__lang = self.__config["Management"].get("lang")
        self.__log_path = self.__config["Logging"].get("path")
        self.__log_level = self.__config["Logging"].get("level")

    def get_version(self):
        return self.__version

    def get_auth_str(self):
        return self.__auth_str

    def get_lang(self):
        return self.__lang

    def get_log_path(self):
        return self.__log_path

    def get_log_level(self):
        return self.__log_level

    def set_auth_str(self, enc_auth_str: str):
        self.__auth_str = enc_auth_str
        return None

    def set_lang(self, lang: str):
        self.__lang = lang
        return None

    def set_log_path(self, log_path: str):
        self.__log_path = log_path
        return None

    def set_log_level(self, log_level: str):
        self.__log_level = log_level
        return None

    def reject(self):
        sys.exit(-1)
