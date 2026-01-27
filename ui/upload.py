import PySide6.QtWidgets as qt
from logic.csv_handler import handleFile
from logic.options import precalculate_all_coords

class UploadPage(qt.QWidget):
    def __init__(self, switch_page, manager):
        super().__init__()
        self.manager = manager
        self.switch_page = switch_page

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
            #precalculate_all_coords(self.manager.get_groups())
            self.switch_page(1)