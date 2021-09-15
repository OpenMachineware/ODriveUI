from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

from utils.connection_thread import ODriveConnector
from utils.init import InitThread
from widgets.control import Dashboard
from widgets.select_drive import SelectDrive


class Splash(QWidget):
    def __init__(self, parent=None):
        super(Splash, self).__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint)

        self.conf = None
        self.main_window = None
        self.select_dialog = None
        self.drive_list = None
        self.drive = None
        self.drive_index = 0
        self.init_worker = None
        self.odrive_worker = None

        main_v_box = QVBoxLayout()
        self.label_logo = QLabel()
        pix = QPixmap('resources/splash.jpg')
        self.label_logo.setPixmap(pix)
        self.label_logo.setScaledContents(True)
        info_h_box = QHBoxLayout()
        self.info = QLabel()
        self.progress_bar = QProgressBar()
        info_h_box.addWidget(self.info)
        info_h_box.addWidget(self.progress_bar)
        main_v_box.addWidget(self.label_logo)
        main_v_box.addLayout(info_h_box)
        self.setLayout(main_v_box)

        self.init()

    def init(self):
        self.init_worker = InitThread()
        self.init_worker.sig_conf.connect(self.progress_set)
        self.init_worker.start()

    def progress_set(self, conf, msg, num):
        self.conf = conf
        self.info.setText(msg)
        self.progress_bar.setValue(num)
        if num == 100:
            self.run_main_process()

    def run_main_process(self):
        self.odrive_worker = ODriveConnector()
        self.odrive_worker.sig_odrive_connected.connect(
            self.odrive_connected)
        self.odrive_worker.start()

    def odrive_connected(self, drive_list):
        self.close()

        self.drive_list = drive_list
        if len(drive_list) == 0:
            QMessageBox.information(self, 'Info', 'Can not find drive, '
                                                  'we will enter offline mode.',
                                    QMessageBox.Ok, QMessageBox.Ok)
            self.drive = None
            self.drive_index = None
            self.launch_control()
        elif len(drive_list) > 1:
            self.select_dialog = SelectDrive(drive_list)
            self.select_dialog.sig_odrive_select.connect(self.select_drive)
            self.select_dialog.show()
        else:
            self.drive = drive_list[0]
            self.drive_index = 0
            self.launch_control()

    def select_drive(self, i):
        self.drive = self.drive_list[i]
        self.drive_index = i
        self.launch_control()

    def launch_control(self):
        self.main_window = Dashboard(self.conf, self.drive, self.drive_index)
        self.main_window.show()


if __name__ == '__main__':
    import sys

    QCoreApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    app = QApplication(sys.argv)
    main_window = Splash()
    main_window.show()
    sys.exit(app.exec())
