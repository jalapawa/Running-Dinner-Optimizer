from PySide6.QtWidgets import QDialog, QFormLayout, QLineEdit,QDialogButtonBox, QCheckBox, QSpinBox
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
            if isinstance(value, bool):
                widget = QCheckBox()
                widget.setChecked(value)

            elif isinstance(value, int):
                widget = QSpinBox()
                widget.setRange(0, 100000)
                widget.setValue(value)

            else:
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
        for att, widget in self.fields.items():
            if isinstance(widget, QCheckBox):
                self.config[att] = widget.isChecked()

            elif isinstance(widget, QSpinBox):
                self.config[att] = widget.value()

            else:
                self.config[att] = widget.text()