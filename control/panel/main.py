import sys
import traceback

from PyQt5.QtWidgets import (
    QApplication
)

from control.panel.mainwindow import ClientWindow


def excepthook(type, value, tb):
    traceback.print_exception(type, value, tb)
    sys.exit(1)


sys.excepthook = excepthook

if __name__ == '__main__':
    app = QApplication(sys.argv)
    client_widget = ClientWindow()
    client_widget.show()
    sys.exit(app.exec_())
