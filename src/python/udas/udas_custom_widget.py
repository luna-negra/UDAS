from functools import partial
from typing import Any
from .udas_pytool import (Qt,
                         QWidget,
                         QDialog,
                         QMessageBox,
                         QSplitter,
                         QVBoxLayout,
                         QHBoxLayout,
                         QFrame,
                         QComboBox,
                         QLabel,
                         QLineEdit,
                         QPushButton,
                         QTableWidget,
                         QTableWidgetItem,
                         QTextEdit,
                         QAbstractItemView,
                         ConfigIni,
                         change_password,
                         get_logs,
                         encrypt_str,
                         exit_process,)


COLOR_SEPARATE_LINE: str = "#333"

def custom_box_layout(children: list,
                      vertical: bool = True,
                      stretch: bool = True,
                      align: str = "center",
                      spacing: int = 10,
                      margin_l: int = 0,
                      margin_t: int = 0,
                      margin_r: int = 0,
                      margin_b: int = 0) -> QVBoxLayout | QHBoxLayout:
    l = QVBoxLayout() if vertical else QHBoxLayout()

    for child in children:
        if isinstance(child, QWidget):
            l.addWidget(child)

        elif isinstance(child, QHBoxLayout) or  isinstance(child, QVBoxLayout):
            l.addLayout(child)

    tmp_align = Qt.AlignCenter
    if stretch:
        if not vertical:
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

def custom_combobox(width: int,
                    height: int,
                    items_list: list,
                    default_item: str,
                    style: str | None = None,
                    tooltip: str | None = None,
                    status_tip: str | None = None,
                    enable: bool = True) -> QComboBox:
    cb = QComboBox()
    cb.addItems(items_list)
    cb.setFixedSize(width, height)
    cb.setStyleSheet(style)
    cb.setToolTip(tooltip)
    cb.setStatusTip(status_tip)
    cb.setCurrentIndex(items_list.index(default_item.upper()))
    cb.setEnabled(enable)
    return cb

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

def custom_push_button(text: str,
                       width: int,
                       height: int,
                       style: str | None = None,
                       connect: Any = None,
                       status_tip: str | None = None,
                       default: bool | None = None,
                       enable: bool = True,) -> QPushButton:
    b = QPushButton(text)
    b.setFixedSize(width, height)
    b.setStyleSheet(style)
    if connect is not None:
        b.clicked.connect(connect)
    b.setStatusTip(status_tip)
    if default is not None:
        b.setDefault(default)
    b.setEnabled(enable)
    return b

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

def custom_table(total_width: int,
                 total_height: int,
                 header_label: list,
                 table_data: list,
                 column_count: int | None = None,
                 row_count: int | None = None,
                 cell_align: str | None = "center",
                 is_enable: bool = False,
                 is_select_columns: bool = True,
                 is_single_selection: bool = True,
                 is_vertical_header: bool = False,
                 is_resize_row_to_contents: bool = False,
                 is_resize_column_to_contents: bool = False,) -> QTableWidget:

    t = QTableWidget()
    t.setFixedSize(total_width, total_height)

    # set row and column count
    t.setRowCount(row_count or 0)
    t.setColumnCount(column_count or len(header_label))

    # add column header
    t.setHorizontalHeaderLabels(header_label)

    # set cell text alignment
    text_align = Qt.AlignCenter
    if cell_align == "left":
        text_align = Qt.AlignLeft
    elif cell_align == "right":
        text_align = Qt.AlignRight

    # set select behavior
    if is_select_columns:
        t.setSelectionBehavior(QAbstractItemView.SelectRows)

    # set single selection
    if is_single_selection:
        t.setSelectionMode(QAbstractItemView.SingleSelection)

    # set visible on vertical header
    t.verticalHeader().setVisible(is_vertical_header)

    # add data into table.
    for row, data in enumerate(table_data):
        for col, atom in enumerate(data):
            item = QTableWidgetItem(str(atom))
            item.setTextAlignment(text_align)
            if t.rowCount() == row:
                t.setRowCount(t.rowCount() + 1)
            t.setItem(row, col, item)

    # set resize to content
    if is_resize_row_to_contents:
        t.resizeRowsToContents()

    if is_resize_column_to_contents:
        t.resizeColumnsToContents()

    # set enable
    if is_enable:
        t.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

    # stretch last column.
    t.horizontalHeader().setStretchLastSection(True)
    return t

def custom_text_edit(width: int,
                     height: int,
                     style: str | None = None,
                     enable: bool = False,
                     text: str = "",
                     ) -> QTextEdit:
    te = QTextEdit()
    te.setFixedSize(width, height)
    te.setStyleSheet(style)
    te.setText(text)
    if not enable:
        te.setTextInteractionFlags(Qt.NoTextInteraction)
    return te

def custom_widget_for_layout(width: int,
                             height: int,
                             style: str | None = None) -> QWidget:
    w = QWidget()
    w.setFixedSize(width, height)
    w.setStyleSheet(style)
    return w

def custom_labels_kv(total_width: int,
                     height: int,
                     key:str,
                     value: str,
                     ratio: float,
                     style: str | None = None,
                     key_style: str | None = None,
                     value_style: str | None = None,
                     align:str = "center",
                     spacing: int = 10) -> QWidget:

    key = f" ・ {key} : "
    label_key = custom_label(text=key,
                             width=int(total_width * ratio),
                             height=height,
                             style=key_style)
    label_value = custom_label(text=value,
                               width=int(total_width * (1 - ratio)),
                               height=height,
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
                                      height=height,
                                      style=style)
    widget.setLayout(layout)
    return widget

def custom_label_button_for_control(total_width: int,
                                    height: int,
                                    ratio: float,
                                    info_text: str,
                                    button_text: str,
                                    button_width: int,
                                    style: str | None = None,
                                    info_style: str | None = None,
                                    button_style: str | None = None,
                                    button_enable: bool = True,
                                    button_default: bool = False,
                                    stretch: bool = True,
                                    align: str = "center",
                                    spacing: int = 10,
                                    status_tip: str = "",
                                    connect: Any = None) -> QWidget:
    info_text = f" ・ {info_text}: " if info_text != "" else ""
    label_info = custom_label(text=info_text,
                              width=int(total_width * ratio),
                              height=height,
                              style=info_style)
    btn_ctrl = custom_push_button(text=button_text,
                                  width=button_width,
                                  height=height,
                                  style=button_style,
                                  connect=connect,
                                  status_tip=status_tip,
                                  default=button_default,
                                  enable=button_enable)
    layout = custom_box_layout(children=[label_info, btn_ctrl],
                               vertical=False,
                               stretch=stretch,
                               align=align,
                               spacing=spacing,
                               margin_l=0,
                               margin_t=0,
                               margin_r=0,
                               margin_b=0)
    widget = custom_widget_for_layout(width=total_width,
                                      height=height,
                                      style=style)
    widget.setLayout(layout)
    return widget


class CustomComboboxWithButton(QWidget):
    def __init__(self, **kwargs):
        super().__init__()

        self.__total_width: int = kwargs.get("total_width")
        self.__total_height: int = kwargs.get("total_height")
        self.__ratio: float = kwargs.get("ratio", 0.4)

        self.__label_text: str = kwargs.get("label_text")
        self.__label_style: str | None = kwargs.get("label_style", None)

        self.__combobox_width: int = kwargs.get("combobox_width")
        self.__combobox_items: list = kwargs.get("combobox_items")
        self.__combobox_default: str = kwargs.get("combobox_default")
        self.__combobox_style: str | None = kwargs.get("combobox_style", None)

        self.__button_width: int = kwargs.get("button_width")
        self.__button_text: str = kwargs.get("button_text")
        self.__button_status_tip: str = kwargs.get("button_status_tip", "")
        self.__button_style: str | None = kwargs.get("button_style", None)
        self.__button_connect: Any = kwargs.get("button_connect")

        # init_ui
        self.__init_ui()

    def __init_ui(self):
        self.setFixedSize(self.__total_width, self.__total_height)

        label = custom_label(text=self.__label_text,
                             width=int(self.__total_width * self.__ratio),
                             height=self.__total_height,
                             style=self.__label_style)

        self.combobox = custom_combobox(width=self.__combobox_width,
                                        height=self.__total_height,
                                        items_list=self.__combobox_items,
                                        default_item=self.__combobox_default,
                                        style=self.__combobox_style)

        self.__button = custom_push_button(text=self.__button_text,
                                         width=self.__button_width,
                                         height=self.__total_height,
                                         status_tip=self.__button_status_tip,
                                         style=self.__button_style,
                                         connect=self.__button_connect,
                                         enable=False)

        self.__combo_default_index = self.combobox.currentIndex()
        self.combobox.currentIndexChanged.connect(self.__on_change_combobox)

        layout = custom_box_layout(children=[label, self.combobox, self.__button], vertical=False,)
        self.setLayout(layout)
        return None

    def __on_change_combobox(self):
        self.__button.setEnabled(True) if self.combobox.currentIndex() != self.__combo_default_index \
            else self.__button.setEnabled(False)
        return None


class CustomDialogPasswordChange(QDialog):
    def __init__(self, **kwargs):
        super().__init__()
        self.__margin: int = 20
        self.__title: str = kwargs.get("title")
        self.__total_width: int = kwargs.get("total_width") - self.__margin * 2
        self.__total_height: int = kwargs.get("total_height")
        self.__ratio: float = kwargs.get("ratio")
        self.__style: str = kwargs.get("style", "")


        self.__label_text: str = kwargs.get("label_text")
        self.__label_width: int = kwargs.get("label_width")
        self.__label_height: int = kwargs.get("label_height")
        self.__label_style: str = kwargs.get("label_style", "")

        self.__line_input_style: str = kwargs.get("line_input_style", "")

        self.__button_width: int = kwargs.get("button_width")
        self.__button_style: str = kwargs.get("button_style", "")
        self.__init_ui()

    def __init_ui(self):
        # set size
        label_width: int = int(self.__total_width * self.__ratio)
        self.setWindowTitle(self.__title)
        self.setFixedSize(self.__total_width, self.__total_height)

        # set buttons
        button_enter = custom_push_button(text="Change",
                                          width=self.__button_width,
                                          height=self.__label_height,
                                          default=True)

        button_enter.clicked.connect(self.__accept)

        layout_buttons = custom_box_layout(children=[button_enter],
                                           vertical=False,
                                           stretch=True,
                                           align="center",
                                           margin_l=125)

        # set layout for old password
        label_old_pw = custom_label(text="・Current Password",
                                    width=label_width,
                                    height=self.__label_height,
                                    style=self.__label_style)

        self.__line_input_old_pw = custom_line_edit(width=self.__label_width,
                                                  height=self.__label_height,
                                                  style=self.__line_input_style,
                                                  tooltip="UDAS Current Password",
                                                  status_tip="Input Current UDAS Password...",
                                                  echo_mode=True)
        layout_old_pw = custom_box_layout(children=[label_old_pw, self.__line_input_old_pw],
                                          vertical=False)


        # set layout for new password
        label_new_pw = custom_label(text="・New Password",
                                    width=label_width,
                                    height=self.__label_height,
                                    style=self.__label_style)
        self.__line_input_new_pw = custom_line_edit(width=self.__label_width,
                                                  height=self.__label_height,
                                                  style=self.__line_input_style,
                                                  tooltip="New UDAS Password",
                                                  status_tip="Input New UDAS Password...",
                                                  echo_mode=True,)
        layout_new_pw = custom_box_layout(children=[label_new_pw, self.__line_input_new_pw],
                                          vertical=False)

        # set layout for new password retype
        label_new_repw = custom_label(text="・New Password Retype",
                                    width=label_width,
                                    height=self.__label_height,
                                    style=self.__label_style)
        self.__line_input_new_repw = custom_line_edit(width=self.__label_width,
                                                    height=self.__label_height,
                                                    style=self.__line_input_style,
                                                    tooltip="Retype New UDAS Password",
                                                    status_tip="Retype New UDAS Password...",
                                                    echo_mode=True)
        layout_new_repw = custom_box_layout(children=[label_new_repw, self.__line_input_new_repw],
                                            vertical=False)

        # set info label
        self.__label_info = custom_label(text="",
                                  width=self.__total_width,
                                  height=self.__label_height,
                                  style=self.__label_style)

        # set layout and apply to dialog
        widget_layout_buttons = custom_widget_for_layout(width=self.__total_width, height=self.__label_height,)
        widget_layout_buttons.setLayout(layout_buttons)
        layout = custom_box_layout(children=[layout_old_pw,
                                             layout_new_pw,
                                             layout_new_repw,
                                             self.__label_info,
                                             widget_layout_buttons],
                                   margin_l=self.__margin,
                                   margin_t=self.__margin,
                                   margin_b=self.__margin,
                                   margin_r=self.__margin)
        self.setLayout(layout)
        return None

    def __accept(self):
        if self.__line_input_old_pw.text() == "":
            self.__label_info.setStyleSheet("color:orange;")
            self.__label_info.setText("Please input your old UDAS password.")

        elif self.__line_input_new_pw.text() == "":
            self.__label_info.setStyleSheet("color:orange;")
            self.__label_info.setText("Please input your new UDAS password.")

        elif self.__line_input_new_repw.text() == "":
            self.__label_info.setStyleSheet("color:orange;")
            self.__label_info.setText("Please input your new UDAS password at last input.")

        elif not self.__is_new_password_match():
            self.__label_info.setStyleSheet("color:red;")
            self.__label_info.setText("New Password is not Match. Please check new password again.")

        else:
            cmd_result = change_password(old_pw=encrypt_str(string=self.__line_input_old_pw.text()),
                                         new_pw=encrypt_str(string=self.__line_input_new_pw.text()))
            if cmd_result.returncode == 0:
                self.accept()

            else:
                self.__label_info.setStyleSheet("color:orange;")
                self.__label_info.setText("Fail to update UDAS password. Please check old password again.")

        return None

    def __is_new_password_match(self) -> bool:
        return self.__line_input_new_pw.text() == self.__line_input_new_repw.text()


class CustomDialogPasswordInput(QDialog):
    def __init__(self, **kwargs):
        super().__init__()

        try:
            self.__auth_str = ConfigIni().get_auth_str()

        except AttributeError:
            msg_box = QMessageBox()
            msg_box.setIcon(QMessageBox.Critical)
            msg_box.setText("UDAS config file is not found.")
            msg_box.exec()
            self.reject(-3)

        else:
            self.__init_ui(kwargs)
            self.__label_width: int = self.width() - 20
            self.__label_height: int = 25
            self.__layout_button_margin: int = 25
            self.__btn_width: int = int((self.width() - self.__layout_button_margin * 2) / 2)
            self.__btn_height: int = 30
            self.__set_widget()

    def __init_ui(self, kwargs):
        self.setWindowTitle(kwargs.get("title") or "UDAS Authentication")
        self.setFixedWidth(kwargs.get("width") or 400)
        self.setFixedHeight(kwargs.get("height") or 200)

    def __set_widget(self):
        label_info = custom_label(text="Enter the UDAS Password to register new trusted device.\n",
                                  width=self.width() - 20,
                                  height=100)

        self.line_input_password = custom_line_edit(width=self.__label_width,
                                                    height=self.__label_height,
                                                    tooltip="UDAS Password",
                                                    status_tip="Input Password",
                                                    echo_mode=True,)

        btn_cancel = custom_push_button(text="Cancel",
                                        width=self.__btn_width,
                                        height=self.__btn_height,)

        btn_enter = custom_push_button(text="OK",
                                       width=self.__btn_width,
                                       height=self.__btn_height,
                                       default=True)

        self.label_result = custom_label(text="",
                                         width=self.__label_width,
                                         height=self.__label_height,)

        btn_cancel.clicked.connect(self.reject)
        btn_enter.clicked.connect(self.__accept)

        layout_button = custom_box_layout(children=[btn_cancel, btn_enter],
                                          vertical=False,
                                          stretch=False,
                                          margin_l=self.__layout_button_margin,
                                          margin_r=self.__layout_button_margin,)

        layout_password = custom_box_layout(children=[label_info,
                                                      self.line_input_password,
                                                      self.label_result,
                                                      layout_button],
                                            align="top",
                                            margin_l=10,
                                            margin_t=10,
                                            margin_r=10,
                                            margin_b=10,)

        self.setLayout(layout_password)

    def __accept(self):
        if self.line_input_password.text() == "":
            self.label_result.setStyleSheet("color: orange; font-weight:500;")
            self.label_result.setText("Please input your UDAS password.")

        elif encrypt_str(string=self.line_input_password.text()) != self.__auth_str:
            self.label_result.setStyleSheet("color: red; font-weight:500;")
            self.label_result.setText("Not Authorized")

        else:
            self.accept()

    def reject(self, exit_code: int=-1):
        exit_process(exit_code)


class CustomLabelWithButton(QWidget):
    def __init__(self, **kwargs):
        super().__init__()
        self.__total_width: int = kwargs.get("total_width")
        self.__total_height: int = kwargs.get("height")
        self.__ratio: float = kwargs.get("ratio", 0.5)

        self.__label_width: int = int(self.__total_width * self.__ratio)
        self.__label_text: str = kwargs.get("label_text")
        self.__label_style: str | None = kwargs.get("label_style", None)

        self.__button_width: int = kwargs.get("button_width")
        self.__button_text: str = kwargs.get("button_text")
        self.__button_style: str | None = kwargs.get("button_style", None)
        self.__button_status_tip: str = kwargs.get("button_status_tip", "")
        self.__button_default: bool = kwargs.get("button_default", False)
        self.__button_enable: bool = kwargs.get("button_enable", True)
        self.__button_connect: Any = kwargs.get("connect", None)

        self.__init_ui()

    def __init_ui(self):
        self.setFixedSize(self.__total_width, self.__total_height)

        label = custom_label(text=self.__label_text,
                             width=self.__label_width,
                             height=self.__total_height,
                             style=self.__label_style)

        button = custom_push_button(text=self.__button_text,
                                         width=self.__button_width,
                                         height = self.__total_height,
                                         style=self.__button_style,
                                         default=self.__button_default,
                                         status_tip=self.__button_status_tip,
                                         enable=self.__button_enable,
                                         connect=self.__button_connect,)

        layout = custom_box_layout(children=[label, button], vertical=False)
        self.setLayout(layout)
        return None


class CustomLogViewer(QWidget):
    def __init__(self, **kwargs):
        super().__init__()
        self.__total_width: int = kwargs.get("total_width")
        self.__total_height: int = kwargs.get("total_height")

        self.__text_edit_height: int = kwargs.get("text_edit_height")
        self.__text_edit_style: str | None = kwargs.get("text_edit_style", None)
        self.__text_edit_enable: bool = kwargs.get("text_edit_enable", False)

        self.__button_text_list: list = ["ERROR", "WARNING", "INFO", "DEBUG"]
        self.__button_width: int = int((self.__total_width / len(self.__button_text_list)) - 10)
        self.__button_height: int = 30
        self.__button_style: str | None = kwargs.get("button_style", None)

        self.__init_ui()


    def __init_ui(self):
        # create text_editor to show logs.
        self.__text_editor = custom_text_edit(width=self.__total_width,
                                              height=self.__text_edit_height,
                                              style=self.__text_edit_style,
                                              enable=self.__text_edit_enable)

        # print out all logs.
        self.__get_logs()

        # create buttons for log level
        button_list: list = []
        for btn_text in self.__button_text_list:
            button_list.append(custom_push_button(width=self.__button_width,
                                                  height=self.__button_height,
                                                  text=f"{btn_text}",
                                                  style=self.__button_style,
                                                  status_tip=f"Show {btn_text.lower()} logs...",
                                                  connect=partial(self.__get_logs, btn_text)))

        buttons_layout = custom_box_layout(children=button_list, vertical=False,)

        # create layout
        layout = custom_box_layout(children=[self.__text_editor,
                                             custom_separate_line(color=COLOR_SEPARATE_LINE),
                                             buttons_layout])
        self.setLayout(layout)
        return None

    def __get_logs(self, grep: str | None = None) -> None:
        logs = get_logs(grep=grep).stdout.decode("utf-8").replace(": [", ":\n[").replace("] ", "]\n")
        self.__text_editor.setText(logs)
        return None


class CustomMessageBox(QMessageBox):
    def __init__(self, **kwargs):
        super().__init__()
        self.__text = kwargs.get("msg_box_text")
        self.__msg_box_type = kwargs.get("msg_box_type", "information")
        self.__init_ui()

    def __init_ui(self):
        # set text for MessageBox
        self.setText(self.__text)

        # set icon for MessageBox
        if self.__msg_box_type == "information":
            self.setIcon(QMessageBox.Information)
            self.setStandardButtons(QMessageBox.Ok)
            self.setDefaultButton(QMessageBox.Ok)

        elif self.__msg_box_type == "Warning":
            self.setIcon(QMessageBox.Warning)
            self.setStandardButtons(QMessageBox.Ok)
            self.setDefaultButton(QMessageBox.Ok)

        elif self.__msg_box_type == "Critical":
            self.setIcon(QMessageBox.Critical)
            self.setStandardButtons(QMessageBox.Abort)
            self.setDefaultButton(QMessageBox.Abort)

        elif self.__msg_box_type == "Question":
            self.setIcon(QMessageBox.Question)
            self.setStandardButtons(QMessageBox.No | QMessageBox.Yes)
            self.setDefaultButton(QMessageBox.No)

        return


class CustomTableWithOneButton(QWidget):
    def __init__(self, **kwargs):
        super().__init__()

        self.__total_width: int = kwargs.get("total_width")

        self.__label_height: int = kwargs.get("label_height")
        self.__label_text: str = kwargs.get("label_text")
        self.__label_style: str = kwargs.get("label_style")

        self.__table_height: int = kwargs.get("table_height")
        self.__table_header: list = kwargs.get("table_header", [])
        self.__table_data: list = kwargs.get("table_data", [])
        self.__table_row_count: int = kwargs.get("table_row_count")
        self.__table_column_count: int = kwargs.get("table_column_count")
        self.__table_cell_align: str = kwargs.get("table_cell_align", "center")
        self.__is_enable: bool = kwargs.get("is_enable", True)
        self.__is_select_columns: bool = kwargs.get("is_select_columns", True)
        self.__is_vertical_header: bool = kwargs.get("is_vertical_header", False)
        self.__is_resize_row_to_contents: bool = kwargs.get("is_resize_row_to_contents", False)
        self.__is_resize_column_to_contents: bool = kwargs.get("is_resize_column_to_contents", False)

        self.__ratio: float = kwargs.get("ratio")
        self.__button_align: str = kwargs.get("align", "right")
        self.__button_width: int = kwargs.get("button_width")
        self.__button_height: int = kwargs.get("button_height")
        self.__button_text: str = kwargs.get("button_text")
        self.__button_style: str = kwargs.get("button_style")
        self.__button_enable: bool = kwargs.get("button_enable", False)
        self.__button_default: bool = kwargs.get("button_default", False)
        self.__button_stretch: bool = kwargs.get("button_stretch", True)
        self.__button_status_tip: str = kwargs.get("button_status_tip")
        self.__button_connect: Any = kwargs.get("button_connect")

        self.__init_ui()

    def __init_ui(self):
        self.setFixedWidth(self.__total_width,)

        label = custom_label(text=self.__label_text,
                             width=self.__total_width,
                             height=self.__label_height,
                             style=self.__label_style)

        self.table = custom_table(total_width=self.__total_width,
                                    total_height=self.__table_height,
                                    header_label=self.__table_header,
                                    table_data=self.__table_data,
                                    column_count=self.__table_column_count,
                                    row_count=self.__table_row_count,
                                    cell_align=self.__table_cell_align,
                                    is_enable=self.__is_enable,
                                    is_select_columns=self.__is_select_columns,
                                    is_vertical_header=self.__is_vertical_header,
                                    is_resize_row_to_contents=self.__is_resize_row_to_contents,
                                    is_resize_column_to_contents=self.__is_resize_column_to_contents)

        self.table.itemClicked.connect(self.__on_click_table_item)

        self.__button = custom_push_button(text=self.__button_text,
                                           width=self.__button_width,
                                           height=self.__button_height,
                                           style=self.__button_style,
                                           connect=self.__button_connect,
                                           enable=self.__button_enable,
                                           default=self.__button_default,
                                           status_tip=self.__button_status_tip)

        self.__button.clicked.connect(self.__button_connect)

        blank_label = custom_label(text="",
                                   width=int(self.__total_width * self.__ratio),
                                   height=self.__button_height)

        layout_button = custom_box_layout(children=[blank_label, self.__button],
                                          vertical=False,
                                          stretch=self.__button_stretch,
                                          align=self.__button_align,)

        layout = custom_box_layout(children=[label, self.table, layout_button],)
        self.setLayout(layout)
        return None

    def __on_click_table_item(self):
        self.__button.setEnabled(True)
