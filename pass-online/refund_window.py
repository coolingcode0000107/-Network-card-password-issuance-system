from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, 
    QPushButton, QTabWidget
)
from PyQt5.QtCore import Qt
from db import (
    get_user_orders, request_refund, get_product_price,
    get_user_refund_records  # 新增导入
)

class RefundWindow(QMainWindow):
    def __init__(self, username):
        super().__init__()
        self.username = username
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("退款管理")
        self.setGeometry(100, 100, 900, 600)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # 创建选项卡
        tab_widget = QTabWidget()
        
        # 申请退款选项卡
        refund_tab = QWidget()
        refund_layout = QVBoxLayout(refund_tab)
        self.refund_table = self.create_refund_table()
        refund_layout.addWidget(self.refund_table)
        
        # 退款记录选项卡
        status_tab = QWidget()
        status_layout = QVBoxLayout(status_tab)
        self.status_table = self.create_status_table()
        status_layout.addWidget(self.status_table)

        tab_widget.addTab(refund_tab, "申请退款")
        tab_widget.addTab(status_tab, "退款记录")
        
        layout.addWidget(tab_widget)
        
        # 加载数据
        self.load_orders()
        self.load_refund_records()

    def create_refund_table(self):
        table = QTableWidget()
        table.setColumnCount(5)
        table.setHorizontalHeaderLabels([
            "购买时间", "商品名称", "卡密", "状态", "操作"
        ])

        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)

        table.setAlternatingRowColors(True)
        table.setSelectionBehavior(QTableWidget.SelectRows)
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        return table

    def create_status_table(self):
        table = QTableWidget()
        table.setColumnCount(4)
        table.setHorizontalHeaderLabels([
            "商品名称", "退款卡密", "退款金额", "退款状态"
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
        try:
            orders = get_user_orders(self.username)
            self.refund_table.setRowCount(len(orders))

            for row, order in enumerate(orders):
                # 购买时间
                time_str = order[0].strftime("%Y-%m-%d %H:%M:%S")
                self.refund_table.setItem(row, 0, QTableWidgetItem(time_str))
                
                # 商品名称
                self.refund_table.setItem(row, 1, QTableWidgetItem(order[1]))
                
                # 卡密
                self.refund_table.setItem(row, 2, QTableWidgetItem(order[2]))
                
                # 状态
                status_item = QTableWidgetItem(order[3])
                if order[3] == '已激活':
                    status_item.setForeground(Qt.green)
                elif order[3] == '失效':
                    status_item.setForeground(Qt.red)
                self.refund_table.setItem(row, 3, status_item)
                
                # 退款按钮
                if order[3] == '未激活':
                    refund_btn = QPushButton("申请退款")
                    refund_btn.clicked.connect(
                        lambda checked, row=row: self.request_refund(row)
                    )
                    self.refund_table.setCellWidget(row, 4, refund_btn)
                else:
                    self.refund_table.setItem(row, 4, QTableWidgetItem(""))

        except Exception as e:
            QMessageBox.critical(self, "错误", f"加载订单数据失败: {e}")

    def load_refund_records(self):
        try:
            records = get_user_refund_records(self.username)
            self.status_table.setRowCount(len(records))

            for row, record in enumerate(records):
                # 商品名称
                self.status_table.setItem(row, 0, QTableWidgetItem(record[0]))
                # 退款卡密
                self.status_table.setItem(row, 1, QTableWidgetItem(record[1]))
                # 退款金额
                amount_item = QTableWidgetItem(f"￥{record[2]:.2f}")
                amount_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.status_table.setItem(row, 2, amount_item)
                # 退款状态
                status_item = QTableWidgetItem(record[3])
                if record[3] == '已同意':
                    status_item.setForeground(Qt.green)
                elif record[3] == '已拒绝':
                    status_item.setForeground(Qt.red)
                elif record[3] == '待处理':
                    status_item.setForeground(Qt.blue)
                self.status_table.setItem(row, 3, status_item)

        except Exception as e:
            QMessageBox.critical(self, "错误", f"加载退款记录失败: {e}")

    def request_refund(self, row):
        try:
            product_name = self.refund_table.item(row, 1).text()
            code = self.refund_table.item(row, 2).text()
            
            # 获取商品实际价格
            refund_amount = get_product_price(product_name)
            if refund_amount is None:
                QMessageBox.warning(self, "失败", "无法获取商品价格！")
                return
            
            reply = QMessageBox.question(
                self, 
                "确认退款", 
                f"确定要申请退款吗？\n退款金额：￥{refund_amount:.2f}\n退款申请提交后需要等待管理员审核。",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                success, message = request_refund(self.username, product_name, code, refund_amount)
                if success:
                    QMessageBox.information(self, "成功", "退款申请已提交，请等待审核！")
                    self.load_orders()  # 刷新订单列表
                    self.load_refund_records()  # 刷新退款记录
                else:
                    QMessageBox.warning(self, "失败", message)
                    
        except Exception as e:
            QMessageBox.critical(self, "错误", f"申请退款失败: {e}") 