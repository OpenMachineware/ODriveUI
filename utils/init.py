from PySide6.QtCore import *

from utils.config import load_conf


class InitThread(QThread):
    sig_conf = Signal(object, str, int)

    def __init__(self):
        super().__init__()

    def run(self):
        ret, conf = load_conf()
        if ret != 0 :
            conf_msg = 'Config load failed'
            step = 1
        else:
            conf_msg = 'Config loaded'
            step =  100
        self.sig_conf.emit(conf, conf_msg, step)
