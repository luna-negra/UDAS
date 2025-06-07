from udas_pytool import *


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
