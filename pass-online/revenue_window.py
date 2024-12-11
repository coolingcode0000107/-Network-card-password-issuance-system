from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QLabel, QMessageBox, QPushButton
)
from PyQt5.QtCore import Qt
from db import get_product_revenue, clear_product_revenue

class RevenueWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("商品收益")
        self.setGeometry(100, 100, 300, 200)  # 稍微增加高度以容纳按钮
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # 创建标签显示总收益
        title_label = QLabel("总收益")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title_label)
        
        self.revenue_label = QLabel()
        self.revenue_label.setAlignment(Qt.AlignCenter)
        self.revenue_label.setStyleSheet("font-size: 24px; color: #2ecc71;")
        layout.addWidget(self.revenue_label)
        
        # 添加清空按钮
        clear_button = QPushButton("清空收益记录")
        clear_button.clicked.connect(self.clear_revenue)
        clear_button.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                padding: 5px;
                border: none;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        layout.addWidget(clear_button)
        
        self.load_revenue()
    
    def clear_revenue(self):
        """清空收益记录"""
        try:
            reply = QMessageBox.question(
                self,
                "确认清空",
                "确定要清空所有商品的收益记录吗？\n此操作不可恢复！",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                if clear_product_revenue():
                    QMessageBox.information(self, "成功", "已清空所有商品的收益记录！")
                    self.load_revenue()  # 刷新显示
                else:
                    QMessageBox.warning(self, "失败", "清空收益记录失败！")
                    
        except Exception as e:
            QMessageBox.critical(self, "错误", f"清空收益记录失败: {e}")
    
    def load_revenue(self):
        try:
            total_revenue = get_product_revenue()
            self.revenue_label.setText(f"￥{float(total_revenue):.2f}")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"加载收益数据失败: {e}") 