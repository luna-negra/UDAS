import sys
from PySide6.QtWidgets import (QApplication,
                               QMessageBox,
                               QDialog,
                               QVBoxLayout,
                               QHBoxLayout,
                               QLineEdit,
                               QPushButton,
                               QLabel)
from PySide6.QtGui import QScreen


def get_usb_info(options: tuple) -> dict:
    tmp: dict = {}
    for option in options[1:]:
        option_tmp: list = option.split("=")
        tmp[option_tmp[0].replace("--", "")] = option_tmp[1]

    tmp["info_label"] = f"""New USB storage device({tmp.get('idVendor')}:{tmp.get('idProduct')}) is being detected.\n
* Manufacturer: {tmp.get('manufacturer')}
* Product     : {tmp.get('product')}
* Serial No.  : {tmp.get('serial')}\n 
Do you want to register it as a trusted device?
"""
    return tmp


class AlertNewUSB(QMessageBox):
    def __init__(self, args):
        super().__init__()
        self.setWindowTitle("UDAS Alert")
        self.centralise(400, 200)
        self.init_ui(args)

    def centralise(self, window_width: int, window_height: int):
        # get a primary screen from QApplication
        # apply it as an argument QScreen.availableGeometry
        # center the widget with center()
        # cnn not apply on Ubuntu Wayland.
        screen = QScreen.availableGeometry(QApplication.primaryScreen())
        window_x = int((screen.width() - window_width) / 2)
        window_y = int((screen.height() - window_height) / 2)
        self.move(window_x, window_y)
        self.setFixedSize(window_width, window_height)

    def init_ui(self, options: tuple):
        if len(options) == 1:
            self.setText("[WARNING] Invalid Execute Command.\n")
            self.setIcon(QMessageBox.Warning)

        else:
            # get information from cmd options
            usb_info: dict = get_usb_info(options)

            # set question MessageBox
            self.setText(usb_info.get("info_label"))
            self.setIcon(QMessageBox.Question)

            # button setting
            self.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            self.setDefaultButton(QMessageBox.No)


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
        test_password = "Password"

        if test_password == self.input_password.text():
            self.accept()

        else:
            self.result_label.setText("Password is not match")
            self.result_label.setStyleSheet("color: red;")

    def reject(self):
        sys.exit(-1)

if __name__ == "__main__":
    app = QApplication()
    msg_box = AlertNewUSB(sys.argv)
    msg_box_result = msg_box.exec()
    if msg_box_result == QMessageBox.Yes:
        dialog = PasswordInputDialog(sys.argv)
        result = dialog.exec()

    else:
        sys.exit(-1)

    sys.exit(app.quit())
