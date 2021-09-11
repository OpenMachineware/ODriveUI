import json

from pathlib import Path
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

from conf.conf import ODRIVE_CONF_FILE
from utils.decode_interface import decode_to_dict


class ODriveConfig(QWidget):
    sig_conf_changed = Signal()

    def __init__(self, conf, parent=None):
        super(ODriveConfig, self).__init__(parent)
        self.setWindowTitle('Config')
        self.setObjectName('config_window')
        self.setWindowModality(Qt.ApplicationModal)
        self.resize(1024, 600)

        self.conf = conf
        self.drive = None
        self.drive_index = 0
        self.changed_settings = {}
        self.drive_dict_list = []

        self.pixmap_success = QPixmap('resources/success.png')
        self.pixmap_failure = QPixmap('resources/failure.png')
        self.icon_success = QIcon()
        self.icon_success.addPixmap(self.pixmap_success,
                                    QIcon.Normal, QIcon.Off)
        self.icon_failure = QIcon()
        self.icon_failure.addPixmap(self.pixmap_failure,
                                    QIcon.Normal, QIcon.Off)

        self.device_tree = QTreeView()
        self.device_tree.setHeaderHidden(True)
        self.device_tree.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.device_tree.clicked.connect(self.item_selected)

        op_h_box = QHBoxLayout()
        self.sampling_period_label = QLabel('Sampling Period')
        self.sampling_period_spin = QSpinBox()
        self.sampling_period_spin.setValue(20)
        self.sampling_period_unit_label = QLabel('ms')
        self.btn_apply = QPushButton('Apply')
        self.btn_apply.clicked.connect(self.apply_changes)
        self.btn_save = QPushButton('Save Configuration')
        self.btn_erase = QPushButton('Erase Configuration')
        self.btn_reboot = QPushButton('Reboot')
        op_h_box.addWidget(self.sampling_period_label)
        op_h_box.addWidget(self.sampling_period_spin)
        op_h_box.addWidget(self.sampling_period_unit_label)
        op_h_box.addStretch()
        op_h_box.addWidget(self.btn_apply)
        op_h_box.addStretch()
        op_h_box.addWidget(self.btn_save)
        op_h_box.addWidget(self.btn_erase)
        op_h_box.addWidget(self.btn_reboot)

        scroll_v_box = QVBoxLayout()
        self.scroll_area = QScrollArea()
        self.scroll_area.setObjectName('scroll_area')
        self.scroll_area.setWidgetResizable(True)
        self.scroll_contents = QWidget()
        self.scroll_contents.setObjectName('scroll_contents')
        self.scroll_area.setWidget(self.scroll_contents)
        scroll_contents_gird = QGridLayout()
        self.scroll_contents.setLayout(scroll_contents_gird)
        self.scroll_content_gird = QGridLayout()
        scroll_contents_gird.addLayout(self.scroll_content_gird, 0, 0)
        scroll_v_box.addLayout(op_h_box)
        scroll_v_box.addWidget(self.scroll_area)

        self.general_layout = None

        main_h_box = QHBoxLayout()
        main_h_box.addWidget(self.device_tree)
        main_h_box.addLayout(scroll_v_box)
        self.setLayout(main_h_box)

    def pass_odrive(self, drive, drive_index):
        self.drive = drive
        self.drive_index = drive_index
        self.device_tree.setDisabled(False)
        self.setWindowTitle('Config: ' + 'odrv' + str(drive_index))
        model = self.setup_odrive_model(drive, drive_index)
        self.device_tree.setModel(model)
        self.device_tree.expandAll()
        self.device_tree.selectionModel().selectionChanged.connect(
            self.item_selected)
        self.device_tree.setCurrentIndex(model.index(0, 0))

    def setup_odrive_model(self, drive, odrive_number):
        model = QStandardItemModel(0, 1, self)
        self.drive_dict_list = []
        item = QStandardItem('odrv' + str(odrive_number))
        drive_dict = decode_to_dict(drive, drive, is_config_object=True)
        self.drive_dict_list.append(drive_dict)
        for key in drive_dict.keys():
            if isinstance(drive_dict[key], dict):
                child = QStandardItem(key)
                for child_key in drive_dict[key].keys():
                    if isinstance(drive_dict[key][child_key], dict):
                        sub_child = QStandardItem(child_key)
                        child.appendRow(sub_child)
                item.appendRow(child)
        model.setItem(odrive_number, 0, item)
        return model

    def delete_items(self, del_layout):
        if del_layout is not None and del_layout.count() > 0:
            while del_layout.count():
                item = del_layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
                else:
                    self.delete_items(item.layout())

    def item_selected(self):
        self.changed_settings = {}
        self.delete_items(self.scroll_content_gird)
        self.setup_config_page()

    def setup_config_page(self):
        drive = self.drive
        path_list = []
        path_list = self.find_tree_parents(
            self.device_tree.selectedIndexes()[0], path_list)
        row_index = 0
        col_index = 1
        path_len = len(path_list)
        path_list.reverse()
        drive_dict = self.drive_dict_list[int(path_list[0][-1])]

        self.general_layout = QGridLayout()
        self.scroll_content_gird.addLayout(self.general_layout, 0, 0)

        if path_len == 1:
            self.setup_general(drive_dict)
        elif path_len == 2:
            if isinstance(drive_dict[path_list[1]], dict):
                for key in drive_dict[path_list[1]].keys():
                    if isinstance(drive_dict[path_list[1]][key], dict):
                        pass
                    else:

                        item_layout = self.add_single_layout_line(key, eval(
                            'drive.{}'.format(path_list[1])))
                        self.general_layout.addLayout(item_layout, row_index, 0,
                                                      1, 1)
                        row_index += 1
            spacer_item = QSpacerItem(1, 1,
                                      QSizePolicy.Minimum,
                                      QSizePolicy.Expanding)
            self.general_layout.addItem(spacer_item, row_index, 0, 1, 1)
        elif path_len == 3:
            if isinstance(drive_dict[path_list[1]][path_list[2]], dict):
                group = self.setup_group_box(path_list[2], eval(
                    'drive.{}.{}'.format(path_list[1], path_list[2])),
                                             drive_dict[path_list[1]][
                                                 path_list[2]])

                self.member_layout = QGridLayout()
                self.scroll_content_gird.addLayout(self.member_layout, 0,
                                                   col_index, 1, 1)
                self.member_layout.addWidget(group, 0, 0, 1, 1)
                spacer_item = QSpacerItem(1, 1,
                                          QSizePolicy.Minimum,
                                          QSizePolicy.Expanding)
                self.member_layout.addItem(spacer_item, 1, 0, 1, 1)
                col_index += 1
            spacer_item = QSpacerItem(1, 1,
                                      QSizePolicy.Minimum,
                                      QSizePolicy.Expanding)
            self.general_layout.addItem(spacer_item, row_index, 0, 1, 1)

    def setup_general(self, drive_dict):
        row_index = 0
        self.delete_items(self.scroll_content_gird)
        for item in drive_dict.keys():
            if isinstance(drive_dict[item], dict):
                pass
            else:
                item_layout = self.add_single_layout_line(item, self.drive)
                self.scroll_content_gird.addLayout(item_layout,
                                                   row_index, 1)
                row_index += 1
        spacer_item = QSpacerItem(1, 1,
                                  QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.scroll_content_gird.addItem(spacer_item, row_index, 1)

    def value_changed_test(self, haha):
        path_list = []
        item_value = self.sender().value()
        path_list.append(self.sender().objectName())
        self.find_parent_path(self.sender(), path_list)
        path_list = self.clean_up_path(path_list)
        index = self.device_tree.selectedIndexes()[0]
        tree_selection = index.model().itemFromIndex(index).text()
        parent_path = []
        parent_path = self.find_tree_parents(
            self.device_tree.selectedIndexes()[0],
            parent_path)
        if len(parent_path) == 3:
            parent_path.pop(0)
        path_list.extend(parent_path)
        palette = QPalette()
        palette.setColor(QPalette.Base, Qt.yellow)
        self.sender().setPalette(palette)
        palette = QPalette()
        palette.setColor(QPalette.Button, Qt.yellow)
        self.btn_apply.setPalette(palette)
        if str(path_list) in self.changed_settings:
            self.changed_settings[str(path_list)]['value'] = item_value
        else:
            self.changed_settings[str(path_list)] = {}
            self.changed_settings[str(path_list)]['value'] = item_value
            self.changed_settings[str(path_list)]['path'] = path_list

    def find_tree_parents(self, index, path_list):
        if index.model() is None:
            return path_list
        else:
            path_list.append(index.model().itemFromIndex(index).text())
            path_list = self.find_tree_parents(index.parent(), path_list)
        return path_list

    def find_parent_path(self, obj, path_list):
        if obj.parent() is None:
            return path_list
        else:
            path_list.append(obj.parent().objectName())
            self.find_parent_path(obj.parent(), path_list)
        return path_list

    def clean_up_path(self, path_list):
        path_list.remove('scroll_contents')
        path_list.remove('qt_scrollarea_viewport')
        path_list.remove('scroll_area')
        path_list.remove('config_window')
        try:
            path_list.remove('')
            path_list.remove('')
            path_list.remove('')
            path_list.remove('')
            path_list.remove('')
        except:
            pass

        return path_list

    def radio_button_changed(self):
        path_list = []
        path_list.append(self.sender().objectName())
        if self.sender().checkedButton().objectName() == 'True':
            item_value = True
        else:
            item_value = False
        self.find_parent_path(self.sender(), path_list)
        path_list = self.clean_up_path(path_list)
        index = self.device_tree.selectedIndexes()[0]
        tree_selection = index.model().itemFromIndex(index).text()
        if tree_selection == 'General':
            pass
        else:
            path_list.append(tree_selection)
        palette = QPalette()
        palette.setColor(QPalette.Base, Qt.yellow)
        self.sender().checkedButton().setPalette(palette)
        palette = QPalette()
        palette.setColor(QPalette.Button, Qt.yellow)
        self.btn_apply.setPalette(palette)
        if str(path_list) in self.changed_settings:
            self.changed_settings[str(path_list)]['value'] = item_value
        else:
            self.changed_settings[str(path_list)] = {}
            self.changed_settings[str(path_list)]['value'] = item_value
            self.changed_settings[str(path_list)]['path'] = path_list

    def apply_changes(self):
        drive_key = 'odrive' + str(self.drive_index)
        if drive_key in self.conf:
            drive_conf = self.conf[drive_key]
        else:
            drive_conf = {}
        drive_conf['sampling_period'] = self.sampling_period_spin.value()
        self.conf[drive_key] = drive_conf
        with open(ODRIVE_CONF_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.conf, f, ensure_ascii=False, indent=4)
        self.sig_conf_changed.emit()

        drive = self.drive
        for key in self.changed_settings:
            path_length = len(self.changed_settings[key]['path'])
            path = self.changed_settings[key]['path']
            if path_length == 3:
                exec('drive.{}.{} = {}'.format(path[-2], path[-3],
                                               self.changed_settings[key][
                                                   'value']))
            elif path_length == 4:
                exec('drive.{}.{}.{} = {}'.format(path[-2], path[-3], path[-4],
                                                  self.changed_settings[key][
                                                      'value']))
            elif path_length == 5:
                exec('drive.{}.{}.{}.{} = {}'.format(path[-2], path[-3],
                                                     path[-4], path[-5],
                                                     self.changed_settings[
                                                         key]['value']))
            elif path_length == 6:
                exec('drive.{}.{}.{}.{}.{} = {}'.format(path[-2], path[-3],
                                                        path[-4], path[-5],
                                                        path[-6],
                                                        self.changed_settings[
                                                            key]['value']))
        self.item_selected()

    def reset_odrive(self):
        self.delete_items(self.scroll_content_gird)
        self.odrive_connect()

    def odrive_reboot(self):
        try:
            self.drive.reboot()
        except Exception as e:
            print('exception rebooting,: {}'.format(e))
        try:
            self.odrive_worker.stop()
        except Exception as e:
            print('exception stopping, closing: {}'.format(e))
        self.delete_items(self.scroll_content_gird)
        self.odrive_connect()

    def odrive_save_configuration(self):
        self.drive.save_configuration()
        self.reset_odrive()

    def odrive_erase_configuration(self):
        self.drive.erase_configuration()
        self.reset_odrive()

    def function_button_pressed(self):
        button_name = self.sender().objectName()
        if button_name == 'clear_errors':
            self.drive.clear_errors()

    def add_function(self, item, drive):
        h_box = QHBoxLayout()
        function_button = QPushButton()
        function_button.setText(item['name'])
        function_button.setObjectName(item['name'])
        function_button.pressed.connect(self.function_button_pressed)
        h_box.addWidget(function_button)
        if item['inputs']:
            for input_item in item['inputs']:
                if input_item['type'] == 'int32':
                    h_box.addLayout(self.add_input_int32(input_item))
                elif input_item['type'] == 'uint32':
                    h_box.addLayout(self.add_input_uint32(input_item))
                elif input_item['type'] == 'float':
                    h_box.addLayout(self.add_input_float(input_item))
                elif input_item['type'] == 'bool':
                    h_box.addLayout(self.add_input_bool(input_item))
                else:
                    print('MISSING INPUT TYPE: {}'.format(input_item['type']))
        return h_box

    # float, bool, json, uint64, uint8, uint32, object,  uint16, int32
    def add_single_layout_line(self, item, drive):
        line_layout = QGridLayout()
        ret_type = eval('drive._{}_property.read._outputs[0][1]'.format(item))
        if ret_type == 'float':
            line_layout.addLayout(self.add_float(item, drive), 0, 0)
        elif ret_type == 'bool':
            line_layout.addLayout(self.add_bool(item, drive), 0, 0)
        elif ret_type == 'uint8':
            line_layout.addLayout(self.add_uint8(item, drive), 0, 0)
        elif ret_type == 'uint16':
            line_layout.addLayout(self.add_uint16(item, drive), 0, 0)
        elif ret_type == 'uint32':
            line_layout.addLayout(self.add_uint32(item, drive), 0, 0)
        elif ret_type == 'uint64':
            line_layout.addLayout(self.add_uint64(item, drive), 0, 0)
        elif ret_type == 'int32':
            line_layout.addLayout(self.add_int32(item, drive), 0, 0)
        else:
            print('MISSING implementation {')
            print(item)
        return line_layout

    def add_input_bool(self, item):
        h_box = QHBoxLayout()
        label = QLabel()
        label.setText(item['name'])
        h_box.addWidget(label)
        if item['access'] == 'rw':
            radio_true = QRadioButton()
            radio_true.setObjectName('True')
            radio_false = QRadioButton()
            radio_false.setObjectName('False')
            radio_true.setIcon(self.icon_success)
            radio_false.setIcon(self.icon_failure)
            btn_group = QButtonGroup(h_box)
            btn_group.setObjectName(item['name'])
            btn_group.addButton(radio_true)
            btn_group.addButton(radio_false)
            h_box_check = QHBoxLayout()
            h_box_check.addWidget(radio_true)
            h_box_check.addWidget(radio_false)
            h_box.addLayout(h_box_check)
        return h_box

    def add_input_float(self, item):
        h_box = QHBoxLayout()
        label = QLabel()
        label.setText(item['name'])
        h_box.addWidget(label)
        if item['access'] == 'rw':
            val_label = QDoubleSpinBox()
            val_label.setObjectName(item['name'])
            val_label.setMaximum(2147483647)
            val_label.setMinimum(-2147483647)
            val_label.setDecimals(8)
        h_box.addWidget(val_label)
        return h_box

    def add_input_uint32(self, item):
        h_box = QHBoxLayout()
        label = QLabel()
        label.setText(item['name'])
        h_box.addWidget(label)
        if item['access'] == 'rw':
            val_label = QSpinBox()
            val_label.setObjectName(item['name'])
            val_label.setMaximum(2147483647)
        h_box.addWidget(val_label)
        return h_box

    def add_input_int32(self, item):
        h_box = QHBoxLayout()
        label = QLabel()
        label.setText(item['name'])
        h_box.addWidget(label)
        if item['access'] == 'rw':
            val_label = QSpinBox()
            val_label.setObjectName(item['name'])
            val_label.setMaximum(32768)
            val_label.setMinimum(-32768)
        h_box.addWidget(val_label)
        return h_box

    def add_bool(self, item, drive):
        h_box = QHBoxLayout()
        label = QLabel()
        label.setText(item)
        h_box.addWidget(label)
        exchange_property = eval('drive._{}_property'.format(item))
        item_value = eval('drive.{}'.format(item))
        if not hasattr(exchange_property, 'exchange'):
            val = QLabel()
            if item_value:
                scaled = self.pixmap_success.scaled(QSize(16, 16),
                                                    Qt.KeepAspectRatio)
                val.setPixmap(scaled)
            else:
                scaled = self.pixmap_failure.scaled(QSize(16, 16),
                                                    Qt.KeepAspectRatio)
                val.setPixmap(scaled)
            h_box.addWidget(val)
        elif hasattr(exchange_property, 'exchange'):
            radio_ture = QRadioButton()
            radio_false = QRadioButton()
            radio_ture.setIcon(self.icon_success)
            radio_false.setIcon(self.icon_failure)
            btn_group = QButtonGroup(h_box)
            btn_group.buttonClicked.connect(self.radio_button_changed)
            btn_group.addButton(radio_ture)
            btn_group.addButton(radio_false)
            if item_value:
                radio_ture.setChecked(True)
            else:
                radio_false.setChecked(True)
            radio_h_box = QHBoxLayout()
            radio_h_box.addWidget(radio_ture)
            radio_h_box.addWidget(radio_false)
            h_box.addLayout(radio_h_box)
        return h_box

    def add_float(self, item, drive):
        h_box = QHBoxLayout()
        label = QLabel()
        label.setText(item)
        h_box.addWidget(label)
        exchange_property = eval('drive._{}_property'.format(item))
        if hasattr(exchange_property, 'exchange'):
            val = QDoubleSpinBox()
            val.setMaximum(2147483647)
            val.setMinimum(-2147483647)
            val.setDecimals(8)
            val.setValue(eval('drive.{}'.format(item)))
            val.valueChanged.connect(self.value_changed_test)
        else:
            val = QLabel()
            val.setText(str(eval('drive.{}'.format(item))))
        h_box.addWidget(val)
        return h_box

    def add_uint64(self, item, drive):
        h_box = QHBoxLayout()
        label = QLabel()
        label.setText(item)
        h_box.addWidget(label)
        exchange_property = eval('drive._{}_property'.format(item))
        if not hasattr(exchange_property, 'exchange'):
            val = QLabel()
            val.setText(str(eval('drive.{}'.format(item))))
        elif hasattr(exchange_property, 'exchange'):
            val = QSpinBox()
            val.setMaximum(2147483647)
            val.setValue(eval('drive.{}'.format(item)))
            val.valueChanged.connect(self.value_changed_test)
        h_box.addWidget(val)
        return h_box

    def add_uint32(self, item, drive):
        h_box = QHBoxLayout()
        label = QLabel()
        label.setText(item)
        h_box.addWidget(label)
        exchange_property = eval('drive._{}_property'.format(item))
        if not hasattr(exchange_property, 'exchange'):
            val = QLabel()
            val.setText(str(eval('drive.{}'.format(item))))
        elif hasattr(exchange_property, 'exchange'):
            val = QSpinBox()
            val.setMaximum(2147483647)
            val.setValue(eval('drive.{}'.format(item)))
            val.valueChanged.connect(self.value_changed_test)
        h_box.addWidget(val)
        return h_box

    def add_uint16(self, item, drive):
        h_box = QHBoxLayout()
        label = QLabel()
        label.setText(item)
        h_box.addWidget(label)
        exchange_property = eval('drive._{}_property'.format(item))
        if not hasattr(exchange_property, 'exchange'):
            val = QLabel()
            val.setText(str(eval('drive.{}'.format(item))))
        elif hasattr(exchange_property, 'exchange'):
            val = QSpinBox()
            val.setMaximum(65536)
            val.setValue(eval('drive.{}'.format(item)))
            val.valueChanged.connect(self.value_changed_test)
        h_box.addWidget(val)
        return h_box

    def add_uint8(self, item, drive):
        h_box = QHBoxLayout()
        label = QLabel()
        label.setText(item)
        h_box.addWidget(label)
        exchange_property = eval('drive._{}_property'.format(item))
        if not hasattr(exchange_property, 'exchange'):
            val = QLabel()
            val.setText(str(eval('drive.{}'.format(item))))
        elif hasattr(exchange_property, 'exchange'):
            val = QSpinBox()
            val.setMaximum(256)
            val.setValue(eval('drive.{}'.format(item)))
            val.valueChanged.connect(self.value_changed_test)
        h_box.addWidget(val)
        return h_box

    def add_int32(self, item, drive):
        h_box = QHBoxLayout()
        label = QLabel()
        label.setText(item)
        h_box.addWidget(label)
        exchange_property = eval('drive._{}_property'.format(item))
        if not hasattr(exchange_property, 'exchange'):
            val = QLabel()
            val.setText(str(eval('drive.{}'.format(item))))
        elif hasattr(exchange_property, 'exchange'):
            val = QSpinBox()
            val.setMaximum(32768)
            val.setMinimum(-32768)
            val.setValue(eval('drive.{}'.format(item)))
            val.valueChanged.connect(self.value_changed_test)
        h_box.addWidget(val)
        return h_box

    def setup_group_box(self, item, drive, drive_dict):
        groupbox = QGroupBox()
        groupbox.setTitle(item)
        groupbox.setObjectName(item)
        group_box_gird = QGridLayout(groupbox)
        row_index = 0
        for key in drive_dict:
            if isinstance(drive_dict[key], dict):
                group = self.setup_group_box(key,
                                             eval('drive.{}'.format(key)),
                                             drive_dict[key])
                group_box_gird.addWidget(group, row_index, 0, 1, 1)
                row_index += 1
            else:
                item_layout = self.add_single_layout_line(key, drive)
                group_box_gird.addLayout(item_layout, row_index, 0, 1, 1)
                row_index += 1
        return groupbox

    def clear_QTree_widget(self, tree):
        iterator = QTreeWidgetItemIterator(tree, QTreeWidgetItemIterator.All)
        while iterator.value():
            iterator.value().takeChildren()
            iterator += 1
        i = tree.topLevelItemCount()
        while i > -1:
            tree.takeTopLevelItem(i)
            i -= 1


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    main_window = ODriveConfig()
    main_window.show()
    sys.exit(app.exec())
