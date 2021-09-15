from PySide6.QtWidgets import *
from PySide6.QtCore import *


class SelectDrive(QDialog):
    sig_odrive_select = Signal(int)

    def __init__(self, drive_list, parent=None):
        super(SelectDrive, self).__init__(parent)
        self.setWindowTitle('Select Drive')
        self.setWindowModality(Qt.ApplicationModal)

        main_h_box = QHBoxLayout()
        self.select = QComboBox()
        num = len(drive_list)
        for i in range(num):
            ietm = 'odrv' + str(i)
            self.select.addItem(ietm)
        self.btn_cancel = QPushButton('Cancel')
        self.btn_cancel.clicked.connect(self.close)
        self.btn_ok = QPushButton('OK')
        self.btn_ok.clicked.connect(self.ok)
        main_h_box.addWidget(self.select)
        main_h_box.addWidget(self.btn_cancel)
        main_h_box.addWidget(self.btn_ok)
        self.setLayout(main_h_box)

    def ok(self):
        i = self.select.currentIndex()
        self.sig_odrive_select.emit(i)


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    main_window = SelectDrive([1, 2, 3])
    main_window.show()
    sys.exit(app.exec())
