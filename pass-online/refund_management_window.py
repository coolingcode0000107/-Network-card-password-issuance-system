from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QPushButton
)
from PyQt5.QtCore import Qt
from db import get_all_refunds, process_refund

class RefundManagementWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("退款管理")
        self.setGeometry(100, 100, 900, 600)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # 创建表格
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "用户名", "商品名称", "卡密", "退款金额", "状态", "操作"
        ])

        # 设置表格列宽
        header = self.table.horizontalHeader()
        for i in range(5):
            header.setSectionResizeMode(i, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)

        # 设置表格样式
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)

        layout.addWidget(self.table)
        self.load_refunds()

    def load_refunds(self):
        try:
            refunds = get_all_refunds()
            self.table.setRowCount(len(refunds))

            for row, refund in enumerate(refunds):
                for col, value in enumerate(refund[:5]):  # 前5列直接显示数据
                    item = QTableWidgetItem(str(value))
                    item.setTextAlignment(Qt.AlignCenter)
                    self.table.setItem(row, col, item)

                # 添加操作按钮
                if refund[4] == '待处理':  # 状态列
                    approve_btn = QPushButton("同意")
                    reject_btn = QPushButton("拒绝")
                    approve_btn.clicked.connect(
                        lambda checked, r=row, a=True: self.process_refund(r, a)
                    )
                    reject_btn.clicked.connect(
                        lambda checked, r=row, a=False: self.process_refund(r, a)
                    )
                    # 创建一个widget来容纳两个按钮
                    btn_widget = QWidget()
                    btn_layout = QHBoxLayout(btn_widget)
                    btn_layout.addWidget(approve_btn)
                    btn_layout.addWidget(reject_btn)
                    btn_layout.setContentsMargins(0, 0, 0, 0)
                    self.table.setCellWidget(row, 5, btn_widget)
                else:
                    self.table.setItem(row, 5, QTableWidgetItem(""))

        except Exception as e:
            QMessageBox.critical(self, "错误", f"加载退款申请失败: {e}")

    def process_refund(self, row, approve):
        try:
            username = self.table.item(row, 0).text()
            code = self.table.item(row, 2).text()
            amount = float(self.table.item(row, 3).text())
            
            action = "同意" if approve else "拒绝"
            reply = QMessageBox.question(
                self, 
                f"确认{action}", 
                f"确定要{action}这个退款申请吗？",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                if process_refund(username, code, approve, amount):
                    QMessageBox.information(self, "成功", f"已{action}退款申请！")
                    self.load_refunds()  # 刷新列表
                else:
                    QMessageBox.warning(self, "失败", f"{action}退款申请失败！")
                    
        except Exception as e:
            QMessageBox.critical(self, "错误", f"处理退款申请失败: {e}") 