from PySide6.QtWidgets import QWidget, QHBoxLayout, QListWidget, QListWidgetItem, QLabel, QVBoxLayout, QPushButton
from PySide6.QtCore import Qt

class GroupsPage(QWidget):
    def __init__(self, switch_page, data_manager, config):
        super().__init__()
        self.switch_page = switch_page
        self.manager = data_manager
        self.config = config

        self.current_selection = None

        layout = QVBoxLayout()
        #Labels
        labels_layout = QHBoxLayout()
        self.label1 = QLabel(f"Vorspeise")
        self.label2 = QLabel(f"Hauptspeise")
        self.label3 = QLabel(f"Nachspeise")
        self.label4 = QLabel(f"Egal")
        labels_layout.addWidget(self.label1)
        labels_layout.addWidget(self.label2)
        labels_layout.addWidget(self.label3)
        labels_layout.addWidget(self.label4)
        layout.addLayout(labels_layout)

        # Horizontal layout for the 3 category boxes
        category_layout = QHBoxLayout()
        self.list1 = QListWidget()
        self.list2 = QListWidget()
        self.list3 = QListWidget()
        self.list4 = QListWidget()

        self.list1.itemSelectionChanged.connect(lambda: self.item_selected(0))
        self.list2.itemSelectionChanged.connect(lambda: self.item_selected(1))
        self.list3.itemSelectionChanged.connect(lambda: self.item_selected(2))
        self.list4.itemSelectionChanged.connect(lambda: self.item_selected(3))

        for lst in [self.list1, self.list2, self.list3, self.list4]:
            lst.setSelectionMode(QListWidget.SingleSelection)

        category_layout.addWidget(self.list1)
        category_layout.addWidget(self.list2)
        category_layout.addWidget(self.list3)
        category_layout.addWidget(self.list4)

        layout.addLayout(category_layout)

        #Switch dish buttons
        changes_layout = QHBoxLayout()
        self.switch1_btn = QPushButton("Wechsel zu Vorspeise")
        self.switch1_btn.setEnabled(False)
        self.switch1_btn.clicked.connect(lambda: self.switch_dish(0))
        self.switch2_btn = QPushButton("Wechsel zu Hauptspeise")
        self.switch2_btn.setEnabled(False)
        self.switch2_btn.clicked.connect(lambda: self.switch_dish(1))
        self.switch3_btn = QPushButton("Wechsel zu Nachspeise")
        self.switch3_btn.setEnabled(False)
        self.switch3_btn.clicked.connect(lambda: self.switch_dish(2))
        changes_layout.addWidget(self.switch1_btn)
        changes_layout.addWidget(self.switch2_btn)
        changes_layout.addWidget(self.switch3_btn)
        layout.addLayout(changes_layout)

        #Add Delete Buttons
        add_layout = QHBoxLayout()
        self.add_btn = QPushButton("Manuell hinzufügen")
        #self.add_btn.clicked.connect(lambda: self.add())
        self.delete_btn = QPushButton("Entfernen")
        self.delete_btn.clicked.connect(lambda: self.delete())
        self.distribute_btn = QPushButton("Egal aufteilen")
        self.distribute_btn.clicked.connect(lambda: self.distribute())
        add_layout.addWidget(self.add_btn)
        add_layout.addWidget(self.delete_btn)
        add_layout.addWidget(self.distribute_btn)
        layout.addLayout(add_layout)
        # Navigation buttons
        back_btn = QPushButton("Zurück")
        back_btn.clicked.connect(lambda: self.switch_page(0))
        self.next_btn = QPushButton("Weiter")
        self.next_btn.clicked.connect(lambda: self.next())  # go to page 3
        self.next_btn.setToolTip("All categories must be equalized before going forward with the optimization")

        nav_layout = QHBoxLayout()
        nav_layout.addWidget(back_btn)
        nav_layout.addWidget(self.next_btn)
        layout.addLayout(nav_layout)

        self.setLayout(layout)

    def next(self):
        self.manager.assign_ids()
        self.switch_page(2)

    def update(self):
        # Populate list1 with all rows initially
        self.list1.clear()
        self.list2.clear()
        self.list3.clear()
        self.list4.clear()
        keys = self.manager.get_keys()
        totalStarter = 0
        totalMain = 0
        totalDessert = 0
        totalFree = 0
        for row in self.manager.get_groups():
            item = QListWidgetItem(row.teamname)  # display name
            item.setData(Qt.UserRole, row)  # store dataclass
            tooltip = ""
            for index, (key, value) in enumerate(row.to_dict().items()):
                if index > 10:
                    break
                name = keys[index]
                if len(name) > 20:
                    name = name[:20] + "..."
                tooltip += f"{name} : {value} \n"
            item.setToolTip(tooltip)
            match row.dish:
                case "Vorspeise":
                    self.list1.addItem(item)
                    totalStarter += 1
                case "Hauptspeise":
                    self.list2.addItem(item)
                    totalMain += 1
                case "Nachspeise":
                    self.list3.addItem(item)
                    totalDessert += 1
                case "Egal":
                    self.list4.addItem(item)
                    totalFree += 1
        self.label1.setText(f"Vorspeise ({totalStarter})")
        self.label2.setText(f"Hauptspeise ({totalMain})")
        self.label3.setText(f"Nachspeise ({totalDessert})")
        self.label4.setText(f"Egal ({totalFree})")
        self.next_btn.setEnabled(totalStarter == totalMain and totalMain == totalDessert and totalFree == 0)

    def showEvent(self, event):
        super().showEvent(event)
        self.update()  # called automatically when page is shown

    def distribute(self):
        self.manager.distribute()
        self.update()

    def item_selected(self, category):
        match category:
            case 0:
                selected_item = self.list1.currentItem()
                if selected_item:
                    self.current_selection = selected_item.data(Qt.UserRole)
                    self.switch1_btn.setEnabled(False)
                    self.switch2_btn.setEnabled(True)
                    self.switch3_btn.setEnabled(True)
                for other_lst in [self.list2, self.list3, self.list4]:
                    other_lst.blockSignals(True)
                    other_lst.clearSelection()
                    other_lst.blockSignals(False)
            case 1:
                selected_item = self.list2.currentItem()
                if selected_item:
                    self.current_selection = selected_item.data(Qt.UserRole)
                    self.switch1_btn.setEnabled(True)
                    self.switch2_btn.setEnabled(False)
                    self.switch3_btn.setEnabled(True)
                for other_lst in [self.list1, self.list3, self.list4]:
                    other_lst.blockSignals(True)
                    other_lst.clearSelection()
                    other_lst.blockSignals(False)
            case 2:
                selected_item = self.list3.currentItem()
                if selected_item:
                    self.current_selection = selected_item.data(Qt.UserRole)
                    self.switch1_btn.setEnabled(True)
                    self.switch2_btn.setEnabled(True)
                    self.switch3_btn.setEnabled(False)
                for other_lst in [self.list1, self.list2, self.list4]:
                    other_lst.blockSignals(True)
                    other_lst.clearSelection()
                    other_lst.blockSignals(False)
            case 3:
                selected_item = self.list4.currentItem()
                if selected_item:
                    self.current_selection = selected_item.data(Qt.UserRole)
                    self.switch1_btn.setEnabled(True)
                    self.switch2_btn.setEnabled(True)
                    self.switch3_btn.setEnabled(True)
                for other_lst in [self.list1, self.list2, self.list3]:
                    other_lst.blockSignals(True)
                    other_lst.clearSelection()
                    other_lst.blockSignals(False)
            case _:
                pass
    def switch_dish(self, category):
        match category:
            case 0:
                self.manager.change_dish(self.current_selection.teamname, "Vorspeise")
            case 1:
                self.manager.change_dish(self.current_selection.teamname, "Hauptspeise")
            case 2:
                self.manager.change_dish(self.current_selection.teamname, "Nachspeise")
            case _:
                pass
        self.update()

    def delete(self):
        if self.list1.currentItem() or self.list2.currentItem() or self.list3.currentItem() or self.list4.currentItem():
            self.manager.delete_group(self.current_selection.teamname)
            self.update()