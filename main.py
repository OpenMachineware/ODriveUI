import sys

from PySide6.QtCore import *
from PySide6.QtWidgets import *

from widgets.splash import Splash


def main_widget():
    QCoreApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    app = QApplication(sys.argv)
    main_window = Splash()
    main_window.show()
    sys.exit(app.exec())


def main():
    main_widget()


if __name__ == '__main__':
    main()
