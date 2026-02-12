from PySide6.QtWidgets import QWidget, QHBoxLayout, QListWidget, QListWidgetItem, QLabel, QVBoxLayout, QPushButton, QSlider, QProgressBar
from PySide6.QtCore import Qt, QObject, QThread, Signal
from PySide6.QtGui import QFontMetrics


# Subclass QListWidget to update DataManager when items are dropped

class DistributionPage(QWidget):
    def __init__(self, switch_page, data_manager):
        super().__init__()
        self.switch_page = switch_page
        self.manager = data_manager
        self.groups = len(self.manager.get_groups())

        layout = QVBoxLayout()

        layout_starter = QHBoxLayout()
        

        #Starter
        legend_starter = QVBoxLayout()
        groups_starter = QHBoxLayout()

        host_label = QLabel("Host")
        host_label.setStyleSheet("""
            color: yellow;
            font-weight: bold;
            font-size: 14px;
        """)
        legend_starter.addWidget(host_label)
        legend_starter.addWidget(QLabel("Guest1"))
        legend_starter.addWidget(QLabel("Guest2"))

        starter_list = []
        for _ in range(self.groups//3):
            list = QListWidget()
            list.setUniformItemSizes(True)
            fm = QFontMetrics(list.font())
            row_height = 25 
            frame = list.frameWidth() * 2

            list.setFixedHeight(row_height * 3 + frame)
            starter_list.append(list)
            groups_starter.addWidget(list)

        layout_starter.addLayout(legend_starter)
        layout_starter.addLayout(groups_starter)

        layout_main = QHBoxLayout()

        legend_main = QVBoxLayout()
        groups_main = QHBoxLayout()

        host_label_main = QLabel("Host")
        host_label_main.setStyleSheet("""
            color: yellow;
            font-weight: bold;
            font-size: 14px;
        """)
        legend_main.addWidget(host_label_main)
        legend_main.addWidget(QLabel("Guest1"))
        legend_main.addWidget(QLabel("Guest2"))

        main_list = []
        for _ in range(self.groups//3):
            list = QListWidget()
            list.setUniformItemSizes(True)
            fm = QFontMetrics(list.font())
            row_height = 25 
            frame = list.frameWidth() * 2

            list.setFixedHeight(row_height * 3 + frame)
            main_list.append(list)
            groups_main.addWidget(list)

        layout_main.addLayout(legend_main)
        layout_main.addLayout(groups_main)

        layout_dessert = QHBoxLayout()

        legend_dessert = QVBoxLayout()
        groups_dessert = QHBoxLayout()

        host_label_dessert = QLabel("Host")
        host_label_dessert.setStyleSheet("""
            color: yellow;
            font-weight: bold;
            font-size: 14px;
        """)
        legend_dessert.addWidget(host_label_dessert)
        legend_dessert.addWidget(QLabel("Guest1"))
        legend_dessert.addWidget(QLabel("Guest2"))

        dessert_list = []
        for _ in range(self.groups//3):
            list = QListWidget()
            list.setUniformItemSizes(True)
            fm = QFontMetrics(list.font())
            row_height = 25 
            frame = list.frameWidth() * 2

            list.setFixedHeight(row_height * 3 + frame)
            dessert_list.append(list)
            groups_dessert.addWidget(list)

        layout_dessert.addLayout(legend_dessert)
        layout_dessert.addLayout(groups_dessert)

        self.all_lists = [starter_list, main_list, dessert_list]

        labels = []
        for label in ["Starter", "Main", "Dessert"]:
            temp = QHBoxLayout()
            temp.addStretch()
            temp.addWidget(QLabel(f"{label}"))
            temp.addStretch()
            labels.append(temp)
        layout.addLayout(labels[0])
        layout.addLayout(layout_starter)
        layout.addLayout(labels[1])
        layout.addLayout(layout_main)
        layout.addLayout(labels[2])
        layout.addLayout(layout_dessert)

        self.setLayout(layout)

    def showEvent(self, event):
        super().showEvent(event)
        self.update()  # called automatically when page is shown

    def update(self):
        self.fillDistributions()

    def fillDistributions(self):
        print("Doing it!")
        optimum = self.manager.get_optimum()
        for host, (guest1, guest2) in optimum.items():
            listnum = (host - 1) // (self.groups // 3)
            currList = self.all_lists[listnum][(host - 1) % (self.groups // 3)]
            print(f"{listnum}, {currList}")
            hostItem = QListWidgetItem(str(host))
            guest1Item = QListWidgetItem(str(guest1))  
            guest2Item = QListWidgetItem(str(guest2))
            currList.addItem(hostItem)  
            currList.addItem(guest1Item)  
            currList.addItem(guest2Item)