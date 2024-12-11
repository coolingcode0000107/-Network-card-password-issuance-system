from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QProgressBar, QFrame
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from db import get_user_vip_info_by_username, get_vip_benefits, get_user_discount

class VIPWindow(QMainWindow):
    def __init__(self, username):
        super().__init__()
        self.username = username
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("VIP等级")
        self.setGeometry(100, 100, 300, 200)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # 获取用户VIP信息
        vip_info = get_user_vip_info_by_username(self.username)
        if vip_info:
            total_recharge, current_level = vip_info
        else:
            total_recharge, current_level = 0.0, 0

        # VIP等级显示
        level_label = QLabel(f"当前等级: VIP {current_level}")
        level_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        level_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(level_label)

        # 累计充值显示
        recharge_label = QLabel(f"累计充值: ￥{total_recharge:.2f}")
        recharge_label.setStyleSheet("font-size: 18px;")
        recharge_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(recharge_label)

        # 获取折扣信息
        discount = get_user_discount(self.username)
        discount_text = f"{int(discount * 100)}折"
        if discount == 1.0:
            discount_text = "无折扣"

        # 当前折扣显示
        # discount_label = QLabel(f"当前享受: {discount_text}")
        # discount_label.setStyleSheet("font-size: 18px;")
        # discount_label.setAlignment(Qt.AlignCenter)
        # layout.addWidget(discount_label)

        # 进度条
        progress_frame = QFrame()
        progress_layout = QVBoxLayout(progress_frame)
        
        # 计算下一级所需金额
        next_level_thresholds = {
            0: 300,   # VIP 1 需要300
            1: 500,   # VIP 2 需要500
            2: 1000,  # VIP 3 需要1000
            3: 1600,  # VIP 4 需要1600
            4: 2500,  # VIP 5 需要2500
            5: 99999  # 最高等级
        }
        
        if current_level < 5:
            next_threshold = next_level_thresholds[current_level]
            progress = (total_recharge / next_threshold) * 100 if next_threshold > 0 else 100
            progress_label = QLabel(f"距离VIP{current_level + 1}还需充值：￥{next_threshold - total_recharge:.2f}")
        else:
            progress = 100
            progress_label = QLabel("已达到最高等级")
        
        progress_label.setAlignment(Qt.AlignCenter)
        progress_layout.addWidget(progress_label)
        
        progress_bar = QProgressBar()
        progress_bar.setMaximum(100)
        progress_bar.setValue(min(int(progress), 100))
        progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid grey;
                border-radius: 5px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #e74c3c;
                width: 10px;
            }
        """)
        progress_layout.addWidget(progress_bar)
        layout.addWidget(progress_frame)

        # 当前享受的权益
        benefits = get_vip_benefits(current_level)
        benefits_frame = QFrame()
        benefits_frame.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border-radius: 10px;
                padding: 10px;
            }
        """)
        benefits_layout = QVBoxLayout(benefits_frame)
        
        title = QLabel("当前享受的权益")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50;")
        title.setAlignment(Qt.AlignCenter)
        benefits_layout.addWidget(title)
        
        for benefit, value in benefits.items():
            benefit_label = QLabel(f"{benefit}：{value}")
            benefit_label.setStyleSheet("font-size: 16px; color: #34495e;")
            benefit_label.setAlignment(Qt.AlignCenter)
            benefits_layout.addWidget(benefit_label)
        
        layout.addWidget(benefits_frame)
        layout.addStretch() 