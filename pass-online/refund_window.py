from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QTableWidget,
    QTableWidgetItem, QHeaderView, QMessageBox, QPushButton,
    QTabWidget
)
from PyQt5.QtCore import Qt
from db import get_user_orders, submit_refund_request, get_refund_status

class RefundWindow(QMainWindow):
    def __init__(self, username):
        super().__init__()
        self.username = username
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("退款管理")
        self.setGeometry(100, 100, 1000, 600)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # 创建标签页
        tab_widget = QTabWidget()
        
        # 申请退款标签页
        refund_tab = QWidget()
        refund_layout = QVBoxLayout(refund_tab)
        self.refund_table = self.create_order_table()
        refund_layout.addWidget(self.refund_table)
        tab_widget.addTab(refund_tab, "申请退款")

        # 退款进度标签页
        status_tab = QWidget()
        status_layout = QVBoxLayout(status_tab)
        self.status_table = self.create_status_table()
        status_layout.addWidget(self.status_table)
        tab_widget.addTab(status_tab, "退款进度")

        layout.addWidget(tab_widget)
        
        # 加载数据
        self.load_orders()
        self.load_refund_status()

    def create_order_table(self):
        """创建订单表格"""
        table = QTableWidget()
        table.setColumnCount(7)
        table.setHorizontalHeaderLabels([
            "买家", "购买时间", "商品名称", "卡密", 
            "激活状态", "交易金额", "操作"
        ])

        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.Fixed)
        table.setColumnWidth(6, 80)

        table.setAlternatingRowColors(True)
        table.setSelectionBehavior(QTableWidget.SelectRows)
        table.setEditTriggers(QTableWidget.NoEditTriggers)

        return table

    def create_status_table(self):
        """创建退款状态表格"""
        table = QTableWidget()
        table.setColumnCount(4)
        table.setHorizontalHeaderLabels([
            "商品名称", "卡密", "退款金额", "状态"
        ])

        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)

        table.setAlternatingRowColors(True)
        table.setSelectionBehavior(QTableWidget.SelectRows)
        table.setEditTriggers(QTableWidget.NoEditTriggers)

        return table

    def load_orders(self):
        """加载订单数据"""
        try:
            orders = get_user_orders(self.username)
            self.refund_table.setRowCount(len(orders))

            for row, order in enumerate(orders):
                # 买家
                buyer_item = QTableWidgetItem(order[0])
                buyer_item.setTextAlignment(Qt.AlignCenter)
                self.refund_table.setItem(row, 0, buyer_item)

                # 购买时间
                purchase_time = order[1]
                if isinstance(purchase_time, str):
                    time_str = purchase_time
                else:
                    time_str = purchase_time.strftime("%Y-%m-%d %H:%M:%S")
                time_item = QTableWidgetItem(time_str)
                time_item.setTextAlignment(Qt.AlignCenter)
                self.refund_table.setItem(row, 1, time_item)

                # 商品名称
                product_item = QTableWidgetItem(order[2])
                product_item.setTextAlignment(Qt.AlignCenter)
                self.refund_table.setItem(row, 2, product_item)

                # 卡密
                code_item = QTableWidgetItem(order[3])
                code_item.setTextAlignment(Qt.AlignCenter)
                self.refund_table.setItem(row, 3, code_item)

                # 激活状态
                status_item = QTableWidgetItem(order[4])
                status_item.setTextAlignment(Qt.AlignCenter)
                if order[4] == '已激活':
                    status_item.setForeground(Qt.green)
                elif order[4] == '失效':
                    status_item.setForeground(Qt.red)
                self.refund_table.setItem(row, 4, status_item)

                # 交易金额
                amount_item = QTableWidgetItem(f"￥{float(order[5]):.2f}")
                amount_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.refund_table.setItem(row, 5, amount_item)

                # 添加退款按钮
                if order[4] == '未激活':  # 只有未激活的订单可以申请退款
                    refund_btn = QPushButton("申请退款")
                    refund_btn.clicked.connect(
                        lambda checked, r=row, p=order[2], c=order[3]: self.request_refund(r, p, c)
                    )
                    self.refund_table.setCellWidget(row, 6, refund_btn)
                else:
                    empty_item = QTableWidgetItem("")
                    self.refund_table.setItem(row, 6, empty_item)

        except Exception as e:
            QMessageBox.critical(self, "错误", f"加载订单数据失败: {e}")

    def request_refund(self, row, product_name, code):
        """申请退款"""
        try:
            reply = QMessageBox.question(
                self, 
                "确认退款", 
                "确定要申请退款吗？\n退款申请提交后将无法撤销。",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                success, message = submit_refund_request(
                    self.username, product_name, code
                )
                if success:
                    QMessageBox.information(self, "成功", message)
                    self.load_orders()  # 刷新订单列表
                    self.load_refund_status()  # 刷新退款状态
                else:
                    QMessageBox.warning(self, "失败", message)
        except Exception as e:
            QMessageBox.critical(self, "错误", f"申请退款失败: {e}") 

    def load_refund_status(self):
        """加载退款状态数据"""
        try:
            refunds = get_refund_status(self.username)
            self.status_table.setRowCount(len(refunds))

            for row, refund in enumerate(refunds):
                # 商品名称
                product_item = QTableWidgetItem(refund[0])
                product_item.setTextAlignment(Qt.AlignCenter)
                self.status_table.setItem(row, 0, product_item)

                # 卡密
                code_item = QTableWidgetItem(refund[1])
                code_item.setTextAlignment(Qt.AlignCenter)
                self.status_table.setItem(row, 1, code_item)

                # 退款金额
                amount_item = QTableWidgetItem(f"￥{float(refund[2]):.2f}")
                amount_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.status_table.setItem(row, 2, amount_item)

                # 状态
                status_item = QTableWidgetItem(refund[3])
                status_item.setTextAlignment(Qt.AlignCenter)
                if refund[3] == '已同意':
                    status_item.setForeground(Qt.green)
                elif refund[3] == '已拒绝':
                    status_item.setForeground(Qt.red)
                self.status_table.setItem(row, 3, status_item)

        except Exception as e:
            QMessageBox.critical(self, "错误", f"加载退款状态失败: {e}")