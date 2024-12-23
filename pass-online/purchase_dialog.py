from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QSpinBox, QPushButton, QMessageBox
)
from PyQt5.QtCore import Qt
from db import purchase_product, get_user_balance, get_user_discount

class PurchaseDialog(QDialog):
    def __init__(self, parent, product_name, price, max_quantity):
        super().__init__(parent)
        self.username = parent.username
        self.product_name = product_name
        self.price = price
        self.max_quantity = max_quantity
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("购买商品")
        self.setFixedSize(300, 200)
        layout = QVBoxLayout()

        # 显示商品信息
        info_layout = QVBoxLayout()
        info_layout.addWidget(QLabel(f"商品名称：{self.product_name}"))
        info_layout.addWidget(QLabel(f"单价：￥{self.price:.2f}"))
        
        # 显示用户余额
        balance = get_user_balance(self.username)
        self.balance_label = QLabel(f"当前余额：￥{balance:.2f}")
        info_layout.addWidget(self.balance_label)

        # 添加折扣显示标签
        self.discount_label = QLabel()
        info_layout.addWidget(self.discount_label)
        
        layout.addLayout(info_layout)

        # 数量选择
        quantity_layout = QHBoxLayout()
        quantity_layout.addWidget(QLabel("购买数量："))
        self.quantity_spin = QSpinBox()
        self.quantity_spin.setMinimum(1)
        self.quantity_spin.setMaximum(self.max_quantity)
        self.quantity_spin.valueChanged.connect(self.update_total)
        quantity_layout.addWidget(self.quantity_spin)
        layout.addLayout(quantity_layout)

        # 显示总价
        self.total_label = QLabel(f"总价：￥{self.price:.2f}")
        layout.addWidget(self.total_label)

        # 按钮
        button_layout = QHBoxLayout()
        buy_button = QPushButton("购买")
        cancel_button = QPushButton("取消")
        buy_button.clicked.connect(self.buy)
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(buy_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)

        self.setLayout(layout)
        self.update_total()  # 初始化时更新总价和折扣显示

    def update_total(self):
        try:
            quantity = self.quantity_spin.value()
            discount = get_user_discount(self.username)
            total = self.price * quantity * discount

            # 更新折扣显示
            if discount == 1.0:
                self.discount_label.setText("当前无折扣优惠")
            else:
                self.discount_label.setText(f"已享受{(1-discount)*100:.0f}折优惠")

            self.total_label.setText(f"总价：￥{total:.2f}")
        except Exception as e:
            print(f"计算总价失败: {e}")
            self.total_label.setText("计算总价失败")

    def buy(self):
        try:
            quantity = self.quantity_spin.value()
            # 计算折扣后的总价
            discount = get_user_discount(self.username)
            total_price = self.price * quantity * discount
            
            success, message = purchase_product(
                self.username, 
                self.product_name, 
                quantity,
                total_price  # 传递折扣后的总价
            )
            
            if success:
                QMessageBox.information(self, "成功", message)
                self.accept()
            else:
                QMessageBox.warning(self, "失败", message)
                
        except Exception as e:
            QMessageBox.critical(self, "错误", f"购买失败: {e}") 