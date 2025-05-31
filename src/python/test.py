import sys
from PySide6.QtWidgets import QApplication, QMessageBox, QDialog, QPushButton, QLabel
from PySide6.QtGui import QScreen
from PySide6.QtCore import Qt


class Test(QMessageBox):
    def __init__(self, *args, **kwargs):

        super().__init__()
        self.setWindowTitle("UDAS Alert")
        self.centralise(400, 200)
        self.init_ui(sys.argv[1:])

    def centralise(self, window_width, window_height):
        # get a primary screen from QApplication
        # apply it as an argument QScreen.availableGeometry
        # center the widget with center()
        # cnn not apply on Ubuntu Wayland.
        screen = QScreen.availableGeometry(QApplication.primaryScreen())
        window_x = int((screen.width() - window_width) / 2)
        window_y = int((screen.height() - window_height) / 2)
        self.setGeometry(window_x, window_y, window_width, window_height)

    def init_ui(self, options: list):
        # get information from cmd options
        tmp: dict = {}
        for option in options:
            option_tmp: list = option.split("=")
            tmp[option_tmp[0].replace("--", "")] = option_tmp[1]

        text = f"""New USB storage device({tmp.get('idVendor')}:{tmp.get('idProduct')}) is being detected.\n
* Manufacturer: {tmp.get('manufacturer')}
* Product     : {tmp.get('product')}
* Serial No.  : {tmp.get('serial')} 
        """

        # set question MessageBox
        self.setText(text)
        self.setIcon(QMessageBox.Question)

        # button setting
        self.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        self.setDefaultButton(QMessageBox.No)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = Test(sys.argv)
    result = widget.exec()
    if result == QMessageBox.Yes:
        print("Password Input")

    sys.exit(app.quit())
