from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QMessageBox
)
from PyQt5.QtCore import Qt
from db import get_connection, close_connection
import bcrypt

class ResetPasswordDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("重置密码")
        self.setFixedSize(400, 250)

        layout = QVBoxLayout()
        layout.setSpacing(20)

        # 账号输入
        username_layout = QHBoxLayout()
        username_label = QLabel("账号:")
        self.username_input = QLineEdit()
        username_layout.addWidget(username_label)
        username_layout.addWidget(self.username_input)
        layout.addLayout(username_layout)

        # 邮箱输入
        email_layout = QHBoxLayout()
        email_label = QLabel("邮箱:")
        self.email_input = QLineEdit()
        email_layout.addWidget(email_label)
        email_layout.addWidget(self.email_input)
        layout.addLayout(email_layout)

        # 新密码输入
        password_layout = QHBoxLayout()
        password_label = QLabel("新密码:")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        password_layout.addWidget(password_label)
        password_layout.addWidget(self.password_input)
        layout.addLayout(password_layout)

        # 确认密码输入
        confirm_layout = QHBoxLayout()
        confirm_label = QLabel("确认密码:")
        self.confirm_input = QLineEdit()
        self.confirm_input.setEchoMode(QLineEdit.Password)
        confirm_layout.addWidget(confirm_label)
        confirm_layout.addWidget(self.confirm_input)
        layout.addLayout(confirm_layout)

        # 按钮
        button_layout = QHBoxLayout()
        reset_button = QPushButton("重置密码")
        cancel_button = QPushButton("取消")
        reset_button.clicked.connect(self.reset_password)
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(reset_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def reset_password(self):
        username = self.username_input.text()
        email = self.email_input.text()
        password = self.password_input.text()
        confirm = self.confirm_input.text()

        if not all([username, email, password, confirm]):
            QMessageBox.warning(self, "警告", "请填写所有字段！")
            return

        if password != confirm:
            QMessageBox.warning(self, "警告", "两次输入的密码不一致！")
            return

        try:
            conn = get_connection()
            if not conn:
                return
            cursor = conn.cursor()

            # 验证用户名和邮箱是否匹配
            cursor.execute(
                "SELECT COUNT(*) FROM users WHERE username = %s AND Mail = %s",
                (username, email)
            )
            if cursor.fetchone()[0] == 0:
                QMessageBox.warning(self, "警告", "账号或邮箱不正确！")
                return

            # 更新密码
            hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            cursor.execute(
                "UPDATE users SET password = %s WHERE username = %s AND Mail = %s",
                (hashed.decode('utf-8'), username, email)
            )
            conn.commit()

            QMessageBox.information(self, "成功", "密码重置成功！")
            self.accept()

        except Exception as e:
            QMessageBox.critical(self, "错误", f"重置密码失败: {e}")
        finally:
            close_connection(conn, cursor) 