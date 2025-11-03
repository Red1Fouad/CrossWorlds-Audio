import sys
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QTreeWidget, QTreeWidgetItem,
                               QDialogButtonBox, QMessageBox)

from data import BGM_DATA

class BGMSelectorWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Common BGM")
        self.resize(500, 600)
        self.result = None

        layout = QVBoxLayout(self)

        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Name", "Filename"])
        self.tree.setColumnWidth(0, 350)
        layout.addWidget(self.tree)

        for category, tracks in BGM_DATA.items():
            category_node = QTreeWidgetItem(self.tree, [category])
            category_node.setExpanded(True)
            for id_num, name in tracks.items():
                filename = ""
                if category == "Menu & System":
                    filename = "BGM.acb"
                elif category == "Voice Lines":
                    # Special case for Miku's unique filename
                    if id_num == "EXTND10_CHARA":
                        filename = "SE_EXTND10_CHARA.acb"
                    else:
                        filename = f"VOICE_{id_num}.acb"
                elif category == "DLC Tracks":
                    filename = f"BGM_{id_num}.acb"
                else:
                    filename = f"BGM_STG{id_num}.acb"
                
                display_text = f"{id_num}: {name}" if category not in ["Menu & System", "Voice Lines"] else name
                QTreeWidgetItem(category_node, [display_text, filename])

        self.tree.itemDoubleClicked.connect(self.on_select)

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.on_accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def on_select(self, item, column):
        if item and item.childCount() == 0: # It's a selectable item, not a category
            self.on_accept()

    def on_accept(self):
        """Handles the logic for when the 'OK' or 'Select' button is clicked."""
        selected_items = self.tree.selectedItems()
        if selected_items and selected_items[0].childCount() == 0:
            self.result = selected_items[0].text(1)
            self.accept()
        else:
            QMessageBox.warning(self, "Selection Error", "Please select a specific track, not a category.")