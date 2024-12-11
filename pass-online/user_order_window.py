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
        self.setGeometry(100, 100, 1100, 600)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # 创建表格
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "买家", "购买时间", "商品名称", "卡密", 
            "激活状态", "交易金额", "操作"
        ])

        # 设置表格列宽
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.Fixed)
        self.table.setColumnWidth(6, 80)

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
                # 买家
                buyer_item = QTableWidgetItem(order[0])
                buyer_item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(row, 0, buyer_item)

                # 购买时间
                purchase_time = order[1]
                if isinstance(purchase_time, str):
                    time_str = purchase_time
                else:
                    time_str = purchase_time.strftime("%Y-%m-%d %H:%M:%S")
                time_item = QTableWidgetItem(time_str)
                time_item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(row, 1, time_item)

                # 商品名称
                product_item = QTableWidgetItem(order[2])
                product_item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(row, 2, product_item)

                # 卡密
                code_item = QTableWidgetItem(order[3])
                code_item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(row, 3, code_item)

                # 激活状态
                status_item = QTableWidgetItem(order[4])
                status_item.setTextAlignment(Qt.AlignCenter)
                if order[4] == '已激活':
                    status_item.setForeground(Qt.green)
                elif order[4] == '失效':
                    status_item.setForeground(Qt.red)
                self.table.setItem(row, 4, status_item)

                # 交易金额
                amount_item = QTableWidgetItem(f"￥{float(order[5]):.2f}")
                amount_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.table.setItem(row, 5, amount_item)

                # 添加激活按钮列
                if order[4] == '未激活':
                    activate_btn = QPushButton("激活")
                    activate_btn.clicked.connect(
                        lambda checked, r=row, c=order[3]: self.activate_order(r, c)
                    )
                    self.table.setCellWidget(row, 6, activate_btn)
                else:
                    empty_item = QTableWidgetItem("")
                    self.table.setItem(row, 6, empty_item)

        except Exception as e:
            QMessageBox.critical(self, "错误", f"加载订单数据失败: {e}")

    def activate_order(self, row, code):
        """激活卡密"""
        try:
            if activate_code(self.username, code):
                QMessageBox.information(self, "成功", "卡密激活成功！")
                self.load_orders()  # 刷新订单列表
            else:
                QMessageBox.warning(self, "失败", "卡密激活失败！")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"激活卡密失败: {e}")