from abc import ABC

from fbs_runtime.application_context import cached_property
from fbs_runtime.application_context.PySide6 import ApplicationContext
from PySide6.QtCore import *
from PySide6.QtWidgets import *

import sys
# TODO: Make init a thread to be called in splash screen.
from utils.config import load_conf
from widgets.splash import Splash


def init():
    conf = load_conf()
    return conf


class MyAppContext(ApplicationContext):
    @cached_property
    def app(self):
        return MyCustomApp(sys.argv)


class MyCustomApp(QApplication):
    pass


def main_widget(conf):
    QCoreApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    appctxt = MyAppContext()  # 1. Instantiate ApplicationContext
    main_window = Splash(conf)
    main_window.show()
    exit_code = appctxt.app.exec()  # 2. Invoke appctxt.app.exec()
    sys.exit(exit_code)


def main():
    conf = init()
    main_widget(conf)


if __name__ == '__main__':
    main()
