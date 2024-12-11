# main.py
from PyQt5.QtWidgets import QApplication
from login import LoginWindow
import sys

def main():
    try:
        app = QApplication(sys.argv)
        window = LoginWindow()
        window.show()
        sys.exit(app.exec_())
    except Exception as e:
        print(f"Application failed to start: {e}")

if __name__ == '__main__':
    main()
