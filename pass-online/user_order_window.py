from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QTableWidget,
    QTableWidgetItem, QHeaderView, QMessageBox, QPushButton
)
from PyQt5.QtCore import Qt
from db import get_user_orders, activate_code

class UserOrderWindow(QMainWindow):
    def __init__(self, username):
        super().__init__()
        self.username = username
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("我的订单")
        self.setGeometry(100, 100, 900, 600)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # 创建表格
        self.table = QTableWidget()
        self.table.setColumnCount(5)  # 包括激活按钮列
        self.table.setHorizontalHeaderLabels([
            "购买时间", "商品名称", "卡密", "状态", "操作"
        ])

        # 设置表格列宽
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)

        # 设置表格样式
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)

        layout.addWidget(self.table)
        self.load_orders()

    def load_orders(self):
        try:
            orders = get_user_orders(self.username)
            self.table.setRowCount(len(orders))

            for row, order in enumerate(orders):
                # 购买时间
                time_str = order[0].strftime("%Y-%m-%d %H:%M:%S")
                self.table.setItem(row, 0, QTableWidgetItem(time_str))

                # 商品名称
                self.table.setItem(row, 1, QTableWidgetItem(order[1]))

                # 卡密
                self.table.setItem(row, 2, QTableWidgetItem(order[2]))

                # 状态
                status_item = QTableWidgetItem(order[3])
                if order[3] == '已激活':
                    status_item.setForeground(Qt.green)
                elif order[3] == '失效':
                    status_item.setForeground(Qt.red)
                self.table.setItem(row, 3, status_item)

                # 激活按钮
                if order[3] == '未激活':
                    activate_btn = QPushButton("激活")
                    activate_btn.clicked.connect(
                        lambda checked, row=row: self.activate_order(row)
                    )
                    self.table.setCellWidget(row, 4, activate_btn)
                else:
                    self.table.setItem(row, 4, QTableWidgetItem(""))

        except Exception as e:
            QMessageBox.critical(self, "错误", f"加载订单数据失败: {e}")

    def activate_order(self, row):
        try:
            code = self.table.item(row, 2).text()
            if activate_code(self.username, code):
                QMessageBox.information(self, "成功", "卡密激活成功！")
                self.load_orders()  # 刷新订单列表
            else:
                QMessageBox.warning(self, "失败", "卡密激活失败！")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"激活卡密失败: {e}")