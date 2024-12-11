# utils.py
import bcrypt
import logging

def hash_password(password):
    """哈希密码"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

def check_password(password, hashed):
    """检查密码是否匹配"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed)

# 配置日志记录
logging.basicConfig(
    filename='app.log',
    filemode='a',
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.DEBUG
)

def log_info(message):
    """记录信息日志"""
    logging.info(message)

def log_error(message):
    """记录错误日志"""
    logging.error(message)
