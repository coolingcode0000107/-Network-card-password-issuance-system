# register.py
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QPushButton, QRadioButton, QButtonGroup,
                             QMessageBox, QWidget)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from db import get_connection, close_connection
from utils import hash_password
import bcrypt
import re  # 添加re模块用于邮箱格式验证

class RegisterDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('用户注册')
        self.setFixedSize(500, 400)

        layout = QVBoxLayout()
        layout.setSpacing(20)

        # 设置默认字体
        self.default_font = QFont()
        self.default_font.setPointSize(12)

        # 添加各个控件
        layout.addStretch(1)
        layout.addLayout(self.create_input_layout('账号:', False))
        layout.addLayout(self.create_input_layout('密码:', True))
        layout.addLayout(self.create_input_layout('邮箱:', False))
        layout.addLayout(self.create_identity_layout())
        layout.addLayout(self.create_activation_layout())
        layout.addLayout(self.create_button_layout())
        layout.addStretch(1)

        layout.setContentsMargins(50, 20, 50, 20)
        self.setLayout(layout)

    def create_input_layout(self, label_text, is_password=False):
        layout = QHBoxLayout()
        label = QLabel(label_text)
        label.setFont(self.default_font)
        input_field = QLineEdit()
        input_field.setFont(self.default_font)
        input_field.setMinimumHeight(40)

        if is_password:
            input_field.setEchoMode(QLineEdit.Password)
            self.password_input = input_field
        elif label_text == '账号:':
            self.account_input = input_field
        else:
            self.email_input = input_field

        layout.addWidget(label)
        layout.addWidget(input_field)
        return layout

    def create_identity_layout(self):
        layout = QHBoxLayout()
        self.identity_group = QButtonGroup()
        self.admin_radio = QRadioButton('管理员')
        self.user_radio = QRadioButton('普通用户')

        for radio in [self.admin_radio, self.user_radio]:
            radio.setFont(self.default_font)
            layout.addWidget(radio)
            self.identity_group.addButton(radio)

        self.user_radio.setChecked(True)
        self.admin_radio.toggled.connect(self.toggle_activation_code)
        return layout

    def create_activation_layout(self):
        # 创建一个容器 QWidget
        self.activation_widget = QWidget()
        self.activation_layout = QHBoxLayout(self.activation_widget)

        label = QLabel('激活码:')
        label.setFont(self.default_font)
        self.activation_input = QLineEdit()
        self.activation_input.setFont(self.default_font)
        self.activation_input.setMinimumHeight(40)
        self.activation_input.setEchoMode(QLineEdit.Password)

        self.activation_layout.addWidget(label)
        self.activation_layout.addWidget(self.activation_input)

        # 初始状态为隐藏
        self.activation_widget.setVisible(False)

        # 将 activation_widget 添加到主布局中
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.activation_widget)
        return main_layout

    def create_button_layout(self):
        layout = QHBoxLayout()
        layout.setSpacing(20)

        self.register_button = QPushButton('注册')
        self.cancel_button = QPushButton('取消')

        for button in [self.register_button, self.cancel_button]:
            button.setFont(self.default_font)
            button.setMinimumHeight(40)
            button.setMinimumWidth(120)

        self.register_button.clicked.connect(self.register)
        self.cancel_button.clicked.connect(self.close)

        layout.addWidget(self.register_button)
        layout.addWidget(self.cancel_button)
        return layout

    def toggle_activation_code(self, checked):
        self.activation_widget.setVisible(checked)
        if checked:
            self.setFixedHeight(450)
        else:
            self.setFixedHeight(400)

    def validate_email(self, email):
        """验证邮箱格式"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None

    def register(self):
        username = self.account_input.text()
        password = self.password_input.text()
        email = self.email_input.text()
        is_admin = self.admin_radio.isChecked()

        if not all([username, password, email]):
            QMessageBox.warning(self, "警告", "请填写所有必填信息！")
            return

        if not self.validate_email(email):
            QMessageBox.warning(self, "警告", "邮箱格式不正确！")
            return

        if is_admin:
            activation_code = self.activation_input.text()
            if activation_code != "123":
                QMessageBox.warning(self, "警告", "管理员激活码错误！")
                return

        try:
            conn = get_connection()
            if not conn:
                return
            cursor = conn.cursor()

            # 检查用户名是否存在
            cursor.execute("SELECT COUNT(*) FROM users WHERE username = %s", (username,))
            if cursor.fetchone()[0] > 0:
                QMessageBox.warning(self, "警告", "该用户名已存在！")
                return

            # 对密码进行加密
            hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

            # 插入新用户
            attar = 1 if is_admin else 2
            cursor.execute(
                "INSERT INTO users (username, password, ATTAR, Mail) VALUES (%s, %s, %s, %s)",
                (username, hashed.decode('utf-8'), attar, email)
            )
            conn.commit()

            QMessageBox.information(self, "成功", "注册成功！")
            self.close()

        except Exception as e:
            QMessageBox.critical(self, "错误", f"注册失败: {e}")
        finally:
            close_connection(conn, cursor)
