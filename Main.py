from PySide6.QtWidgets import QApplication
from App import App


class Main:
    def __init__(self):
        self.qt_app = QApplication([])
        self.window = App()

    def run(self):
        self.window.show()
        self.qt_app.exec()

main = Main()
main.run()