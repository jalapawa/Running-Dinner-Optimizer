from PySide6.QtWidgets import QWidget, QHBoxLayout, QListWidget, QListWidgetItem, QLabel, QVBoxLayout, QPushButton
from PySide6.QtCore import Qt

class UploadPage(qt.QWidget):
    def __init__(self, switch_page, manager):
        super().__init__()
        self.manager = manager
        self.switch_page = switch_page

        category_layout = QHBoxLayout()
        self.list1 = CategoryList("Vorspeise", self.manager)
        self.list2 = CategoryList("Hauptspeise", self.manager)
        self.list3 = CategoryList("Nachspeise", self.manager)
        self.list4 = CategoryList("Egal", self.manager)



    def on_click(self):