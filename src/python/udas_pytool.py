import sys
import configparser
from PySide6.QtGui import QScreen
from PySide6.QtWidgets import (QApplication,
                               QMainWindow,
                               QWidget,
                               QDialog,
                               QMessageBox,
                               QVBoxLayout,
                               QHBoxLayout,
                               QListWidget,
                               QTableWidget,
                               QLineEdit,
                               QPushButton,
                               QLabel)


CONFIG_PATH: str = "../../config/config.ini"


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
        sys.exit(-3);


class PasswordInputDialog(QDialog):
    def __init__(self, *args, **kwargs):
        super().__init__()
        self.setWindowTitle("Register Trusted USB")
        self.centralise(440, 150)
        self.init_ui(args)

    def centralise(self, window_width: int, window_height: int):
        screen = QScreen.availableGeometry(QApplication.primaryScreen())
        window_x = int((screen.width() - window_width) / 2)
        window_y = int((screen.height() - window_height) / 2)
        self.move(window_x, window_y)
        self.setFixedSize(window_width, window_height)

    def init_ui(self, options: tuple):
        # create layout
        main_layout = QVBoxLayout()
        btn_layout = QHBoxLayout()

        # create label
        password_label = QLabel("Enter the UDAS Password to register new trusted device\n")
        self.result_label = QLabel("")

        # create password input
        self.input_password = QLineEdit()
        self.input_password.setPlaceholderText("UDAS Password")
        self.input_password.setEchoMode(QLineEdit.Password)

        # create button
        self.cancel_btn = QPushButton("Cancel")
        self.register_btn = QPushButton("Register")
        self.cancel_btn.clicked.connect(self.reject)
        self.register_btn.clicked.connect(self.on_click_register_btn)

        # add widget into layout
        btn_layout.addWidget(self.register_btn)
        btn_layout.addWidget(self.cancel_btn)
        main_layout.addWidget(password_label)
        main_layout.addWidget(self.input_password)
        main_layout.addWidget(self.result_label)
        main_layout.addLayout(btn_layout)
        main_layout.addStretch()
        self.setLayout(main_layout)

    def on_click_register_btn(self):
        test_password = ConfigIni().get_auth_str()

        if test_password == self.input_password.text():
            self.accept()

        else:
            self.result_label.setText("Password is not match")
            self.result_label.setStyleSheet("color: red;")

    def reject(self):
        sys.exit(-1)