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
                         QAbstractItemView,
                         ConfigIni,
                         exit_process,
                         remove_registered_usb_info,)


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
                       default: bool = False,
                       enable: bool = True,) -> QPushButton:
    b = QPushButton(text)
    b.setFixedSize(width, height)
    b.setStyleSheet(style)
    if connect is not None:
        b.clicked.connect(connect)
    b.setStatusTip(status_tip)
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
        t.setSelectionBehavior(QTableWidget.SelectRows)

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

def custom_label_combobox_for_control(total_width: int,
                                      height: int,
                                      ratio: float,
                                      info_text: str,
                                      combobox_width: int,
                                      combobox_items: list,
                                      default_item: str,
                                      style: str | None = None,
                                      info_style: str | None = None,
                                      combobox_style: str | None = None,
                                      status_tip: str | None = None,
                                      align: str = "center",
                                      spacing: int = 10,) -> QWidget:

    label_info = custom_label(text=info_text,
                              width=int(total_width * ratio),
                              height=height,
                              style=info_style,)
    combobox = custom_combobox(width=combobox_width,
                               height=height,
                               style=combobox_style,
                               items_list=combobox_items,
                               default_item=default_item,
                               status_tip=status_tip,)
    layout = custom_box_layout(children=[label_info, combobox],
                               vertical=False,
                               align=align,
                               spacing=spacing)

    widget = custom_widget_for_layout(width=total_width, height=height, style=style)
    widget.setLayout(layout)
    return widget


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

        btn_enter = custom_push_button(text="Override",
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
        # 2025.06.07: require encryption.
        input_password = self.line_input_password.text()

        if input_password == self.__auth_str:
            self.accept()
        else:
            self.label_result.setText("Not Authorized")
            self.label_result.setStyleSheet("color: red; font-weight:500;")

    def reject(self, exit_code: int=-1):
        exit_process(exit_code)

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
        label = custom_label(text=self.__label_text,
                             width=self.__total_width,
                             height=self.__label_height,
                             style=self.__label_style)

        self.__table = custom_table(total_width=self.__total_width,
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

        self.__table.itemClicked.connect(lambda: self.__on_click_table_item())

        self.__button = custom_push_button(text=self.__button_text,
                                           width=self.__button_width,
                                           height=self.__button_height,
                                           style=self.__button_style,
                                           connect=self.__button_connect,
                                           enable=self.__button_enable,
                                           default=self.__button_default,
                                           status_tip=self.__button_status_tip)

        self.__button.clicked.connect(lambda: self.__on_click_remove_item())

        blank_label = custom_label(text="",
                                   width=int(self.__total_width * self.__ratio),
                                   height=self.__button_height)

        layout_button = custom_box_layout(children=[blank_label, self.__button],
                                          vertical=False,
                                          stretch=self.__button_stretch,
                                          align=self.__button_align,)

        layout = custom_box_layout(children=[label, self.__table, layout_button],)
        self.setLayout(layout)
        return None

    def __on_click_table_item(self):
        self.__button.setEnabled(True)

    def __on_click_remove_item(self):
        selected_item: list = self.__table.selectedItems()
        row: int = self.__table.currentRow()
        manufacturer, id_vendor = [ text.strip("()") for text in selected_item[0].text().split() ]
        product, id_product = [ text.strip("()") for text in selected_item[1].text().split() ]
        serial = selected_item[2].text()

        cmd_result = remove_registered_usb_info(id_vendor=id_vendor,
                                                id_product=id_product,
                                                serial=serial,
                                                manufacturer=manufacturer,
                                                product=product,)
        # exit_code:
        # 0 - OK,
        # 1 - Error with command usage,
        # 126 - cancelled,
        # 127 - Not exist command
        exit_code = cmd_result.returncode
        if exit_code == 0:
            self.__table.removeRow(row)
            # MessageBox

        elif exit_code == 1:
            print("[ERROR] COMMAND ERROR")
            print(exit_code)
            # MessageBox

        elif exit_code == 127:
            print("[ERROR] NO COMMAND EXIST")
            # MessageBox

        else:
            print(exit_code)
            print(cmd_result.stdout)

        return None