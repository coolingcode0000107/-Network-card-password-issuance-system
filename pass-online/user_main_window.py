from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QTableWidget, 
    QTableWidgetItem, QHeaderView, QMessageBox, QAction
)
from PyQt5.QtCore import Qt
from db import get_products_for_user
from user_order_window import UserOrderWindow
from purchase_dialog import PurchaseDialog
from refund_window import RefundWindow
from balance_window import BalanceWindow

class UserMainWindow(QMainWindow):
    def __init__(self, username):
        try:
            print(f"开始初始化用户窗口，用户名: {username}")  # 调试信息
            super().__init__()
            
            # 确保在使用username之前进行验证
            if not username:
                raise ValueError("用户名不能为空")
            self.username = username
            
            print("初始化类属性")  # 调试信息
            # 初始化类属性
            self.table = None
            self.product_window = None
            self.order_window = None
            self.refund_window = None
            self.balance_window = None
            
            print("开始初始化UI")  # 调试信息
            # 调用UI初始化
            self.init_ui()
            print("UI初始化完成")  # 调试信息
            
        except Exception as e:
            print(f"用户窗口初始化失败: {str(e)}")  # 调试信息
            QMessageBox.critical(None, "错误", f"初始化用户窗口失败: {str(e)}")
            raise e

    def init_ui(self):
        try:
            print("开始设置窗口属性")  # 调试信息
            # 设置窗口基本属性
            self.setWindowTitle("商品列表")
            self.setGeometry(100, 100, 800, 600)
            self.setAttribute(Qt.WA_DeleteOnClose)

            print("创建中央窗口部件")  # 调试信息
            # 创建中央窗口部件
            central_widget = QWidget()
            self.setCentralWidget(central_widget)
            layout = QVBoxLayout(central_widget)

            print("创建菜单栏")  # 调试信息
            # 创建菜单栏
            menubar = self.menuBar()

            # 商品菜单
            product_menu = menubar.addMenu("商品")
            buy_action = QAction("购买商品", self)
            buy_action.triggered.connect(self.buy_product)
            product_menu.addAction(buy_action)

            # 订单菜单
            order_menu = menubar.addMenu("订单")
            view_orders_action = QAction("查看订单", self)
            view_orders_action.triggered.connect(self.view_orders)
            order_menu.addAction(view_orders_action)

            # 退款菜单
            refund_menu = menubar.addMenu("退款")
            refund_action = QAction("退款申请", self)
            refund_action.triggered.connect(self.request_refund)
            refund_menu.addAction(refund_action)

            # 余额菜单
            balance_menu = menubar.addMenu("余额")
            balance_action = QAction("余额管理", self)
            balance_action.triggered.connect(self.manage_balance)
            balance_menu.addAction(balance_action)

            # 添加退出登录菜单
            logout_menu = menubar.addMenu("系统")
            logout_action = QAction("退出登录", self)
            logout_action.triggered.connect(self.logout)
            logout_menu.addAction(logout_action)

            print("初始化表格")  # 调试信息
            # 创建并初始化表格
            self.init_table()
            layout.addWidget(self.table)
            
            print("加载商品数据")  # 调试信息
            # 加载商品数据
            self.load_products()
            print("UI初始化完成")  # 调试信息
            
        except Exception as e:
            print(f"UI初始化失败: {str(e)}")  # 调试信息
            QMessageBox.critical(self, "错误", f"初始化界面失败: {str(e)}")
            raise e

    def init_table(self):
        """初始化表格"""
        try:
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
        except Exception as e:
            QMessageBox.critical(self, "错误", f"初始化表格失败: {str(e)}")
            raise e

            layout.addWidget(self.table)
            
            # 加载商品数据
            self.load_products()
        except Exception as e:
            QMessageBox.critical(self, "错误", f"初始化界面失败: {str(e)}")
            raise e

    def create_menu_bar(self):
        menubar = self.menuBar()

        # 商品菜单
        product_menu = menubar.addMenu("商品")
        buy_action = QAction("购买商品", self)
        buy_action.triggered.connect(self.buy_product)
        product_menu.addAction(buy_action)

        # 订单菜单
        order_menu = menubar.addMenu("订单")
        view_orders_action = QAction("查看订单", self)
        view_orders_action.triggered.connect(self.view_orders)
        order_menu.addAction(view_orders_action)

        # 退款菜单
        refund_menu = menubar.addMenu("退款")
        refund_action = QAction("退款申请", self)
        refund_action.triggered.connect(self.request_refund)
        refund_menu.addAction(refund_action)

        # 余额菜单
        balance_menu = menubar.addMenu("余额")
        balance_action = QAction("余额管理", self)
        balance_action.triggered.connect(self.manage_balance)
        balance_menu.addAction(balance_action)

    def load_products(self):
        try:
            products = get_products_for_user()
            self.table.setRowCount(len(products))
            for row, product in enumerate(products):
                for col, value in enumerate(product):
                    item = QTableWidgetItem(str(value))
                    item.setTextAlignment(Qt.AlignCenter)
                    self.table.setItem(row, col, item)
        except Exception as e:
            QMessageBox.critical(self, "错误", f"加载商品数据失败: {e}")

    def buy_product(self):
        try:
            selected_items = self.table.selectedItems()
            if not selected_items:
                QMessageBox.warning(self, "警告", "请先选择要购买的商品！")
                return

            row = selected_items[0].row()
            product_name = self.table.item(row, 0).text()
            price = float(self.table.item(row, 1).text())
            available_quantity = int(self.table.item(row, 2).text())

            dialog = PurchaseDialog(self, product_name, price, available_quantity)
            dialog.exec_()
            
            # 刷新商品列表
            self.load_products()
        except Exception as e:
            QMessageBox.critical(self, "错误", f"购买商品失败: {e}")

    def view_orders(self):
        try:
            self.order_window = UserOrderWindow(self.username)
            self.order_window.show()
        except Exception as e:
            QMessageBox.critical(self, "错误", f"无法打开订单窗口: {e}")

    def request_refund(self):
        try:
            self.refund_window = RefundWindow(self.username)
            self.refund_window.show()
        except Exception as e:
            QMessageBox.critical(self, "错误", f"无法打开退款窗口: {e}")

    def manage_balance(self):
        try:
            self.balance_window = BalanceWindow(self.username)
            self.balance_window.show()
        except Exception as e:
            QMessageBox.critical(self, "错误", f"无法打开余额管理窗口: {e}")

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
                    'product_window', 'order_window', 
                    'refund_window', 'balance_window'
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