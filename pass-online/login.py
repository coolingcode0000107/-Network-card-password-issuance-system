import mysql.connector
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout,
    QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QRadioButton, QButtonGroup, QMessageBox
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from register import RegisterDialog
from db import get_connection, close_connection
from utils import check_password, log_info, log_error
from product_management import ProductManagement  # 导入商品管理界面
from user_main_window import UserMainWindow  # 修改这行，使用正确的文件名


class LoginWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('卡密系统登录')
        self.setFixedSize(600, 400)

        # 创建主窗口部件和布局
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(20)

        # 创建顶部布局（用于放置帮助按钮和标题）
        top_layout = QHBoxLayout()

        # 添加帮助按钮
        help_button = QPushButton("?")
        help_button.setFixedSize(30, 30)  # 设置按钮大小
        help_button.setFont(QFont("Arial", 12, QFont.Bold))
        help_button.clicked.connect(self.show_help)
        help_button.setStyleSheet("""
            QPushButton {
                border-radius: 15px;
                background-color: #4a90e2;
                color: white;
            }
            QPushButton:hover {
                background-color: #357abd;
            }
        """)
        top_layout.addWidget(help_button)

        # 添加标题标签
        title_label = QLabel("卡密购买系统登录")
        title_label.setAlignment(Qt.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(20)
        title_font.setBold(True)
        title_label.setFont(title_font)
        top_layout.addWidget(title_label)

        # 添加一个空的弹性空间，使帮助按钮靠左，标题居中
        top_layout.addSpacing(30)

        # 将顶部布局添加到主布局
        layout.addLayout(top_layout)

        # 设置默认字体
        self.default_font = QFont()
        self.default_font.setPointSize(12)

        # 添加各个控件
        layout.addStretch(1)
        layout.addLayout(self.create_input_layout('账号:', self.default_font))
        layout.addLayout(self.create_input_layout('密码:', self.default_font, True))
        layout.addLayout(self.create_identity_layout())
        layout.addLayout(self.create_button_layout())
        layout.addStretch(1)
        layout.setContentsMargins(50, 20, 50, 20)

    def create_input_layout(self, label_text, font, is_password=False):
        layout = QHBoxLayout()
        label = QLabel(label_text)
        label.setFont(font)
        input_field = QLineEdit()
        input_field.setFont(font)
        input_field.setMinimumHeight(40)
        if is_password:
            input_field.setEchoMode(QLineEdit.Password)
            self.password_input = input_field
        else:
            self.account_input = input_field
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
        return layout

    def create_button_layout(self):
        layout = QHBoxLayout()
        layout.setSpacing(20)

        # 创建按钮字典
        buttons = {
            '登录': self.login,
            '注册': self.register,
            '忘记密码': self.forgot_password,
            '退出': self.close
        }

        for text, slot in buttons.items():
            btn = QPushButton(text)
            btn.setFont(self.default_font)
            btn.setMinimumHeight(40)
            btn.setMinimumWidth(120)
            btn.clicked.connect(slot)
            layout.addWidget(btn)

        return layout

    def login(self):
        cursor = None
        conn = None
        try:
            print("开始登录流程")  # 调试信息
            self.username = self.account_input.text()
            password = self.password_input.text()
            is_admin = self.admin_radio.isChecked()
            
            print(f"用户名: {self.username}, 是否管理员: {is_admin}")  # 调试信息

            # 检查用户名和密码是否为空
            if not self.username or not password:
                QMessageBox.warning(self, "警告", "请输入账号和密码！")
                return

            print("尝试连接数据库...")  # 调试信息
            # 获取数据库连接
            try:
                conn = get_connection()
                if not conn:
                    QMessageBox.critical(self, "错误", "无法连接到数据库！")
                    return
                print("数据库连接成功")  # 调试信息
            except Exception as db_err:
                print(f"数据库连接失败: {str(db_err)}")  # 调试信息
                QMessageBox.critical(self, "数据库错误", f"连接数据库失败: {str(db_err)}")
                return

            try:
                cursor = conn.cursor()
                print("游标创建成功")  # 调试信息

                # 验证用户身份
                print(f"执行SQL查询: SELECT password, attar FROM users WHERE username = {self.username}")  # 调试信息
                cursor.execute("SELECT password, attar FROM users WHERE username = %s", (self.username,))
                result = cursor.fetchone()
                print(f"查询结果: {result}")  # 调试信息

                if result:
                    stored_password, attar = result
                    print(f"查询到用户，权限级别: {attar}")  # 调试信息
                    
                    # 检查密码是否匹配
                    try:
                        password_match = check_password(password, stored_password.encode('utf-8'))
                        print(f"密码验证结果: {password_match}")  # 调试信息
                    except Exception as pwd_err:
                        print(f"密码验证失败: {str(pwd_err)}")  # 调试信息
                        raise pwd_err

                    if password_match:
                        if (is_admin and attar == 1) or (not is_admin and attar == 2):
                            print("密码验证成功，准备打开新窗口")  # 调试信息
                            QMessageBox.information(self, "成功", "登录成功！")
                            log_info(f"用户登录成功: {self.username}")
                            
                            # 在调用on_login_success之前确保数据库连接已关闭
                            if cursor:
                                cursor.close()
                            if conn:
                                conn.close()
                            
                            self.on_login_success()
                            return
                        else:
                            QMessageBox.warning(self, "失败", "用户身份不匹配！")
                            log_info(f"用户身份不匹配: {self.username}")
                    else:
                        QMessageBox.warning(self, "失败", "账号或密码错误！")
                        log_info(f"登录失败，密码错误: {self.username}")
                else:
                    QMessageBox.warning(self, "失败", "账号或密码错误！")
                    log_info(f"登录失败，用户名不存在: {self.username}")

            except Exception as query_err:
                print(f"数据库查询失败: {str(query_err)}")  # 调试信息
                raise query_err

        except Exception as e:
            print(f"登录过程发生异常: {str(e)}")  # 调试信息
            QMessageBox.critical(self, "未知错误", f"发生未知错误: {e}")
            log_error(f"未知错误: {e}")
        finally:
            print("执行清理操作...")  # 调试信息
            try:
                if cursor:
                    cursor.close()
                if conn:
                    conn.close()
                print("数据库连接已关闭")  # 调试信息
            except Exception as cleanup_err:
                print(f"清理过程发生错误: {str(cleanup_err)}")  # 调试信息

    def on_login_success(self):
        try:
            print(f"开始创建新窗口，用户类型: {'管理员' if self.admin_radio.isChecked() else '普通用户'}")  # 调试信息
            
            if self.admin_radio.isChecked():
                print("准备创建管理员窗口")  # 调试信息
                self.product_window = ProductManagement()
                if self.product_window is None:
                    raise ValueError("无法创建管理员窗口")
                self.product_window.show()
            else:
                print(f"准备创建用户窗口，用户名: {self.username}")  # 调试信息
                if not hasattr(self, 'username') or not self.username:
                    raise ValueError("用户名不能为空")
                self.user_window = UserMainWindow(self.username)
                if self.user_window is None:
                    raise ValueError("无法创建用户窗口")
                print("用户窗口创建成功，准备显示")  # 调试信息
                self.user_window.show()
            
            print("新窗口创建完成，准备关闭登录窗口")  # 调试信息
            # 延迟关闭登录窗口，确保新窗口已经完全创建
            from PyQt5.QtCore import QTimer
            QTimer.singleShot(100, self.close)
            
        except Exception as e:
            print(f"创建新窗口时发生异常: {str(e)}")  # 调试信息
            QMessageBox.critical(self, "错误", f"打开新窗口失败: {str(e)}")
            log_error(f"打开新窗口失败: {str(e)}")

    def register(self):
        try:
            dialog = RegisterDialog()
            dialog.exec_()
        except Exception as e:
            QMessageBox.critical(self, "错误", f"无法打开注册对话框: {e}")
            print(f"Error opening RegisterDialog: {e}")  # 打印到控制台

    def forgot_password(self):
        try:
            from reset_password_dialog import ResetPasswordDialog
            dialog = ResetPasswordDialog(self)
            dialog.exec_()
        except Exception as e:
            QMessageBox.critical(self, "错误", f"无法打开密码重置窗口: {e}")

    def show_help(self):
        QMessageBox.information(
            self,
            "关于系统",
            "本卡密系统由emmmm制作，界面清晰易懂，功能较为齐全，感谢您的支持与使用，有问题联系管理员",
            QMessageBox.Ok
        )
