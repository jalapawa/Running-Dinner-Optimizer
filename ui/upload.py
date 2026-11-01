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

        self._thread = None
        self._worker = None

        self.setWindowTitle("Rudi schwimmt randomizer")

        button = qt.QPushButton("Upload")
        button.clicked.connect(self.on_click)

        layout = qt.QVBoxLayout()
        layout.addWidget(button)

        self.setLayout(layout)



    def on_click(self):
        if self._thread is not None:
            return
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
        self._thread = QThread()
        self._worker = BackgroundTask(self.manager, self.config)

        self._worker.moveToThread(self._thread)

        self._thread.started.connect(self._worker.run)

        self._worker.finished.connect(self._thread.quit)
        self._thread.finished.connect(self._cleanup_geocode_thread)
        self._worker.status_message.connect(self.statusBar.showMessage)

        self._thread.start()

    def _cleanup_geocode_thread(self):
        self._thread.wait()
        self._thread = None
        self._worker = None


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
