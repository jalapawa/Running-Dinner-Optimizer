from PySide6.QtWidgets import QWidget, QHBoxLayout, QListWidget, QListWidgetItem, QLabel, QVBoxLayout, QPushButton, QSlider, QProgressBar
from PySide6.QtCore import Qt, QObject, QThread, Signal
from PySide6.QtGui import QFontMetrics

from logic.export import export


# Subclass QListWidget to update DataManager when items are dropped

class DistributionPage(QWidget):
    def __init__(self, switch_page, data_manager):
        super().__init__()
        self.switch_page = switch_page
        self.manager = data_manager
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
        export_btn = QPushButton("Export to csv")
        export_btn.clicked.connect(lambda: export(self.manager))  # go to page 3
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

    def showEvent(self, event):
        print("Arrived at page")
        super().showEvent(event)
        self.update()  # called automatically when page is shown
        print("Page updated!")

    def adaptWidgets(self):
        groups_starter = QHBoxLayout()
        grouplen = len(self.manager.get_groups())
        starter_list = []
        for _ in range(grouplen//3):
            list = QListWidget()
            list.setUniformItemSizes(True)
            list.setSpacing(4)
            list.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)

            list.setStyleSheet("""
                QScrollBar:horizontal {
                    height: 0px;
                }
            """)
            fm = QFontMetrics(list.font())
            row_height = 25 
            frame = list.frameWidth() * 2

            list.setFixedHeight(row_height * 3 + frame)
            starter_list.append(list)
            groups_starter.addWidget(list)
        self.layout_starter.addLayout(groups_starter)

        main_list = []
        groups_main = QHBoxLayout()
        for _ in range(grouplen//3):
            list = QListWidget()
            list.setUniformItemSizes(True)
            list.setSpacing(4)
            list.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)

            list.setStyleSheet("""
                QScrollBar:horizontal {
                    height: 0px;
                }
            """)
            fm = QFontMetrics(list.font())
            row_height = 25 
            frame = list.frameWidth() * 2

            list.setFixedHeight(row_height * 3 + frame)
            main_list.append(list)
            groups_main.addWidget(list)

        self.layout_main.addLayout(groups_main)

        groups_dessert = QHBoxLayout()
        dessert_list = []
        for _ in range(grouplen//3):
            list = QListWidget()
            list.setUniformItemSizes(True)
            list.setSpacing(4)
            list.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            list.setStyleSheet("""
                QScrollBar:horizontal {
                    height: 0px;
                }
            """)
            fm = QFontMetrics(list.font())
            row_height = 25 
            frame = list.frameWidth() * 2

            list.setFixedHeight(row_height * 3 + frame)
            dessert_list.append(list)
            groups_dessert.addWidget(list)
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