from datetime import datetime
from pathlib import Path

from PySide6.QtWidgets import QFileDialog, QMessageBox, QWidget, QHBoxLayout, QListWidget, QListWidgetItem, QLabel, QVBoxLayout, QPushButton, QSlider, QProgressBar
from PySide6.QtCore import Qt, QObject, QThread, Signal
from PySide6.QtGui import QFontMetrics

from logic.export import export


# Subclass QListWidget to update DataManager when items are dropped

class DistributionPage(QWidget):
    def __init__(self, switch_page, data_manager, config):
        super().__init__()
        self.switch_page = switch_page
        self.manager = data_manager
        self.config = config
        layout = QVBoxLayout()

        self.layout_starter = QHBoxLayout()
        

        #Starter
        legend_starter = QVBoxLayout()

        host_label = QLabel("Host")
        host_label.setStyleSheet("""
            color: yellow;
            font-weight: bold;
            font-size: 14px;
        """)
        legend_starter.addWidget(host_label)
        legend_starter.addWidget(QLabel("Guest1"))
        legend_starter.addWidget(QLabel("Guest2"))



        self.layout_starter.addLayout(legend_starter)

        self.layout_main = QHBoxLayout()

        legend_main = QVBoxLayout()

        host_label_main = QLabel("Host")
        host_label_main.setStyleSheet("""
            color: yellow;
            font-weight: bold;
            font-size: 14px;
        """)
        legend_main.addWidget(host_label_main)
        legend_main.addWidget(QLabel("Guest1"))
        legend_main.addWidget(QLabel("Guest2"))

        self.layout_main.addLayout(legend_main)

        self.layout_dessert = QHBoxLayout()

        legend_dessert = QVBoxLayout()

        host_label_dessert = QLabel("Host")
        host_label_dessert.setStyleSheet("""
            color: yellow;
            font-weight: bold;
            font-size: 14px;
        """)
        legend_dessert.addWidget(host_label_dessert)
        legend_dessert.addWidget(QLabel("Guest1"))
        legend_dessert.addWidget(QLabel("Guest2"))

        buttons = QHBoxLayout()
        export_btn = QPushButton("Export to Excel")
        export_btn.clicked.connect(self.export_distribution)
        buttons.addWidget(export_btn)

        self.layout_dessert.addLayout(legend_dessert)

        self.all_lists = None

        labels = []
        for label in ["Starter", "Main", "Dessert"]:
            temp = QHBoxLayout()
            temp.addStretch()
            temp.addWidget(QLabel(f"{label}"))
            temp.addStretch()
            labels.append(temp)
        layout.addLayout(labels[0])
        layout.addLayout(self.layout_starter)
        layout.addLayout(labels[1])
        layout.addLayout(self.layout_main)
        layout.addLayout(labels[2])
        layout.addLayout(self.layout_dessert)

        layout.addLayout(buttons)
        

        self.setLayout(layout)

    def export_distribution(self):
        filename = f"Rudischwimmt Einteilung-{datetime.now():%Y-%m-%d_%H-%M-%S}.xlsx"
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save distribution",
            str(Path.home() / filename),
            "Excel files (*.xlsx)",
        )

        if not file_path:
            return

        path = Path(file_path)
        if path.suffix.lower() != ".xlsx":
            path = path.with_suffix(".xlsx")

        try:
            export(self.manager, self.config, path)
        except Exception as error:
            QMessageBox.critical(self, "Export failed", f"Could not save the distribution:\n{error}")

    def showEvent(self, event):
        super().showEvent(event)
        self.update()  # called automatically when page is shown

    def adaptWidgets(self):
        groups_starter = QHBoxLayout()
        grouplen = len(self.manager.get_groups())
        starter_list = []
        for i in range(grouplen//3):
            widget = QListWidget()
            widget.setUniformItemSizes(True)
            widget.setSpacing(4)
            widget.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)

            widget.setStyleSheet("""
                QScrollBar:horizontal {
                    height: 0px;
                }
            """)
            fm = QFontMetrics(widget.font())
            row_height = 25 
            frame = widget.frameWidth() * 2

            widget.setFixedHeight(row_height * 3 + frame)
            starter_list.append(widget)
            groups_starter.addWidget(widget)
        self.layout_starter.addLayout(groups_starter)

        main_list = []
        groups_main = QHBoxLayout()
        for _ in range(grouplen//3):
            widget = QListWidget()
            widget.setUniformItemSizes(True)
            widget.setSpacing(4)
            widget.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)

            widget.setStyleSheet("""
                QScrollBar:horizontal {
                    height: 0px;
                }
            """)
            fm = QFontMetrics(widget.font())
            row_height = 25 
            frame = widget.frameWidth() * 2

            widget.setFixedHeight(row_height * 3 + frame)
            main_list.append(widget)
            groups_main.addWidget(widget)

        self.layout_main.addLayout(groups_main)
        groups_dessert = QHBoxLayout()
        dessert_list = []
        for _ in range(grouplen//3):
            widget = QListWidget()
            widget.setUniformItemSizes(True)
            widget.setSpacing(4)
            widget.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            widget.setStyleSheet("""
                QScrollBar:horizontal {
                    height: 0px;
                }
            """)
            fm = QFontMetrics(widget.font())
            row_height = 25 
            frame = widget.frameWidth() * 2

            widget.setFixedHeight(row_height * 3 + frame)
            dessert_list.append(widget)
            groups_dessert.addWidget(widget)
        self.layout_dessert.addLayout(groups_dessert)
        self.all_lists = [starter_list, main_list, dessert_list]

    def update(self):
        self.adaptWidgets()
        self.fillDistributions()

    def fillDistributions(self):
        optimum = self.manager.get_optimum()
        groups = len(self.manager.get_groups())
        for host, (guest1, guest2) in optimum.items():
            listnum = (host - 1) // (groups // 3)
            currList = self.all_lists[listnum][(host - 1) % (groups // 3)]
            mappings = self.manager.get_map()
            hostItem = QListWidgetItem(str(mappings[host]))
            guest1Item = QListWidgetItem(str(mappings[guest1]))  
            guest2Item = QListWidgetItem(str(mappings[guest2]))
            currList.addItem(hostItem)  
            currList.addItem(guest1Item)  
            currList.addItem(guest2Item)
