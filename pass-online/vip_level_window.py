from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QTableWidget, 
    QTableWidgetItem, QHeaderView, QMessageBox
)
from PyQt5.QtCore import Qt
from db import get_user_vip_info

class VIPLevelWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("用户VIP等级管理")
        self.setGeometry(100, 100, 800, 600)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # 创建表格
        self.table = QTableWidget()
        self.table.setColumnCount(4)  # 用户名、累计充值、VIP等级、折扣率
        self.table.setHorizontalHeaderLabels([
            "用户名", "累计充值(元)", "VIP等级", "折扣率"
        ])

        # 设置表格列宽
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)

        # 设置表格样式
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)

        layout.addWidget(self.table)
        self.load_vip_info()

    def load_vip_info(self):
        try:
            vip_info = get_user_vip_info()
            self.table.setRowCount(len(vip_info))

            for row, info in enumerate(vip_info):
                # 用户名
                username_item = QTableWidgetItem(info[0])
                username_item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(row, 0, username_item)

                # 累计充值
                recharge_item = QTableWidgetItem(f"￥{float(info[1]):.2f}")
                recharge_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.table.setItem(row, 1, recharge_item)

                # VIP等级
                level_text = "普通用户" if info[2] == 0 else f"VIP {info[2]}"
                level_item = QTableWidgetItem(level_text)
                level_item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(row, 2, level_item)

                # 折扣率
                discounts = {
                    0: "无折扣",
                    1: "95折", 
                    2: "93折", 
                    3: "91折", 
                    4: "88折", 
                    5: "85折"
                }
                discount_item = QTableWidgetItem(discounts.get(info[2], "无折扣"))
                discount_item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(row, 3, discount_item)

        except Exception as e:
            QMessageBox.critical(self, "错误", f"加载VIP信息失败: {e}") 