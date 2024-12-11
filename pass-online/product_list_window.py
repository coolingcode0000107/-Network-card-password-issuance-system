from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QTableWidget, 
    QTableWidgetItem, QHeaderView, QMessageBox, QPushButton
)
from PyQt5.QtCore import Qt
from db import get_products_for_user
from purchase_dialog import PurchaseDialog

class ProductListWindow(QMainWindow):
    def __init__(self, username):
        super().__init__()
        self.username = username
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("商品列表")
        self.setGeometry(100, 100, 800, 600)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # 创建表格
        self.table = QTableWidget()
        self.table.setColumnCount(4)  # 商品名称、价格、库存数量、操作
        self.table.setHorizontalHeaderLabels([
            "商品名称", "价格", "库存数量", "操作"
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
        self.load_products()

    def load_products(self):
        """加载商品数据"""
        try:
            products = get_products_for_user()
            self.table.setRowCount(len(products))

            for row, product in enumerate(products):
                # 商品名称
                self.table.setItem(row, 0, QTableWidgetItem(product[0]))
                
                # 价格
                price_item = QTableWidgetItem(f"￥{product[1]:.2f}")
                price_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.table.setItem(row, 1, price_item)
                
                # 库存数量
                quantity_item = QTableWidgetItem(str(product[2]))
                quantity_item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(row, 2, quantity_item)
                
                # 购买按钮
                if product[2] > 0:  # 只有有库存时才显示购买按钮
                    buy_btn = QPushButton("购买")
                    buy_btn.clicked.connect(
                        lambda checked, row=row: self.buy_product(row)
                    )
                    self.table.setCellWidget(row, 3, buy_btn)
                else:
                    self.table.setItem(row, 3, QTableWidgetItem("缺货"))

        except Exception as e:
            QMessageBox.critical(self, "错误", f"加载商品数据失败: {e}")

    def buy_product(self, row):
        """购买商品"""
        try:
            product_name = self.table.item(row, 0).text()
            price = float(self.table.item(row, 1).text().replace('￥', ''))
            available_quantity = int(self.table.item(row, 2).text())

            dialog = PurchaseDialog(self, product_name, price, available_quantity)
            if dialog.exec_() == dialog.Accepted:
                self.load_products()  # 刷新商品列表
                
        except Exception as e:
            QMessageBox.critical(self, "错误", f"购买商品失败: {e}") 