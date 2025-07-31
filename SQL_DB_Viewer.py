import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton,
    QTableView, QMessageBox, QHBoxLayout, QFileDialog, QInputDialog
)
from PyQt6.QtSql import QSqlDatabase, QSqlTableModel
import sqlite3

class DatabaseEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ویرایشگر دیتابیس پدرام")

        self.db = QSqlDatabase.addDatabase("QSQLITE")
        self.model = None
        self.view = QTableView()

        # دکمه‌ها
        btn_choose_db = QPushButton("📁 انتخاب دیتابیس")
        btn_save = QPushButton("💾 ذخیره تغییرات")
        btn_cancel = QPushButton("↩️ لغو تغییرات")
        btn_delete = QPushButton("🗑️ حذف سطر انتخاب شده")
        btn_add = QPushButton("➕ افزودن سطر جدید")

        btn_choose_db.clicked.connect(self.choose_database)
        btn_save.clicked.connect(self.save_changes)
        btn_cancel.clicked.connect(self.cancel_changes)
        btn_delete.clicked.connect(self.delete_row)
        btn_add.clicked.connect(self.add_row)

        # چینش
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(btn_choose_db)
        btn_layout.addStretch()
        btn_layout.addWidget(btn_add)
        btn_layout.addWidget(btn_delete)
        btn_layout.addWidget(btn_cancel)
        btn_layout.addWidget(btn_save)

        layout = QVBoxLayout()
        layout.addWidget(self.view)
        layout.addLayout(btn_layout)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def choose_database(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "انتخاب فایل دیتابیس", "", "SQLite Database (*.db *.sqlite)"
        )
        if not file_path:
            return

        # گرفتن لیست جداول با sqlite3
        try:
            conn = sqlite3.connect(file_path)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            conn.close()
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"خواندن جداول با خطا مواجه شد:\n{str(e)}")
            return

        if not tables:
            QMessageBox.warning(self, "هشدار", "هیچ جدولی در این دیتابیس یافت نشد.")
            return

        table_name, ok = QInputDialog.getItem(
            self, "انتخاب جدول", "لطفاً یک جدول را انتخاب کنید:", tables, 0, False
        )
        if not ok:
            return

        if self.db.isOpen():
            self.db.close()
        self.db.setDatabaseName(file_path)
        if not self.db.open():
            QMessageBox.critical(self, "خطا", f"اتصال به دیتابیس ناموفق بود:\n{self.db.lastError().text()}")
            return

        self.model = QSqlTableModel(self, self.db)
        self.model.setTable(table_name)
        self.model.setEditStrategy(QSqlTableModel.EditStrategy.OnManualSubmit)
        self.model.select()

        self.view.setModel(self.model)
        self.view.resizeColumnsToContents()
        self.view.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self.view.setSelectionMode(QTableView.SelectionMode.SingleSelection)

    def save_changes(self):
        if self.model and self.model.submitAll():
            QMessageBox.information(self, "موفق", "تغییرات ذخیره شدند.")
        else:
            QMessageBox.warning(self, "خطا", "ذخیره تغییرات ناموفق بود.")

    def cancel_changes(self):
        if self.model:
            self.model.revertAll()
            QMessageBox.information(self, "اطلاع", "تغییرات لغو شدند.")

    def delete_row(self):
        if not self.model:
            return
        index = self.view.currentIndex()
        if not index.isValid():
            QMessageBox.warning(self, "خطا", "ابتدا یک سطر را انتخاب کنید.")
            return
        row = index.row()
        confirm = QMessageBox.question(
            self, "تأیید حذف", "آیا مطمئن هستید که این سطر حذف شود؟",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if confirm == QMessageBox.StandardButton.Yes:
            self.model.removeRow(row)

    def add_row(self):
        if self.model:
            row_count = self.model.rowCount()
            self.model.insertRow(row_count)
            self.view.selectRow(row_count)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    editor = DatabaseEditor()
    editor.resize(900, 600)
    editor.show()
    sys.exit(app.exec())
