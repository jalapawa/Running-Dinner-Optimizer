import sys
from PySide6.QtWidgets import QApplication, QWidget, QStackedWidget, QVBoxLayout, QToolBar, QMainWindow
from PySide6.QtGui import QAction
from ui.groups import GroupsPage
from ui.upload import UploadPage

from logic.group_manager import GroupManager

import pickle


from PySide6.QtCore import QStandardPaths
from pathlib import Path

from PySide6.QtWidgets import QMessageBox

app_data_dir = Path(
    QStandardPaths.writableLocation(QStandardPaths.AppDataLocation)
)
app_data_dir.mkdir(parents=True, exist_ok=True)

save_file = app_data_dir / "state.pkl"


class MainApp(QMainWindow):
    def __init__(self, manager):
        super().__init__()
        self.manager = manager
        self.setWindowTitle("Rudi schwimmt randomizer")
        self.stack = QStackedWidget()

        central = QWidget()
        layout = QVBoxLayout(central)

         # Toolbar
        toolbar = QToolBar("Main Toolbar")
        self.addToolBar(toolbar)

        new_action = QAction("Neu", self)
        new_action.triggered.connect(self.new)
        toolbar.addAction(new_action)

        save_action = QAction("Speichern", self)
        save_action.triggered.connect(self.save_state)
        toolbar.addAction(save_action)

        self.page_upload = UploadPage(self.switch_page, self.manager)
        self.page_preview = GroupsPage(self.switch_page, self.manager)

        self.stack.addWidget(self.page_upload)
        self.stack.addWidget(self.page_preview)

        layout.addWidget(self.stack)
        
        central.setLayout(layout)
        self.setCentralWidget(central)

        if self.manager.groups:
            self.stack.setCurrentIndex(1)

    def switch_page(self, index):
        self.stack.setCurrentIndex(index)

    def save_state(self):
        try:
            with open(save_file, "wb") as f:
                pickle.dump(self.manager, f)
        except Exception as e:
            # Show a popup with the error
            QMessageBox.critical(
                self,
                "Save Error",
                f"Failed to save project:\n{e}"
            )
        else:
            # Success: optional popup or status bar
            self.statusBar().showMessage(f"Saved successfully in {save_file}", 2000)

    
    def new(self):
        with open(save_file, "wb") as f:
            pickle.dump(GroupManager(), f)
            self.manager = GroupManager()
            self.stack.setCurrentIndex(0)


manager = None

try:
    with open(save_file, "rb") as f:
        manager = pickle.load(f)
except FileNotFoundError:
    # No saved state → start fresh
    manager = GroupManager()

app = QApplication([])
window = MainApp(manager)

window.show()
app.exec()