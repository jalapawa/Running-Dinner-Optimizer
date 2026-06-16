import sys
from PySide6.QtWidgets import QApplication, QWidget, QStackedWidget, QVBoxLayout, QToolBar, QMainWindow, QMessageBox
from PySide6.QtWidgets import QDialog, QFileDialog
from PySide6.QtGui import QAction
from ui import GroupsPage, UploadPage, OptionsPage, ConfigDialog, DistributionPage
from pathlib import Path
from logic.group_manager import GroupManager
import json
from datetime import datetime
import sys

timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
save_file = f"state-{timestamp}"

class MainApp(QMainWindow):
    def __init__(self, manager):
        super().__init__()
        self.manager = manager
        #self.config = config
        self.setWindowTitle("Rudi schwimmt randomizer")
        self.stack = QStackedWidget()

        central = QWidget()
        self.layout = QVBoxLayout(central)

         # Toolbar
        toolbar = QToolBar("Main Toolbar")
        self.addToolBar(toolbar)

        new_action = QAction("Neu", self)
        new_action.triggered.connect(self.new)
        toolbar.addAction(new_action)

        save_action = QAction("Speichern", self)
        save_action.triggered.connect(self.save_state)
        toolbar.addAction(save_action)

        load_action = QAction("Laden", self)
        load_action.triggered.connect(self.load_state)
        toolbar.addAction(load_action)
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


        self.layout.addWidget(self.stack)
        
        central.setLayout(self.layout)
        self.setCentralWidget(central)


        if self.manager.groups:
            self.stack.setCurrentIndex(1)

                ##Debugging:
        #self.stack.setCurrentIndex(3)

    def switch_page(self, index):
        self.stack.setCurrentIndex(index)

    def save_state(self):
        
        try:
            with open(f"data/{save_file}.json", "w") as f:
                json.dump(self.manager.to_dict(), f, indent=4)
            with open(f"data/.last.json", "w") as f:
                json.dump(self.manager.to_dict(), f, indent=4)
        except Exception as e:
            # Show a popup with the error
            QMessageBox.critical(
                self,
                "Save Error",
                f"Failed to save project:\n{e}"
            )
        else:
            # Success: optional popup or status bar
            self.statusBar().showMessage(f"Saved successfully in data/{save_file}", 2000)

    
    def new(self):
        Path("data/.last.json").unlink(missing_ok=True)
        self.manager = GroupManager()
        self.rebuild_stack()


    def rebuild_stack(self):
        oldstack = self.stack
        self.stack = QStackedWidget()
        self.page_upload = UploadPage(self.switch_page, self.manager, self.statusBar(), None)
        self.page_groups = GroupsPage(self.switch_page, self.manager)
        self.page_options = OptionsPage(self.switch_page, self.manager)
        self.page_distribution = DistributionPage(self.switch_page, self.manager)

        self.stack.addWidget(self.page_upload)
        self.stack.addWidget(self.page_groups)
        self.stack.addWidget(self.page_options)
        self.stack.addWidget(self.page_distribution)
        self.stack.setCurrentIndex(0)
        self.layout.replaceWidget(oldstack, self.stack)
        oldstack.deleteLater()

    def load_state(self):
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Load State",
            "",
            "JSON Files (*.json)"
        )

        if not filename:
            return

        with open(filename, "r") as f:
            data = json.load(f)

        self.manager.from_dict(data)
        self.stack.setCurrentIndex(1)

    def configuration(self):
        dialog = ConfigDialog(self.config, self)
        if dialog.exec() == QDialog.Accepted:
            self.config = dialog.config
            #self.save_state()


manager = None
#config = None

try:
    with open("data/.last.json", "r") as f:
        manager = GroupManager()
        manager.from_dict(json.load(f))
        #config = config.load(f)# I dont like this, prob should be using yamls after all

except FileNotFoundError:
    manager = GroupManager()
    #print(manager)
    #config = Config()

app = QApplication([])
window = MainApp(manager)

window.show()
app.exec()