from PySide6.QtWidgets import QDialog, QFormLayout, QLineEdit, QDialogButtonBox
import copy

class ConfigDialog(QDialog):
    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configuration")

        # copy so Cancel does nothing
        self.config = copy.copy(config)

        self.city = QLineEdit()
        self.city.setText(self.config.city)

        layout = QFormLayout(self)
        layout.addRow("City", self.city)

        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

    def accept(self):
        self.config.city = self.city.text()
        super().accept()