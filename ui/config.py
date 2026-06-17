from PySide6.QtWidgets import QDialog, QFormLayout, QLineEdit, QDialogButtonBox
import copy

class ConfigDialog(QDialog):
    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configuration")

        # copy so Cancel does nothing
        self.config = copy.copy(config)

        layout = QFormLayout(self)
        self.fields = {}

        for att, value in config.items():
            widget = QLineEdit(str(value))
            self.fields[att] = widget
            layout.addRow(att, self.fields[att])

        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

    def accept(self):
        super().accept()
        for att in self.config.keys():
            self.config[att] = self.fields[att].text()