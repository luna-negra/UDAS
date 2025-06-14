import subprocess
import sys
import configparser
import re
from hashlib import sha512
from subprocess import (run,
                        PIPE,)
from PySide6.QtCore import Qt
from PySide6.QtGui import (QScreen,
                           QAction,
                           QIcon,
                           QKeySequence,)
from PySide6.QtWidgets import (QApplication,
                               QAbstractItemView,
                               QMainWindow,
                               QWidget,
                               QDialog,
                               QMessageBox,
                               QMenu,
                               QSplitter,
                               QVBoxLayout,
                               QHBoxLayout,
                               QListWidget,
                               QListWidgetItem,
                               QTableWidget,
                               QTableWidgetItem,
                               QCheckBox,
                               QComboBox,
                               QLineEdit,
                               QPushButton,
                               QLabel,
                               QFrame,)


# need to convert absolute
BLACKLIST_PATH: str = "/etc/udev/rules.d/99-udas.blacklist.rules"
ENCODING: str ="utf-8"
CONFIG_PATH: str = "/etc/udas/config/config.ini"
WHITELIST_PATH: str = "/etc/udev/rules.d/99-udas.custom.rules"
RULE_REGEX = r'ACTION=="add", SUBSYSTEM=="block", ATTRS{idVendor}=="(?P<id_vendor>[A-z0-9]{4})", ATTRS{idProduct}=="(?P<id_product>[A-z0-9]{4})",.+, ENV{UDISKS_IGNORE}="(?P<ignore>[01])"'
SERIAL_REGEX = r'ATTRS{serial}=="(?P<serial>[A-z0-9]+)"'
MANUFACTURER_REGEX= r'ATTRS{manufacturer}=="(?P<manufacturer>[A-z0-9]+)"'
PRODUCT_REGEX= r'ATTRS{product}=="(?P<product>[A-z0-9]+)"'


def centralise_fixed(obj, width: int, height: int):
    screen = QScreen.availableGeometry(QApplication.primaryScreen())
    window_x = int((screen.width() - width) / 2)
    window_y = int((screen.height() - height) / 2)
    obj.move(window_x, window_y)
    obj.setFixedSize(width, height)
    return None

def change_blacklist(opt: str) -> subprocess.CompletedProcess:
    command: str = f"pkexec udas set blacklist {opt}"
    return run(args=command, stdout=PIPE, stderr=PIPE, shell=True)

def change_loglevel(log_level:str) -> subprocess.CompletedProcess:
    command: str = f"pkexec udas set loglevel {log_level}"
    return run(args=command, stdout=PIPE, stderr=PIPE, shell=True)

def change_password(old_pw: str, new_pw:str) -> subprocess.CompletedProcess:
    command: str = f"pkexec udas set passwd --old-password={old_pw} --new-password={new_pw}"
    return run(args=command, stdout=PIPE, stderr=PIPE, shell=True)

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

def encrypt_str(string:str) -> str:
    return sha512(string=f"udas::{string}::2abu".encode("utf-8")).hexdigest()

def exit_process(exit_code: int=0) -> None:
    sys.exit(exit_code)

def get_rules(is_white: bool=True) -> list:
    result = []
    file_path: str = WHITELIST_PATH if is_white else BLACKLIST_PATH
    code: str = "0" if is_white else "1"

    run_result = run(f"cat {file_path}", stdout=PIPE, stderr=PIPE, shell=True)
    if run_result.returncode == 0:
        whitelist_regex = re.compile(RULE_REGEX)

        for line in run_result.stdout.decode(ENCODING).split("\n"):
            regex_result = whitelist_regex.search(line)

            if regex_result is None:
                continue

            tmp = list(regex_result.groups())
            if tmp[-1] != code:
                continue

            manufacturer = re.compile(MANUFACTURER_REGEX).search(line)
            product = re.compile(PRODUCT_REGEX).search(line)
            serial = re.compile(SERIAL_REGEX).search(line)

            group: list = [
                f"{manufacturer.group(manufacturer.lastgroup)} ({tmp[0]})" if manufacturer is not None else f"N/A ({tmp[0]})",
                f"{product.group(product.lastgroup)} ({tmp[1]})" if product is not None else f"N/A ({tmp[1]})",
                f"{serial.group(serial.lastgroup)}" if serial is not None else "N/A"
            ]
            result.append(group)
    return result

def get_rule_num(is_white: bool = True) -> str:
    file_path: str = WHITELIST_PATH if is_white else BLACKLIST_PATH
    run_result = run(f"wc -l {file_path}", stdout=PIPE, stderr=PIPE, shell=True)
    if run_result.returncode == 0:
        result = run_result.stdout.decode(ENCODING).split()[0]
        return result
    return "ERROR"

def get_service_status() -> dict:
    ret_value = {"is_running": "ERROR", "start_dt": "ERROR",  "uptime": "ERROR"}
    run_result = run("systemctl status docker | head -n 3 | tail -n 1", stdout=PIPE, stderr=PIPE, shell=True)
    if run_result.returncode == 0:
        tmp = run_result.stdout.decode(ENCODING).split()
        ret_value["is_running"] = f"{tmp[2].strip('()')} ({tmp[1]})"
        ret_value["start_dt"] = f"{tmp[5]} {tmp[6]} {tmp[7].strip(';')}"
        ret_value["uptime"] = f"{tmp[-3]} {tmp[-2]}" if "h" in tmp[-3] else f"{tmp[-2]}"
    return ret_value

def remove_registered_usb_info(id_vendor: str,
                               id_product:str,
                               serial:str,
                               manufacturer:str,
                               product:str,
                               blacklist:bool=False) -> subprocess.CompletedProcess:
    id_vendor = id_vendor if id_vendor != "N/A" else "Unknown"
    id_product = id_product if id_product != "N/A" else "Unknown"
    serial = serial if serial != "N/A" else "Unknown"
    manufacturer = manufacturer if manufacturer != "N/A" else "Unknown"
    product = product if product != "N/A" else "Unknown"
    blacklist = "blacklist" if blacklist else "whitelist"

    command: str = f"pkexec udas td remove {blacklist} --idVendor={id_vendor} --idProduct={id_product} --serial={serial} --manufacturer={manufacturer} --product={product}"
    return run(args=command, stdout=PIPE, stderr=PIPE, shell=True)


class ConfigIni:
    def __init__(self):
        self.__config = configparser.ConfigParser()
        self.__config.read(CONFIG_PATH)

        try:
            if len(self.__config.sections()) != 3:
                raise AttributeError("[ERROR] Config file is not a proper.")
        except AttributeError as e:
            pass

        else:
            self.__version = self.__config["Version"].get("version")
            self.__auth_str = self.__config["Management"].get("auth_str")
            self.__blacklist = self.__config["Management"].get("blacklist")
            self.__lang = self.__config["Management"].get("lang")
            self.__log_path = self.__config["Logging"].get("path")
            self.__log_level = self.__config["Logging"].get("level")

    def get_version(self):
        return self.__version

    def get_auth_str(self):
        return self.__auth_str

    def get_blacklist(self):
        try:
            value = int(self.__blacklist)
        except ValueError:
            return 0
        return value

    def get_lang(self):
        return self.__lang

    def get_log_path(self):
        return self.__log_path

    def get_log_level(self):
        return self.__log_level

    def set_auth_str(self, enc_auth_str: str):
        self.__auth_str = enc_auth_str
        return None

    def set_blacklist(self, on_off: int):
        self.__blacklist = str(on_off)
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

    def write(self):
        with open(CONFIG_PATH, "w") as f:
            self.__config.write(f)
        return None

    def reject(self):
        sys.exit(-1)
