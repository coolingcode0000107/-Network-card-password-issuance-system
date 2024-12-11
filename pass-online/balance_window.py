from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QMessageBox, QInputDialog, QDoubleSpinBox, QDialog
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from db import get_user_balance, add_balance, check_sign_in
from datetime import datetime

class BalanceWindow(QMainWindow):
    def __init__(self, username):
        super().__init__()
        self.username = username
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("余额管理")
        self.setFixedSize(400, 250)  # 增加窗口高度

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(20)  # 增加组件间距

        # 签到按钮 - 放在最上方
        self.sign_in_button = QPushButton("每日签到 +1元")
        self.sign_in_button.setFixedSize(200, 50)  # 设置固定大小
        font = QFont()
        font.setPointSize(12)
        font.setBold(True)
        self.sign_in_button.setFont(font)
        self.sign_in_button.clicked.connect(self.daily_sign_in)
        layout.addWidget(self.sign_in_button, alignment=Qt.AlignCenter)
        
        # 设置签到按钮样式
        self.update_sign_in_button_status()

        # 显示当前余额
        balance = get_user_balance(self.username)
        self.balance_label = QLabel(f"当前余额：￥{balance:.2f}")
        self.balance_label.setAlignment(Qt.AlignCenter)
        font = self.balance_label.font()
        font.setPointSize(16)
        self.balance_label.setFont(font)
        layout.addWidget(self.balance_label)

        # 其他按钮布局
        button_layout = QHBoxLayout()
        
        # 充值按钮
        recharge_button = QPushButton("充值")
        recharge_button.setFixedSize(120, 40)
        recharge_button.clicked.connect(self.recharge)
        button_layout.addWidget(recharge_button)
        
        # 刷新余额按钮
        refresh_button = QPushButton("刷新余额")
        refresh_button.setFixedSize(120, 40)
        refresh_button.clicked.connect(self.refresh_balance)
        button_layout.addWidget(refresh_button)
        
        layout.addLayout(button_layout)

    def update_sign_in_button_status(self):
        """更新签到按钮状态"""
        try:
            from db import get_connection
            conn = get_connection()
            if not conn:
                return
            cursor = conn.cursor()
            
            # 获取用户ID
            cursor.execute("SELECT id FROM users WHERE username = %s", (self.username,))
            result = cursor.fetchone()
            if not result:
                return
            
            user_id = result[0]
            current_date = datetime.now().date()
            
            if check_sign_in(user_id, current_date):
                # 已签到状态
                self.sign_in_button.setStyleSheet("""
                    QPushButton {
                        background-color: #cccccc;
                        color: #666666;
                        border: none;
                        border-radius: 5px;
                    }
                """)
                self.sign_in_button.setText("今日已签到")
                self.sign_in_button.setEnabled(False)
            else:
                # 未签到状态
                self.sign_in_button.setStyleSheet("""
                    QPushButton {
                        background-color: #2ecc71;
                        color: white;
                        border: none;
                        border-radius: 5px;
                    }
                    QPushButton:hover {
                        background-color: #27ae60;
                    }
                """)
                self.sign_in_button.setText("每日签到 +1元")
                self.sign_in_button.setEnabled(True)
        except Exception as e:
            print(f"更新签到按钮状态失败: {e}")
        finally:
            if 'conn' in locals() and conn:
                conn.close()

    def daily_sign_in(self):
        """用户每日签到"""
        try:
            from db import add_sign_in_record
            success, message = add_sign_in_record(self.username)
            if success:
                QMessageBox.information(self, "签到成功", message)
                # 刷新余额显示
                self.refresh_balance()
                # 更新签到按钮状态
                self.update_sign_in_button_status()
            else:
                QMessageBox.warning(self, "签到失败", message)
        except Exception as e:
            QMessageBox.critical(self, "错误", f"签到失败: {e}")

    def refresh_balance(self):
        """刷新余额显示"""
        try:
            balance = get_user_balance(self.username)
            self.balance_label.setText(f"当前余额：￥{balance:.2f}")
            # 同时更新签到按钮状态
            self.update_sign_in_button_status()
        except Exception as e:
            QMessageBox.critical(self, "错误", f"刷新余额失败: {e}")

    def recharge(self):
        try:
            dialog = RechargeDialog(self)
            if dialog.exec_() == dialog.Accepted:
                amount = dialog.get_amount()
                if add_balance(self.username, amount):
                    QMessageBox.information(self, "成功", f"成功充值 ￥{amount:.2f}")
                    # 更新显示的余额
                    new_balance = get_user_balance(self.username)
                    self.balance_label.setText(f"当前余额：￥{new_balance:.2f}")
                else:
                    QMessageBox.warning(self, "失败", "充值失败！")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"充值失败: {e}")

class RechargeDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("充值")
        self.setFixedSize(300, 150)
        
        layout = QVBoxLayout(self)
        
        # 创建一个QDoubleSpinBox作为输入控件
        amount_layout = QHBoxLayout()
        amount_label = QLabel("充值金额：")
        self.amount_input = QDoubleSpinBox()
        self.amount_input.setRange(0.01, 100000.00)
        self.amount_input.setDecimals(2)
        self.amount_input.setValue(100.00)
        self.amount_input.setPrefix("￥")
        amount_layout.addWidget(amount_label)
        amount_layout.addWidget(self.amount_input)
        layout.addLayout(amount_layout)
        
        # 添加按钮
        button_layout = QHBoxLayout()
        confirm_button = QPushButton("确认")
        cancel_button = QPushButton("取消")
        confirm_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(confirm_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)

    def get_amount(self):
        return self.amount_input.value() 