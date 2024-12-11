from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QLabel, 
    QProgressBar, QMessageBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from db import get_user_discount

class UserVIPWindow(QMainWindow):
    def __init__(self, username):
        super().__init__()
        self.username = username
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("我的VIP等级")
        self.setFixedSize(400, 300)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(20)

        try:
            from db import get_connection
            conn = get_connection()
            if not conn:
                return
            cursor = conn.cursor()
            
            # 获取用户VIP信息
            cursor.execute("""
                SELECT CumulativeRecharge, VIPLevel 
                FROM userlevels 
                WHERE Username = %s
            """, (self.username,))
            
            result = cursor.fetchone()
            if result:
                total_recharge, vip_level = result
            else:
                total_recharge, vip_level = 0, 1

            # VIP等级显示（修改显示文本）
            level_text = "普通用户" if vip_level == 0 else f"VIP {vip_level}"
            level_label = QLabel(f"当前等级：{level_text}")
            level_label.setAlignment(Qt.AlignCenter)
            font = level_label.font()
            font.setPointSize(16)
            font.setBold(True)
            level_label.setFont(font)
            layout.addWidget(level_label)

            # 累计充值显示
            recharge_label = QLabel(f"累计充值：￥{float(total_recharge):.2f}")
            recharge_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(recharge_label)

            # 当前折扣显示
            discount = get_user_discount(self.username)
            discount_text = "无折扣" if discount == 1.0 else f"{discount*100:.0f}折优惠"
            discount_label = QLabel(f"当前享受：{discount_text}")
            discount_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(discount_label)

            # 升级进度条
            progress_layout = QVBoxLayout()
            
            # 修改等级阈值
            level_thresholds = {
                0: 300,   # VIP 0 上限
                1: 500,   # VIP 1 上限
                2: 1000,  # VIP 2 上限
                3: 1600,  # VIP 3 上限
                4: 2500,  # VIP 4 上限
                5: float('inf')  # VIP 5 无上限
            }
            
            if vip_level < 5:
                next_threshold = level_thresholds[vip_level]
                current_threshold = level_thresholds[vip_level - 1] if vip_level > 0 else 0
                
                progress = ((total_recharge - current_threshold) / 
                          (next_threshold - current_threshold)) * 100
                
                next_level_text = f"VIP {vip_level + 1}"
                if vip_level == 0:
                    next_level_text = "VIP 1"
                
                progress_label = QLabel(
                    f"距离{next_level_text}还需充值：￥{next_threshold - total_recharge:.2f}"
                )
                progress_label.setAlignment(Qt.AlignCenter)
                progress_layout.addWidget(progress_label)
                
                progress_bar = QProgressBar()
                progress_bar.setMinimum(0)
                progress_bar.setMaximum(100)
                progress_bar.setValue(int(progress))
                progress_layout.addWidget(progress_bar)
            else:
                max_level_label = QLabel("恭喜！您已达到最高等级")
                max_level_label.setAlignment(Qt.AlignCenter)
                progress_layout.addWidget(max_level_label)
            
            layout.addLayout(progress_layout)

            # 修改等级说明文本
            info_label = QLabel(
                "VIP等级说明：\n"
                "普通用户 (0-300元)：无折扣\n"
                "VIP 1 (301-500元)：95折\n"
                "VIP 2 (501-1000元)：93折\n"
                "VIP 3 (1001-1600元)：91折\n"
                "VIP 4 (1601-2500元)：88折\n"
                "VIP 5 (2501元以上)：85折"
            )
            info_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(info_label)

        except Exception as e:
            QMessageBox.critical(self, "错误", f"获取VIP信息失败: {e}")
        finally:
            if 'conn' in locals() and conn:
                conn.close() 