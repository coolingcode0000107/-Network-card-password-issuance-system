# order_management_window.py
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QMessageBox
)
from PyQt5.QtCore import Qt, QDateTime
from db import get_all_orders

class OrderManagementWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("订单管理")
        self.setGeometry(100, 100, 1000, 600)  # 加宽窗口以适应更多列

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # 创建表格
        self.table = QTableWidget()
        self.table.setColumnCount(6)  # 增加列数
        self.table.setHorizontalHeaderLabels([
            "买家", "购买时间", "商品名称", "卡密", 
            "激活状态", "交易金额"
        ])

        # 设置表格列宽
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)

        # 设置表格样式
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)

        layout.addWidget(self.table)
        self.load_orders()

    def load_orders(self):
        try:
            orders = get_all_orders()
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
                self.table.setItem(row, 4, status_item)

                # 交易金额
                amount_item = QTableWidgetItem(f"￥{float(order[5]):.2f}")
                amount_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.table.setItem(row, 5, amount_item)

        except Exception as e:
            QMessageBox.critical(self, "错误", f"加载订单数据失败: {e}")
