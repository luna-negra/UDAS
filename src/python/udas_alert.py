from udas.udas_pytool import (sys,
                              QApplication,
                              QMessageBox,
                              centralise_fixed,)
from udas.udas_custom_widget import CustomDialogPasswordInput


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
        centralise_fixed(self, 400, 200)
        self.init_ui(args)

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
    if msg_box_result != QMessageBox.Yes:
        sys.exit(-1)

    dialog = CustomDialogPasswordInput()


    result = dialog.exec()
    sys.exit(app.quit())
