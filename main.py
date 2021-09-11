import sys

from PySide6.QtCore import *
from PySide6.QtWidgets import *

from utils.config import load_conf
from widgets.splash import Splash


# TODO: Make init a thread to be called in splash screen.
def init():
    conf = load_conf()
    return conf


def main_widget(conf):
    QCoreApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    app = QApplication(sys.argv)
    main_window = Splash(conf)
    main_window.show()
    sys.exit(app.exec())


def main():
    conf = init()
    main_widget(conf)


if __name__ == '__main__':
    main()
