import odrive

from PySide6.QtCore import *


class ODriveConnector(QThread):
    sig_odrive_connected = Signal(object)

    def __init__(self):
        QThread.__init__(self)
        self.drives = None
        self._isRunning = True

    def stop(self):
        self._isRunning = False

    def run(self):
        try:
            self.drives = odrive.find_any(timeout=3)
            self.sig_odrive_connected.emit([self.drives])
        except:
            self.sig_odrive_connected.emit([])
