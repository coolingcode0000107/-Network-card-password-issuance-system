# product_management.py
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QMessageBox, QAction, QDialog, QHBoxLayout, QLabel, QLineEdit, QPushButton
)
from PyQt5.QtCore import Qt
from db import (
    get_all_products, add_product_with_cards, update_product, delete_product
)
from user_management_window import UserManagementWindow
from order_management_window import OrderManagementWindow
from refund_management_window import RefundManagementWindow

class ProductManagement(QMainWindow):
    def __init__(self):
        super().__init__()
        try:
            self.setWindowTitle("商品管理系统")
            self.setGeometry(100, 100, 800, 600)

            # 创建中央窗口部件
            central_widget = QWidget()
            self.setCentralWidget(central_widget)

            # 创建布局
            layout = QVBoxLayout(central_widget)

            # 创建菜单栏
            self.create_menu_bar()

            # 创建表格
            self.table = QTableWidget()
            self.table.setColumnCount(3)
            self.table.setHorizontalHeaderLabels(["商品名称", "价格", "库存数量"])

            # 设置表格列宽
            header = self.table.horizontalHeader()
            header.setSectionResizeMode(0, QHeaderView.Stretch)
            header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
            header.setSectionResizeMode(2, QHeaderView.ResizeToContents)

            # 设置表格样式
            self.table.setAlternatingRowColors(True)
            self.table.setSelectionBehavior(QTableWidget.SelectRows)
            self.table.setSelectionMode(QTableWidget.SingleSelection)
            self.table.setEditTriggers(QTableWidget.NoEditTriggers)

            # 添加到布局
            layout.addWidget(self.table)

            # 加载商品数据
            self.load_products()

        except Exception as e:
            QMessageBox.critical(None, "错误", f"初始化商品管理界面失败: {e}")
            raise e

    def create_menu_bar(self):
        menu_bar = self.menuBar()

        # 用户管理菜单
        user_menu = menu_bar.addMenu("用户管理")
        view_users_action = QAction("查看用户", self)
        view_users_action.triggered.connect(self.open_user_management)
        user_menu.addAction(view_users_action)

        # 订单查看菜单
        order_menu = menu_bar.addMenu("订单查看")
        view_orders_action = QAction("查看订单", self)
        view_orders_action.triggered.connect(self.open_order_management)
        order_menu.addAction(view_orders_action)

        # 退款管理菜单
        refund_menu = menu_bar.addMenu("退款管理")
        view_refunds_action = QAction("查看退款", self)
        view_refunds_action.triggered.connect(self.open_refund_management)
        clear_refunds_action = QAction("清理已处理记录", self)
        clear_refunds_action.triggered.connect(self.clear_processed_refunds)
        refund_menu.addAction(view_refunds_action)
        refund_menu.addAction(clear_refunds_action)

        # 商品管理菜单
        product_menu = menu_bar.addMenu("商品管理")
        add_product_action = QAction("添加商品", self)
        add_product_action.triggered.connect(self.add_product_dialog)
        delete_product_action = QAction("删除商品", self)
        delete_product_action.triggered.connect(self.delete_selected_product)
        update_product_action = QAction("修改商品", self)
        update_product_action.triggered.connect(self.update_selected_product)

        product_menu.addAction(add_product_action)
        product_menu.addAction(delete_product_action)
        product_menu.addAction(update_product_action)

        # 添���退出登录菜单
        logout_menu = menu_bar.addMenu("系统")
        logout_action = QAction("退出登录", self)
        logout_action.triggered.connect(self.logout)
        logout_menu.addAction(logout_action)

    def load_products(self):
        """加载商品数据"""
        try:
            products = get_all_products()

            # 设置表格行数
            self.table.setRowCount(len(products))

            # 填充数据
            for row, product in enumerate(products):
                for col, value in enumerate(product):
                    item = QTableWidgetItem(str(value))
                    item.setTextAlignment(Qt.AlignCenter)
                    self.table.setItem(row, col, item)
                    
        except Exception as e:
            QMessageBox.critical(self, "错误", f"加载商品数据失败: {e}")

    def add_product_dialog(self):
        """打开添加商品对话框"""
        try:
            dialog = AddProductDialog(self)
            if dialog.exec_() == QDialog.Accepted:
                name, price, quantity = dialog.get_data()
                success = add_product_with_cards(name, price, quantity)
                if success:
                    QMessageBox.information(self, "成功", f"商品添加成功！已生成 {quantity} 个卡密。")
                    self.load_products()
        except Exception as e:
            QMessageBox.critical(self, "错误", f"添加商品失败: {e}")

    def delete_selected_product(self):
        """删除选中的商品"""
        try:
            selected_items = self.table.selectedItems()
            if not selected_items:
                QMessageBox.warning(self, "警告", "请先选择要删除的商品！")
                return
                
            row = selected_items[0].row()
            product_name = self.table.item(row, 0).text()
            
            reply = QMessageBox.question(
                self, "确认删除", 
                f"确定要删除商品 '{product_name}' 吗？\n这将同时删除该商品的所有卡密！",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                success = delete_product(product_name)
                if success:
                    QMessageBox.information(self, "成功", "商品及其卡密已成功删除！")
                    self.load_products()
                    
        except Exception as e:
            QMessageBox.critical(self, "错误", f"删除商品失败: {e}")

    def update_selected_product(self):
        """更新选中的商品"""
        try:
            selected_items = self.table.selectedItems()
            if not selected_items:
                QMessageBox.warning(self, "警告", "请先选择要修改的商品！")
                return
            row = selected_items[0].row()
            product_name = self.table.item(row, 0).text()
            current_price = self.table.item(row, 1).text()
            current_quantity = self.table.item(row, 2).text()

            dialog = UpdateProductDialog(self, product_name, current_price, current_quantity)
            if dialog.exec_() == QDialog.Accepted:
                new_price, new_quantity = dialog.get_data()
                success = update_product(product_name, new_price, new_quantity)
                if success:
                    QMessageBox.information(self, "成功", "商品更新成功！")
                    self.load_products()
        except Exception as e:
            QMessageBox.critical(self, "错误", f"更新商品失败: {e}")

    def open_user_management(self):
        """打开用户管理界面"""
        try:
            self.user_management_window = UserManagementWindow()
            self.user_management_window.show()
        except Exception as e:
            QMessageBox.critical(self, "错误", f"无法打开用户管理界面: {e}")

    def open_order_management(self):
        """打开订单管理界面"""
        try:
            self.order_management_window = OrderManagementWindow()
            self.order_management_window.show()
        except Exception as e:
            QMessageBox.critical(self, "错误", f"无法打开订单管理界面: {e}")

    def open_refund_management(self):
        """打开退款管理界面"""
        try:
            self.refund_management_window = RefundManagementWindow()
            self.refund_management_window.show()
        except Exception as e:
            QMessageBox.critical(self, "错误", f"无法打开退款管理界面: {e}")

    def clear_processed_refunds(self):
        """清理已处理的退款记录"""
        try:
            reply = QMessageBox.question(
                self,
                "确认清理",
                "确定要清理所有已处理的退款记录吗？\n此操作不可恢复！",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                from db import clear_processed_refunds
                if clear_processed_refunds():
                    QMessageBox.information(self, "成功", "已清理所有已处理的退款记录！")
                    # 如果退款管理窗口已打开，刷新其显示
                    if hasattr(self, 'refund_management_window'):
                        self.refund_management_window.load_refunds()
                else:
                    QMessageBox.warning(self, "失败", "清理退款记录失败！")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"清理退款记录失败: {e}")

    def logout(self):
        """退出登录"""
        try:
            reply = QMessageBox.question(
                self, 
                '确认退出', 
                '确定要退出登录吗？',
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                # 关闭所有可能存在的子窗口
                windows_to_close = [
                    'user_management_window', 'order_management_window', 
                    'refund_management_window'
                ]
                
                for window_name in windows_to_close:
                    window = getattr(self, window_name, None)
                    if window is not None:
                        window.close()
                
                # 创建并显示登录窗口
                from login import LoginWindow
                self.login_window = LoginWindow()
                self.login_window.show()
                
                # 关闭当前窗口
                self.close()
                
        except Exception as e:
            print(f"退出登录时发生错误: {str(e)}")  # 添加调试信息
            QMessageBox.critical(self, "错误", f"退出登录失败: {e}")

class AddProductDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("添加商品")
        self.setFixedSize(300, 200)

        layout = QVBoxLayout()

        # 商品名称
        name_layout = QHBoxLayout()
        name_label = QLabel("商品名称:")
        self.name_input = QLineEdit()
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.name_input)
        layout.addLayout(name_layout)

        # 价格
        price_layout = QHBoxLayout()
        price_label = QLabel("价格:")
        self.price_input = QLineEdit()
        self.price_input.setPlaceholderText("0.00")
        price_layout.addWidget(price_label)
        price_layout.addWidget(self.price_input)
        layout.addLayout(price_layout)

        # 库存数量
        quantity_layout = QHBoxLayout()
        quantity_label = QLabel("库存数量:")
        self.quantity_input = QLineEdit()
        self.quantity_input.setPlaceholderText("0")
        quantity_layout.addWidget(quantity_label)
        quantity_layout.addWidget(self.quantity_input)
        layout.addLayout(quantity_layout)

        # 按钮
        button_layout = QHBoxLayout()
        add_button = QPushButton("添加")
        cancel_button = QPushButton("取消")
        add_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(add_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def accept(self):
        name = self.name_input.text().strip()
        price = self.price_input.text().strip()
        quantity = self.quantity_input.text().strip()

        if not name or not price or not quantity:
            QMessageBox.warning(self, "警告", "请填写所有字段！")
            return

        try:
            price = float(price)
            quantity = int(quantity)
            if price < 0 or quantity < 0:
                QMessageBox.warning(self, "警告", "价格和数量必须为非负数！")
                return
        except ValueError:
            QMessageBox.warning(self, "警告", "价格必须是数字，数量必须是整数！")
            return

        super().accept()

    def get_data(self):
        name = self.name_input.text().strip()
        price = float(self.price_input.text().strip())
        quantity = int(self.quantity_input.text().strip())
        return name, price, quantity

class UpdateProductDialog(QDialog):
    def __init__(self, parent=None, name="", price="", quantity=""):
        super().__init__(parent)
        self.product_name = name
        self.init_ui(price, quantity)

    def init_ui(self, price, quantity):
        self.setWindowTitle("修改商品")
        self.setFixedSize(300, 200)

        layout = QVBoxLayout()

        # 商品名称 (显示，不能修改)
        name_layout = QHBoxLayout()
        name_label = QLabel("商品名称:")
        self.name_display = QLabel(self.product_name)
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.name_display)
        layout.addLayout(name_layout)

        # 价格
        price_layout = QHBoxLayout()
        price_label = QLabel("价格:")
        self.price_input = QLineEdit(str(price))
        price_layout.addWidget(price_label)
        price_layout.addWidget(self.price_input)
        layout.addLayout(price_layout)

        # 库存数量
        quantity_layout = QHBoxLayout()
        quantity_label = QLabel("库存数量:")
        self.quantity_input = QLineEdit(str(quantity))
        quantity_layout.addWidget(quantity_label)
        quantity_layout.addWidget(self.quantity_input)
        layout.addLayout(quantity_layout)

        # ���钮
        button_layout = QHBoxLayout()
        update_button = QPushButton("更新")
        cancel_button = QPushButton("取消")
        update_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(update_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def accept(self):
        price = self.price_input.text().strip()
        quantity = self.quantity_input.text().strip()

        if not price or not quantity:
            QMessageBox.warning(self, "警告", "请填写所有字段！")
            return

        try:
            price = float(price)
            quantity = int(quantity)
            if price < 0 or quantity < 0:
                QMessageBox.warning(self, "警告", "价格和数量必须为非负数！")
                return
        except ValueError:
            QMessageBox.warning(self, "警告", "价格必须是数字，数量必须是整数！")
            return

        super().accept()

    def get_data(self):
        price = float(self.price_input.text().strip())
        quantity = int(self.quantity_input.text().strip())
        return price, quantity
