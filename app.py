import sys
from PySide6.QtWidgets import QApplication, QWidget, QStackedWidget, QVBoxLayout, QToolBar, QMainWindow, QMessageBox
from PySide6.QtWidgets import QDialog
from PySide6.QtCore import QStandardPaths
from PySide6.QtGui import QAction
from ui import GroupsPage, UploadPage, OptionsPage, ConfigDialog, DistributionPage
from pathlib import Path
from logic.group_manager import GroupManager
import pickle
from models.config import Config

app_data_dir = Path(
    QStandardPaths.writableLocation(QStandardPaths.AppDataLocation)
)
app_data_dir.mkdir(parents=True, exist_ok=True)

save_file = app_data_dir / ".state.pkl"


class MainApp(QMainWindow):
    def __init__(self, manager):
        super().__init__()
        self.manager = manager
        #self.config = config
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

        # config_action = QAction("Config", self)
        # config_action.triggered.connect(self.configuration)
        # toolbar.addAction(config_action)

        #self.page_upload = UploadPage(self.switch_page, self.manager, self.statusBar(), self.config)
        self.page_upload = UploadPage(self.switch_page, self.manager, self.statusBar(), None)
        self.page_groups = GroupsPage(self.switch_page, self.manager)
        self.page_options = OptionsPage(self.switch_page, self.manager)
        self.page_distribution = DistributionPage(self.switch_page, self.manager)


        self.stack.addWidget(self.page_upload)
        self.stack.addWidget(self.page_groups)
        self.stack.addWidget(self.page_options)
        self.stack.addWidget(self.page_distribution)


        layout.addWidget(self.stack)
        
        central.setLayout(layout)
        self.setCentralWidget(central)


        if self.manager.groups:
            self.stack.setCurrentIndex(1)

                ##Debugging:
        #self.stack.setCurrentIndex(3)

    def switch_page(self, index):
        self.stack.setCurrentIndex(index)

    def save_state(self):
        try:
            with open(save_file, "wb") as f:
                pickle.dump(self.manager, f)
                #pickle.dump(self.config, f)
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

    def configuration(self):
        dialog = ConfigDialog(self.config, self)
        if dialog.exec() == QDialog.Accepted:
            self.config = dialog.config
            #self.save_state()


manager = None
#config = None

try:
    with open(save_file, "rb") as f:
        manager = pickle.load(f)
        #config = config.load(f)# I dont like this, prob should be using yamls after all

except FileNotFoundError:
    # No saved state → start fresh
    manager = GroupManager()
    #config = Config()

app = QApplication([])
window = MainApp(manager)

window.show()
app.exec()