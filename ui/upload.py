import PySide6.QtWidgets as qt
from logic.csv_handler import handleFile
from logic.options import precalculate_all_coords
from PySide6.QtCore import QObject, QThread, Signal


class UploadPage(qt.QWidget):
    def __init__(self, switch_page, manager, statusBar, config):
        super().__init__()
        self.manager = manager
        self.switch_page = switch_page
        self.statusBar = statusBar
        self.config = config

        self.setWindowTitle("Rudi schwimmt randomizer")

        button = qt.QPushButton("Upload")
        button.clicked.connect(self.on_click)

        layout = qt.QVBoxLayout()
        layout.addWidget(button)

        self.setLayout(layout)



    def on_click(self):
        file_path, _ = qt.QFileDialog.getOpenFileName(
            parent = self,
            caption="Select CSV file",
            dir="",
            filter="CSV Files(*.csv);;All Files(*)"
        )
        if file_path:
            groups, keys = handleFile(file_path)
            self.manager.set_groups(groups)
            self.manager.set_keys(keys)
            self.background_calc()         #Running this in background
            self.switch_page(1)

    def background_calc(self):
        self.thread = QThread()
        self.worker = BackgroundTask(self.manager, self.config)

        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)

        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.worker.status_message.connect(self.statusBar.showMessage)

        self.thread.start()

class BackgroundTask(QObject):
    finished = Signal(object)
    status_message = Signal(str)

    def __init__(self, manager, config):
        super().__init__()
        self.manager = manager
        self.config = config

    def run(self):
        precalculate_all_coords(self.manager, self.status_message, self.config)
        self.finished.emit(None)
