# db.py
import mysql.connector
from mysql.connector import Error
from PyQt5.QtWidgets import QMessageBox
import random
import string
from datetime import datetime

def get_connection():
    """创建并返回数据库连接"""
    try:
        print("尝试创建数据库连接...")  # 调试信息
        
        # 使用最基本的配置
        config = {
            'host': 'localhost',
            'user': 'root',
            'password': '123456',
            'database': 'data',
            'use_pure': True  # 使用纯Python实现
        }
        
        print("连接参数:", config)  # 调试信息
        
        # 直接尝试连接
        conn = mysql.connector.connect(**config)
        
        if conn and conn.is_connected():
            print("数据库连接创建成功")  # 调试信息
            return conn
        else:
            raise Exception("连接创建失败")
            
    except mysql.connector.Error as err:
        error_msg = str(err)
        print(f"MySQL错误: {error_msg}")  # 调试信息
        QMessageBox.critical(None, "数据库连接错误", f"无法连接到数据库: {error_msg}")
        return None
        
    except Exception as e:
        print(f"创建数据库连接时发生未知错误: {str(e)}")  # 调试信息
        QMessageBox.critical(None, "未知错误", f"创建数据库连接时发生错误: {e}")
        return None

def close_connection(conn, cursor):
    """关闭数据库连���和游标"""
    if cursor:
        cursor.close()
    if conn:
        conn.close()

def get_all_products():
    """获取所有商品"""
    try:
        conn = get_connection()
        if not conn:
            return []
        cursor = conn.cursor()
        cursor.execute("SELECT name, price, quantity FROM products")
        products = cursor.fetchall()
        return products
    except Error as err:
        QMessageBox.critical(None, "错误", f"获取商品数据失败: {err}")
        return []
    finally:
        close_connection(conn, cursor)

def get_all_users():
    """获取所有用户（不包括密码）"""
    try:
        conn = get_connection()
        if not conn:
            return []
        cursor = conn.cursor()
        # 仅选择id, username, attar，不包括password
        cursor.execute("SELECT id, username, attar FROM users")
        users = cursor.fetchall()
        return users
    except Error as err:
        QMessageBox.critical(None, "错误", f"获取用户数据失败: {err}")
        return []
    finally:
        close_connection(conn, cursor)


def get_all_orders():
    """获取所有订单"""
    try:
        conn = get_connection()
        if not conn:
            return []
        cursor = conn.cursor()
        cursor.execute("""
            SELECT buyer_name, purchase_time, product_name, code, activation_status 
            FROM orders
            ORDER BY purchase_time DESC
        """)
        orders = cursor.fetchall()
        return orders
    except Error as err:
        QMessageBox.critical(None, "错误", f"获取订单数据失败: {err}")
        return []
    finally:
        close_connection(conn, cursor)

def generate_card_code(length=10):
    """生成随机卡密"""
    # 生成包含1-9和大小写字母的字符集
    characters = string.digits[1:] + string.ascii_letters
    return ''.join(random.choice(characters) for _ in range(length))

def add_product_with_cards(name, price, quantity):
    """添加商品并生成卡密"""
    try:
        conn = get_connection()
        if not conn:
            return False
        cursor = conn.cursor()
        
        # 开始事务
        conn.start_transaction()
        
        try:
            # 添加商品
            cursor.execute(
                "INSERT INTO products (name, price, quantity) VALUES (%s, %s, %s)",
                (name, price, quantity)
            )
            
            # 生成并插入卡密
            for _ in range(quantity):
                while True:
                    code = generate_card_code()
                    # ���查卡密是否已存在
                    cursor.execute("SELECT COUNT(*) FROM card_code WHERE CODE = %s", (code,))
                    if cursor.fetchone()[0] == 0:
                        break
                
                cursor.execute(
                    "INSERT INTO card_code (NAME, CODE) VALUES (%s, %s)",
                    (name, code)
                )
            
            # 提交事务
            conn.commit()
            return True
            
        except Exception as e:
            # 发生错误时回滚事务
            conn.rollback()
            raise e
            
    except Exception as e:
        QMessageBox.critical(None, "错误", f"添加商品和卡密失败: {e}")
        return False
    finally:
        close_connection(conn, cursor)

# 修改原有的add_product函数名，避免冲突
def add_product_only(name, price, quantity):
    """仅添加商品（原add_product函数）"""
    try:
        conn = get_connection()
        if not conn:
            return False
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO products (name, price, quantity) VALUES (%s, %s, %s)",
            (name, price, quantity)
        )
        conn.commit()
        return True
    except Error as err:
        QMessageBox.critical(None, "错��", f"添加商品失败: {err}")
        return False
    finally:
        close_connection(conn, cursor)

def update_product(name, price, quantity):
    """更新商品信息"""
    try:
        conn = get_connection()
        if not conn:
            return False
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE products SET price = %s, quantity = %s WHERE name = %s",
            (price, quantity, name)
        )
        conn.commit()
        if cursor.rowcount == 0:
            QMessageBox.warning(None, "警告", f"没有找到商品: {name}")
            return False
        return True
    except Error as err:
        QMessageBox.critical(None, "错误", f"更新商品失败: {err}")
        return False
    finally:
        close_connection(conn, cursor)

def delete_product(name):
    """删除商品及其相关卡密"""
    try:
        conn = get_connection()
        if not conn:
            return False
        cursor = conn.cursor()
        
        # 开始事务
        conn.start_transaction()
        
        try:
            # 先删除相关的卡密
            cursor.execute("DELETE FROM card_code WHERE NAME = %s", (name,))
            
            # 再删除商品
            cursor.execute("DELETE FROM products WHERE name = %s", (name,))
            
            if cursor.rowcount == 0:
                conn.rollback()
                QMessageBox.warning(None, "警告", f"没有找到商品: {name}")
                return False
                
            # 提交事务
            conn.commit()
            return True
            
        except Exception as e:
            # 发生错误时回滚事务
            conn.rollback()
            raise e
            
    except Error as err:
        QMessageBox.critical(None, "错误", f"删除商品失败: {err}")
        return False
    finally:
        close_connection(conn, cursor)

def get_products_for_user():
    """获取商品列表（用户视图）"""
    try:
        conn = get_connection()
        if not conn:
            return []
        cursor = conn.cursor()
        cursor.execute("SELECT name, price, quantity FROM products WHERE quantity > 0")
        return cursor.fetchall()
    except Error as err:
        QMessageBox.critical(None, "错误", f"获取商品数据失败: {err}")
        return []
    finally:
        close_connection(conn, cursor)

def get_user_orders(username):
    """获取用户的订单"""
    try:
        conn = get_connection()
        if not conn:
            return []
        cursor = conn.cursor()
        cursor.execute("""
            SELECT purchase_time, product_name, code, activation_status 
            FROM orders 
            WHERE buyer_name = %s 
            ORDER BY purchase_time DESC
        """, (username,))
        return cursor.fetchall()
    except Error as err:
        QMessageBox.critical(None, "错误", f"获取订单数据失败: {err}")
        return []
    finally:
        close_connection(conn, cursor)

def purchase_product(username, product_name, quantity):
    """购买商品"""
    try:
        conn = get_connection()
        if not conn:
            return False, "数据库连接失败"
        cursor = conn.cursor()
        
        # 开始事务
        conn.start_transaction()
        
        try:
            # 检查商品库存
            cursor.execute("SELECT price, quantity FROM products WHERE name = %s", (product_name,))
            result = cursor.fetchone()
            if not result:
                conn.rollback()
                return False, "商品不存在"
                
            price, available_quantity = result
            if quantity > available_quantity:
                conn.rollback()
                return False, "库存不足"
                
            # 检查用户余额
            total_amount = price * quantity
            cursor.execute("SELECT balance_amount FROM balance WHERE user_id = (SELECT id FROM users WHERE username = %s)", (username,))
            balance_result = cursor.fetchone()
            if not balance_result or balance_result[0] < total_amount:
                conn.rollback()
                return False, "余额不足"
                
            # 获取卡密
            cursor.execute(
                "SELECT CODE FROM card_code WHERE NAME = %s LIMIT %s",
                (product_name, quantity)
            )
            codes = cursor.fetchall()
            if len(codes) < quantity:
                conn.rollback()
                return False, "卡密库存不足"
                
            # 更新商品库存
            cursor.execute(
                "UPDATE products SET quantity = quantity - %s WHERE name = %s",
                (quantity, product_name)
            )
            
            # 扣除用户余额
            cursor.execute(
                "UPDATE balance SET balance_amount = balance_amount - %s WHERE user_id = (SELECT id FROM users WHERE username = %s)",
                (total_amount, username)
            )
            
            # 创建订单记录
            for code in codes:
                cursor.execute("""
                    INSERT INTO orders (buyer_name, purchase_time, product_name, code, activation_status)
                    VALUES (%s, NOW(), %s, %s, '未激活')
                """, (username, product_name, code[0]))
                
                # 删除已使用的卡密
                cursor.execute("DELETE FROM card_code WHERE CODE = %s", (code[0],))
            
            conn.commit()
            return True, "购买成功"
            
        except Exception as e:
            conn.rollback()
            raise e
            
    except Error as err:
        return False, f"购买失败: {err}"
    finally:
        close_connection(conn, cursor)

def activate_code(username, code):
    """激活卡密"""
    try:
        conn = get_connection()
        if not conn:
            return False
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE orders 
            SET activation_status = '已激活' 
            WHERE buyer_name = %s AND code = %s AND activation_status = '未激活'
        """, (username, code))
        
        success = cursor.rowcount > 0
        conn.commit()
        return success
    except Error as err:
        QMessageBox.critical(None, "错误", f"激活卡密失败: {err}")
        return False
    finally:
        close_connection(conn, cursor)

def request_refund(username, product_name, code, refund_amount):
    """申请退款"""
    try:
        conn = get_connection()
        if not conn:
            return False, "数据库连接失败"
        cursor = conn.cursor()
        
        # 开始事务
        conn.start_transaction()
        
        try:
            # 检查订单状态
            cursor.execute("""
                SELECT activation_status 
                FROM orders 
                WHERE buyer_name = %s AND code = %s AND product_name = %s
            """, (username, code, product_name))
            
            result = cursor.fetchone()
            if not result or result[0] != '未激活':
                conn.rollback()
                return False, "只能对未激活的卡密申请退款"
            
            # 检查是否已经申请过退款
            cursor.execute("""
                SELECT COUNT(*) 
                FROM refunds 
                WHERE username = %s AND refund_code = %s
            """, (username, code))
            
            if cursor.fetchone()[0] > 0:
                conn.rollback()
                return False, "该卡密已申请过退款"
                
            # 创建退款申请
            cursor.execute("""
                INSERT INTO refunds (username, product_name, refund_code, refund_amount, status)
                VALUES (%s, %s, %s, %s, '待处理')
            """, (username, product_name, code, refund_amount))
            
            conn.commit()
            return True, "退款申请成功"
            
        except Exception as e:
            conn.rollback()
            raise e
            
    except Error as err:
        return False, f"申请退款失败: {err}"
    finally:
        close_connection(conn, cursor)

def get_user_balance(username):
    """获取用户余额"""
    try:
        conn = get_connection()
        if not conn:
            return 0
        cursor = conn.cursor()
        
        # 先获取用户ID
        cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
        user_result = cursor.fetchone()
        if not user_result:
            return 0
            
        user_id = user_result[0]
        
        # 获取余额
        cursor.execute("SELECT balance_amount FROM balance WHERE user_id = %s", (user_id,))
        result = cursor.fetchone()
        
        # 如果用户没有余额记录，创建一个
        if not result:
            cursor.execute(
                "INSERT INTO balance (user_id, balance_amount) VALUES (%s, 0.0)",
                (user_id,)
            )
            conn.commit()
            return 0.0
            
        return float(result[0]) if result else 0.0
    except Error as err:
        QMessageBox.critical(None, "错误", f"获取余额失败: {err}")
        return 0
    finally:
        close_connection(conn, cursor)

def add_balance(username, amount):
    """充值余额"""
    try:
        conn = get_connection()
        if not conn:
            return False
        cursor = conn.cursor()
        
        # 开始事务
        conn.start_transaction()
        
        try:
            # 获取用户ID
            cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
            user_result = cursor.fetchone()
            if not user_result:
                conn.rollback()
                return False
                
            user_id = user_result[0]
            
            # 检查是否存在余额记录
            cursor.execute("SELECT balance_amount FROM balance WHERE user_id = %s", (user_id,))
            balance_result = cursor.fetchone()
            
            if balance_result:
                # 更新现有余额
                cursor.execute("""
                    UPDATE balance 
                    SET balance_amount = balance_amount + %s 
                    WHERE user_id = %s
                """, (amount, user_id))
            else:
                # 创建新的余额记录
                cursor.execute("""
                    INSERT INTO balance (user_id, balance_amount) 
                    VALUES (%s, %s)
                """, (user_id, amount))
            
            conn.commit()
            return True
            
        except Exception as e:
            conn.rollback()
            raise e
            
    except Error as err:
        QMessageBox.critical(None, "错误", f"充值失败: {err}")
        return False
    finally:
        close_connection(conn, cursor)

def get_product_price(product_name):
    """获取商品价格"""
    try:
        conn = get_connection()
        if not conn:
            return None
        cursor = conn.cursor()
        cursor.execute("SELECT price FROM products WHERE name = %s", (product_name,))
        result = cursor.fetchone()
        return result[0] if result else None
    except Error as err:
        QMessageBox.critical(None, "错误", f"获取商品价格失败: {err}")
        return None
    finally:
        close_connection(conn, cursor)

def get_all_refunds():
    """获取所有退款申请"""
    try:
        conn = get_connection()
        if not conn:
            return []
        cursor = conn.cursor()
        cursor.execute("""
            SELECT username, product_name, refund_code, refund_amount, status 
            FROM refunds 
            ORDER BY status = '待处理' DESC
        """)
        return cursor.fetchall()
    except Error as err:
        QMessageBox.critical(None, "错误", f"获取退款申请失败: {err}")
        return []
    finally:
        close_connection(conn, cursor)

def clear_processed_refunds():
    """清理已处理的退款记录"""
    try:
        conn = get_connection()
        if not conn:
            return False
        cursor = conn.cursor()
        
        cursor.execute(
            "DELETE FROM refunds WHERE status != '待处理'"
        )
        
        conn.commit()
        return True
    except Error as err:
        QMessageBox.critical(None, "错误", f"清理退款记录失败: {err}")
        return False
    finally:
        close_connection(conn, cursor)

def process_refund(username, code, approve, amount):
    """处理退款申请"""
    try:
        conn = get_connection()
        if not conn:
            return False
        cursor = conn.cursor()
        
        # 开始事务
        conn.start_transaction()
        
        try:
            # 更新退款状态
            new_status = '已同意' if approve else '已拒绝'
            cursor.execute("""
                UPDATE refunds 
                SET status = %s 
                WHERE username = %s AND refund_code = %s AND status = '待处理'
            """, (new_status, username, code))
            
            if cursor.rowcount == 0:
                conn.rollback()
                return False
            
            # 如果同意退款，更新用户余额
            if approve:
                cursor.execute("""
                    UPDATE balance 
                    SET balance_amount = balance_amount + %s 
                    WHERE user_id = (SELECT id FROM users WHERE username = %s)
                """, (amount, username))
                
                # 更新订单状态为"已退款"
                cursor.execute("""
                    UPDATE orders 
                    SET activation_status = '失效' 
                    WHERE buyer_name = %s AND code = %s
                """, (username, code))
            
            conn.commit()
            return True
            
        except Exception as e:
            conn.rollback()
            raise e
            
    except Error as err:
        QMessageBox.critical(None, "错误", f"处理退款申请失败: {err}")
        return False
    finally:
        close_connection(conn, cursor)

def delete_user(username):
    """删除用���及其所有相关数据"""
    try:
        conn = get_connection()
        if not conn:
            return False
        cursor = conn.cursor()
        
        # 开始事务
        conn.start_transaction()
        
        try:
            # 删除用户的退款申请记录
            cursor.execute(
                "DELETE FROM refunds WHERE username = %s",
                (username,)
            )
            
            # 删除用户的订单记录
            cursor.execute(
                "DELETE FROM orders WHERE buyer_name = %s",
                (username,)
            )
            
            # 删除用户的余额记录
            cursor.execute("""
                DELETE FROM balance 
                WHERE user_id = (SELECT id FROM users WHERE username = %s)
            """, (username,))
            
            # 最后删除用户
            cursor.execute(
                "DELETE FROM users WHERE username = %s",
                (username,)
            )
            
            if cursor.rowcount == 0:
                conn.rollback()
                return False
                
            conn.commit()
            return True
            
        except Exception as e:
            conn.rollback()
            raise e
            
    except Error as err:
        QMessageBox.critical(None, "错误", f"删除用户失败: {err}")
        return False
    finally:
        close_connection(conn, cursor)

def update_user_attar(username, new_attar):
    """更新用户权限"""
    try:
        conn = get_connection()
        if not conn:
            return False
        cursor = conn.cursor()
        
        cursor.execute(
            "UPDATE users SET ATTAR = %s WHERE username = %s",
            (new_attar, username)
        )
        
        success = cursor.rowcount > 0
        conn.commit()
        return success
    except Error as err:
        QMessageBox.critical(None, "错误", f"更新用户权限失败: {err}")
        return False
    finally:
        close_connection(conn, cursor)

def get_user_refund_records(username):
    """获取用户的退款记录"""
    try:
        conn = get_connection()
        if not conn:
            return []
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT product_name, refund_code, refund_amount, status
            FROM refunds 
            WHERE username = %s 
            ORDER BY status = '待处理' DESC
        """, (username,))
        
        return cursor.fetchall()
    except Error as err:
        QMessageBox.critical(None, "错误", f"获取退款记录���败: {err}")
        return []
    finally:
        close_connection(conn, cursor)

def check_sign_in(user_id, current_date):
    """检查用户今天是否已经签到"""
    try:
        conn = get_connection()
        if not conn:
            return True  # 如果无法连接数据库,返回True防止重复签到
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT COUNT(*) 
            FROM sign_in_records 
            WHERE user_id = %s AND sign_date = %s
        """, (user_id, current_date))
        
        count = cursor.fetchone()[0]
        return count > 0
    except Error as err:
        print(f"检查签到记录失败: {err}")
        return True
    finally:
        close_connection(conn, cursor)

def add_sign_in_record(username):
    """添加签到记录并增加用户余额"""
    try:
        conn = get_connection()
        if not conn:
            return False, "数据库连接失败"
        cursor = conn.cursor()
        
        # 开始事务
        conn.start_transaction()
        
        try:
            # 获取用户ID
            cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
            result = cursor.fetchone()
            if not result:
                conn.rollback()
                return False, "用户不存在"
            
            user_id = result[0]
            current_date = datetime.now().date()
            
            # 检查是否已经签到
            if check_sign_in(user_id, current_date):
                conn.rollback()
                return False, "今天已经签到过了"
            
            # 添加签到记录
            cursor.execute("""
                INSERT INTO sign_in_records (user_id, sign_date)
                VALUES (%s, %s)
            """, (user_id, current_date))
            
            # 增加用户余额
            cursor.execute("""
                UPDATE balance 
                SET balance_amount = balance_amount + 1.00
                WHERE user_id = %s
            """, (user_id,))
            
            conn.commit()
            return True, "签到成功! 获得1元奖励"
            
        except Exception as e:
            conn.rollback()
            raise e
            
    except Error as err:
        return False, f"签到失败: {err}"
    finally:
        close_connection(conn, cursor)
