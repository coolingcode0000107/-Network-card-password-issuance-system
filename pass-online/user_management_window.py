# user_management_window.py
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QMessageBox, QPushButton, QComboBox
)
from PyQt5.QtCore import Qt
from db import get_all_users, delete_user, update_user_attar

class UserManagementWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("用户管理")
        self.setGeometry(100, 100, 800, 600)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # 创建表格
        self.table = QTableWidget()
        self.table.setColumnCount(3)  # 用户名, 权限, 操作
        self.table.setHorizontalHeaderLabels([
            "用户名", "权限", "操作"
        ])

        # 设置表格列宽
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)

        # 设置表格样式
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)

        layout.addWidget(self.table)
        self.load_users()

    def load_users(self):
        try:
            users = get_all_users()
            self.table.setRowCount(len(users))

            for row, user in enumerate(users):
                # 用户名
                username_item = QTableWidgetItem(user[1])  # user[1]是用户名
                username_item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(row, 0, username_item)

                # 权限（使用下拉框）
                attar_combo = QComboBox()
                attar_combo.addItems(["管理员", "普通用户"])
                attar_combo.setCurrentIndex(0 if user[2] == 1 else 1)  # user[2]是权限
                attar_combo.currentIndexChanged.connect(
                    lambda idx, r=row: self.update_user_attar(r, idx)
                )
                self.table.setCellWidget(row, 1, attar_combo)

                # 删除按钮
                btn_widget = QWidget()
                btn_layout = QHBoxLayout(btn_widget)
                delete_btn = QPushButton("删除")
                delete_btn.clicked.connect(lambda _, r=row: self.delete_user(r))
                btn_layout.addWidget(delete_btn)
                btn_layout.setContentsMargins(5, 0, 5, 0)
                self.table.setCellWidget(row, 2, btn_widget)

        except Exception as e:
            QMessageBox.critical(self, "错误", f"加载用户数据失败: {e}")

    def delete_user(self, row):
        try:
            username = self.table.item(row, 0).text()  # 改为从第0列获取用户名
            
            reply = QMessageBox.question(
                self,
                "确认删除",
                f"确定要删除用户 '{username}' 吗？\n此操作不可恢复！",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                if delete_user(username):
                    QMessageBox.information(self, "成功", "用户已删除！")
                    self.load_users()  # 刷新列表
                else:
                    QMessageBox.warning(self, "失败", "删除用户失败！")
                    
        except Exception as e:
            QMessageBox.critical(self, "错误", f"删除用户失败: {e}")

    def update_user_attar(self, row, index):
        try:
            username = self.table.item(row, 0).text()  # 改为从第0列获取用户名
            new_attar = 1 if index == 0 else 2  # 0=管理员, 1=普通用户
            
            reply = QMessageBox.question(
                self,
                "确认修改",
                f"确定要修改用户 '{username}' 的权限吗？",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                if update_user_attar(username, new_attar):
                    QMessageBox.information(self, "成功", "用户权限已更新！")
                    self.load_users()  # 刷新列表
                else:
                    QMessageBox.warning(self, "失败", "更新用户权限失败！")
                    self.load_users()  # 刷新列表，恢复原来的选择
                    
        except Exception as e:
            QMessageBox.critical(self, "错误", f"更新用户权限失败: {e}")
            self.load_users()  # 刷新列表，恢复原来的选择
