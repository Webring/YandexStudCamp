from PyQt5.QtWidgets import QMainWindow


class MainWindowWithKeys(QMainWindow):
    def __init__(self):
        super().__init__()
        self.pressed_keys = set()  # Множество для хранения нажатых клавиш

    def keyPressEvent(self, event):
        # Добавляем нажатую клавишу в множество
        self.pressed_keys.add(event.nativeScanCode())
        self.onKeyChange()

    def keyReleaseEvent(self, event):
        # Удаляем отпущенную клавишу из множества
        self.pressed_keys.discard(event.nativeScanCode())
        self.onKeyChange()

    def onKeyChange(self):
        pass
