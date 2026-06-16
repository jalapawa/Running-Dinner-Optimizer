from PySide6.QtWidgets import QWidget, QHBoxLayout, QListWidget, QListWidgetItem, QLabel, QVBoxLayout, QPushButton, QSlider, QProgressBar, QDialog, QComboBox, QCheckBox
from PySide6.QtCore import Qt, QObject, QThread, Signal

import logic.options as op

from time import sleep

class ConstraintsDialog(QDialog):
    def __init__(self, groups, mode):
        super().__init__()

        self.mode = mode

        self.groups = groups

        if mode == "besties":
            self.setWindowTitle("Besties")
        elif mode == "haties":
            self.setWindowTitle("Haties")

        layout = QVBoxLayout(self)

        self.checkbox = QCheckBox("Show names instead")
        layout.addWidget(self.checkbox)
        self.checkbox.toggled.connect(self.on_checkbox_toggled)

        layout.addWidget(QLabel("First Team"))
        self.group1 = QComboBox()
        self.group1.addItems([g.teamname for g in groups])
        layout.addWidget(self.group1)

        layout.addWidget(QLabel("Second Team"))
        self.group2 = QComboBox()
        self.group2.addItems([g.teamname for g in groups])
        layout.addWidget(self.group2)

        confirm_btn = QPushButton("Confirm")
        confirm_btn.clicked.connect(self.accept)
        layout.addWidget(confirm_btn)

    def get_selection(self):
        if self.checkbox.isChecked():
            return self.group1.currentText().split("]")[0][1:], self.group2.currentText().split("]")[0][1:]
        else:
            return self.group1.currentText(), self.group2.currentText()
    
    def on_checkbox_toggled(self, checked):
        if checked:
            self.group1.clear()
            self.group1.addItems([f"[{g.teamname}] {g.personA}, {g.personB}" for g in self.groups])
            self.group2.clear()
            self.group2.addItems([f"[{g.teamname}] {g.personA}, {g.personB}" for g in self.groups])
        else:
            self.group1.clear()
            self.group1.addItems([g.teamname for g in self.groups])
            self.group2.clear()
            self.group2.addItems([g.teamname for g in self.groups])


class OptionsPage(QWidget):
    def __init__(self, switch_page, data_manager):
        super().__init__()
        self.switch_page = switch_page
        self.manager = data_manager

        layout = QVBoxLayout()

        layout_tables = QHBoxLayout()
        layout_tables.addStretch()
        layout_tables.addWidget(QLabel("Haties"))
        layout_tables.addStretch()
        layout_tables.addStretch()
        layout_tables.addWidget(QLabel("Besties"))
        layout_tables.addStretch()


        layout_pairings = QHBoxLayout()
        self.haties = QListWidget()
        self.besties = QListWidget()
        layout_pairings.addWidget(self.haties)
        layout_pairings.addWidget(self.besties)

        layout_buttons = QHBoxLayout()
        self.hatiesAdd = QPushButton("+")
        self.hatiesAdd.clicked.connect(lambda: self.addHaties())
        self.hatiesDel = QPushButton("-")
        self.hatiesDel.clicked.connect(lambda: self.delHaties())
        self.bestiesAdd = QPushButton("+")
        self.bestiesAdd.clicked.connect(lambda: self.addBesties())
        self.bestiesDel = QPushButton("-")
        self.bestiesDel.clicked.connect(lambda: self.delBesties())
        self.besties.itemSelectionChanged.connect(lambda: self.item_selected(0))
        self.haties.itemSelectionChanged.connect(lambda: self.item_selected(1))
        self.bestiesDel.setEnabled(False)
        self.hatiesDel.setEnabled(False)

        layout_buttons.addWidget(self.hatiesAdd)
        layout_buttons.addWidget(self.hatiesDel)
        layout_buttons.addWidget(self.bestiesAdd)
        layout_buttons.addWidget(self.bestiesDel)
        #Slider for randomness
        self.slider = BetterSlider(Qt.Horizontal)
        self.slider.setMinimum(0)
        self.slider.setMaximum(5)
        self.slider.setValue(0)
        self.slider.setTickPosition(QSlider.TicksBelow)
        self.slider.setTickInterval(1)
        self.slider.setSingleStep(1)
        self.slider.setStyleSheet("""
                                QSlider::handle:horizontal {
                                    background: #3498db;
                                    width: 20px;
                                    height: 40px;
                                    margin: -10px 0; /* center handle on the groove */
                                    border-radius: 10px;
                                }
                                QSlider::groove:horizontal {
                                    background: #bbb;
                                    height: 10px;
                                    border-radius: 5px;
                                }
                                """)

        labels_layout = QHBoxLayout()
        labels_layout.addWidget(QLabel("0"))
        labels_layout.addStretch()
        labels_layout.addWidget(QLabel("1"))
        labels_layout.addStretch()
        labels_layout.addWidget(QLabel("2"))
        labels_layout.addStretch()
        labels_layout.addWidget(QLabel("3"))
        labels_layout.addStretch()
        labels_layout.addWidget(QLabel("4"))
        labels_layout.addStretch()
        labels_layout.addWidget(QLabel("5"))
        labels_layout_2 = QHBoxLayout()
        labels_layout_2.addWidget(QLabel("Best route optimization"))
        labels_layout_2.addStretch()
        labels_layout_2.addWidget(QLabel("Completely random"))

        self.optimize = QPushButton("Optimize!")
        self.optimize.clicked.connect(lambda: self.calc())
        h = self.optimize.sizeHint().height()
        self.optimize.setFixedHeight(h * 2)
        self.optimize.setStyleSheet("""
            color: yellow;
            font-weight: bold;
            font-size: 14px;
        """)

        self.back_btn = QPushButton("Zurück")
        self.back_btn.clicked.connect(lambda: self.switch_page(1))
    
        self.progress = QProgressBar()
        self.progress.setRange(0, 0)  # infinite animation
        self.progress.hide()

        self.result = QLabel("")
        self.result.hide()

        layout.addLayout(layout_tables)
        layout.addLayout(layout_pairings)
        layout.addLayout(layout_buttons)
        layout.addWidget(self.slider)
        layout.addLayout(labels_layout)
        layout.addLayout(labels_layout_2)
        layout.addWidget(self.optimize)
        layout.addWidget(self.back_btn)
        layout.addWidget(self.progress)
        layout.addWidget(self.result)



        self.setLayout(layout)

        self.updateBesties()
        self.updateHaties()


    def calc(self):
        self.result.setVisible(False)
        self.progress.setVisible(True)
        self.optimize.setEnabled(False)
        self.run_optimizer(self.manager.get_groups(), self.manager.get_map(), self.slider.value(), self.manager.get_besties(), self.manager.get_haties())

    def addBesties(self):
        dialog = ConstraintsDialog(self.manager.get_groups(), "besties")

        if dialog.exec():
            group_a, group_b = dialog.get_selection()

            self.manager.add_besties(group_a, group_b)

        self.updateBesties()

    def updateBesties(self):
        self.besties.clear()
        for teamA, teamB in self.manager.get_besties():
            self.besties.addItem(QListWidgetItem(f"{teamA.teamname} : {teamB.teamname}"))

    def updateHaties(self):
        self.haties.clear()
        for teamA, teamB in self.manager.get_haties():
            self.haties.addItem(QListWidgetItem(f"{teamA.teamname} : {teamB.teamname}"))

    def addHaties(self):
        dialog = ConstraintsDialog(self.manager.get_groups(), "haties")

        if dialog.exec():
            group_a, group_b = dialog.get_selection()

            self.manager.add_haties(group_a, group_b)
        
        self.updateHaties()

    def delBesties(self):
        selected_item = self.besties.currentItem()
        self.manager.del_besties(selected_item.text())

        self.updateBesties()


    def delHaties(self):
        selected_item = self.haties.currentItem()
        self.manager.del_haties(selected_item.text())

        self.updateHaties()



    def item_selected(self, category):
        match category:
            case 0:
                selected_item = self.besties.currentItem()
                if selected_item:
                    self.hatiesDel.setEnabled(False)
                    self.bestiesDel.setEnabled(True)
                
                    self.haties.blockSignals(True)
                    self.haties.clearSelection()
                    self.haties.blockSignals(False)
            case 1:
                selected_item = self.haties.currentItem()
                if selected_item:
                    self.bestiesDel.setEnabled(False)
                    self.hatiesDel.setEnabled(True)
                
                    self.besties.blockSignals(True)
                    self.besties.clearSelection()
                    self.besties.blockSignals(False)
        
    def on_optimizer_finished(self, result):
        self.progress.setVisible(False)
        print("Optimizer finish received")
        self.result.setText(f"Solver success!")
        self.result.setStyleSheet("color: green;")
        self.result.setVisible(True)
        self.optimize.setVisible(False)
        self.manager.set_optimum(result)
        print("Switching page now")
        self.switch_page(3)

    def on_optimizer_error(self, msg):
        self.progress.setVisible(False)
        self.result.setText(f"Solver error: {msg}!")
        self.result.setStyleSheet("color: red;")
        self.result.setVisible(True)
        self.optimize.setVisible(True)
        self.optimize.setEnabled(True)


    def run_optimizer(self, groups, map, level, besties, haties):
        self.thread = QThread()
        self.worker = OptimizerWorker(groups, map, level, besties, haties)

        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.on_optimizer_finished)
        self.worker.error.connect(self.on_optimizer_error)
        self.worker.error.connect(self.thread.quit)
        self.worker.error.connect(self.worker.deleteLater)

        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        self.thread.start()

class OptimizerWorker(QObject):
    finished = Signal(object)
    error = Signal(str)

    def __init__(self, groups, map, level, besties, haties):
        super().__init__()
        self.groups = groups
        self.mapping = map
        self.level = level
        self.besties = besties
        self.haties = haties

    def run(self):
        try:
            result = op.calculate_optimum(self.groups, self.mapping, self.level, self.besties, self.haties)
            print("After optimization res")
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))

#Changed up slider cuz clicking on it was not working properly
class BetterSlider(QSlider):
    def mousePressEvent(self, event):
        click_pos = event.position().x()
        slider_length = self.width()

        ratio = click_pos / slider_length
        value_range = self.maximum() - self.minimum()
        raw_value = self.minimum() + ratio * value_range

        val = round(raw_value)

        self.setValue(val)