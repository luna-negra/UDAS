from typing import Any
from .udas_pytool import (Qt,
                         QWidget,
                         QMainWindow,
                         QDialog,
                         QSplitter,
                         QVBoxLayout,
                         QHBoxLayout,
                         QFrame,
                         QLabel,
                         QLineEdit,
                         QPushButton,
                         ConfigIni,
                         sys,)


def custom_box_layout(children: list,
                      vertical: bool = True,
                      stretch: bool = True,
                      align: str = "center",
                      spacing: int = 10,
                      margin_l: int = 10,
                      margin_t: int = 10,
                      margin_r: int = 10,
                      margin_b: int = 10) -> QVBoxLayout | QHBoxLayout:
    l = QVBoxLayout() if vertical else QHBoxLayout()

    for child in children:
        if isinstance(child, QWidget):
            l.addWidget(child)

        elif isinstance(child, QHBoxLayout) or  isinstance(child, QVBoxLayout):
            l.addLayout(child)

    tmp_align = Qt.AlignCenter
    if stretch:
        if vertical:
            if align.lower() == "left":
                tmp_align = Qt.AlignLeft
            elif align.lower() == "right":
                tmp_align = Qt.AlignRight

        else:
            if align.lower() == "top":
                tmp_align = Qt.AlignTop
            elif align.lower() == "bottom":
                tmp_align = Qt.AlignBottom
    l.addStretch(tmp_align)
    l.setSpacing(spacing)
    l.setContentsMargins(margin_l, margin_t, margin_r, margin_b)
    return l

def custom_label(text: str,
                 width: int,
                 height: int,
                 style: str | None = None,
                 enable: bool = True) -> QLabel:
    l = QLabel(text)
    l.setStyleSheet(style)
    l.setFixedSize(width, height)
    l.setStyleSheet(style)
    l.setEnabled(enable)
    return l

def custom_fixed_push_button(text: str,
                             width: int,
                             height: int,
                             style: str | None = None,
                             connect: Any = None,
                             status_tip: str | None = None,
                             default: bool = False,
                             enable: bool = True,) -> QPushButton:
    b = QPushButton(text)
    b.setFixedSize(width, height)
    b.setStyleSheet(style)
    b.clicked.connect(connect)
    b.setStatusTip(status_tip)
    b.setDefault(default)
    b.setEnabled(enable)
    return b

def custom_line_edit(width: int,
                     height: int,
                     style: str | None = None,
                     tooltip: str | None = None,
                     status_tip: str | None = None,
                     default: str | None = None,
                     echo_mode: bool = False,
                     enable: bool = True) -> QLineEdit:
    i = QLineEdit()
    i.setFixedSize(width, height)
    i.setStyleSheet(style)
    i.setToolTip(tooltip)
    i.setStatusTip(status_tip)
    i.setText(default)
    if echo_mode:
        i.setEchoMode(QLineEdit.Password)
    i.setEnabled(enable)
    return i

def custom_separate_line(color:str="#fff",
                         thickness:int=1,
                         line_type=QFrame.HLine,
                         shadow=QFrame.Sunken) -> QFrame:
    separate_line = QFrame()
    separate_line.setFrameShape(line_type)
    separate_line.setStyleSheet(f"background-color: {color};")
    separate_line.setFrameShadow(shadow)  # Sunken | Raised | Plain
    separate_line.setFixedHeight(thickness)
    return separate_line

def custom_splitter_fixed(widget_list: list,
                          vertical_line: bool = True,
                          style: str | None = None) -> QSplitter:
    s = QSplitter()
    s.setOrientation(Qt.Horizontal) if vertical_line else s.setOrientation(Qt.Vertical)
    s.setStyleSheet(style)
    [ s.addWidget(widget) for widget in widget_list ]
    return s

def custom_widget_for_layout(width: int, height: int, style: str | None = None) -> QWidget:
    w = QWidget()
    w.setFixedSize(width, height)
    w.setStyleSheet(style)
    return w


def custom_labels_kv(total_width: int,
                     total_height: int,
                     key:str,
                     value: str,
                     ratio: float,
                     key_height: int | None = None,
                     style: str | None = None,
                     key_style: str | None = None,
                     value_style: str | None = None,
                     align:str = "center",
                     spacing: int = 10):

    key = f" ・ {key} : "
    label_key = custom_label(text=key,
                             width=int(total_width * ratio),
                             height=key_height or total_height,
                             style=key_style)
    label_value = custom_label(text=value,
                               width=int(total_width * (1 - ratio)),
                               height=key_height or total_height,
                               style=value_style)
    layout = custom_box_layout(children=[label_key, label_value],
                               vertical=False,
                               align=align,
                               spacing=spacing,
                               margin_l=0,
                               margin_r=0,
                               margin_t=0,
                               margin_b=0)
    widget = custom_widget_for_layout(width=total_width,
                                      height=total_height,
                                      style=style)
    widget.setLayout(layout)
    return widget


class CustomDialogPasswordInput(QDialog):
    def __init__(self, **kwargs):
        super().__init__()
        self.__init_ui(kwargs)
        self.__label_width: int = self.width() - 20
        self.__label_height: int = 25
        self.__btn_width: int = int((self.width() - 50) / 2)
        self.__btn_height: int = 30
        self.__set_widget()

    def __init_ui(self, kwargs):
        self.setWindowTitle(kwargs.get("title"))
        self.setFixedWidth(kwargs.get("width"))
        self.setFixedHeight(kwargs.get("height"))

    def __set_widget(self):
        label_info = custom_label(text="Enter the UDAS Password to register new trusted device.\n",
                                  width=self.width() - 20,
                                  height=100)
        self.line_input_password = custom_line_edit(width=self.__label_width,
                                                    height=self.__label_height,
                                                    tooltip="UDAS Password",
                                                    status_tip="Input Password",
                                                    echo_mode=True,)
        btn_cancel = custom_fixed_push_button(text="Cancel",
                                              width=self.__btn_width,
                                              height=self.__btn_height,)
        btn_enter = custom_fixed_push_button(text="Override",
                                             width=self.__btn_width,
                                             height=self.__btn_height,
                                             default=True)
        self.label_result = custom_label(text="",
                                         width=self.__label_width,
                                         height=self.__label_height,)

        btn_cancel.clicked.connect(lambda: self.reject())
        btn_enter.clicked.connect(self.__accept)


        layout_button = custom_box_layout(children=[btn_cancel, btn_enter],
                                          vertical=False,
                                          stretch=False)

        layout_password = custom_box_layout(children=[label_info,
                                                      self.line_input_password,
                                                      self.label_result,
                                                      layout_button],
                                            align="top")
        self.setLayout(layout_password)

    def __accept(self):
        # 2025.06.07: require encryption.
        input_password = self.line_input_password.text()

        if input_password == ConfigIni().get_auth_str():
            self.accept()
        else:
            self.label_result.setText("Not Authorized")
            self.label_result.setStyleSheet("color: red; font-weight:500;")

    def reject(self):
        sys.exit(-1)
