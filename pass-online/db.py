# db.py
import mysql.connector
from mysql.connector import Error
from PyQt5.QtWidgets import QMessageBox
import random
import string
from datetime import datetime
import uuid

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
    """关闭数据库连接和游标"""
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
    """获取所有用户信息（不包括密码）"""
    try:
        conn = get_connection()
        if not conn:
            return []
        cursor = conn.cursor()
        # 添加Mail字段到查询中
        cursor.execute("SELECT id, username, attar, password, Mail FROM users")
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
            SELECT buyer_name, purchase_time, product_name, code, 
                   activation_status, transaction_amount 
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
            # 
            cursor.execute(
                "INSERT INTO products (name, price, quantity) VALUES (%s, %s, %s)",
                (name, price, quantity)
            )
            
            # 生成并插入卡密
            for _ in range(quantity):
                while True:
                    code = generate_card_code()
                    # 检查卡密是否已存在
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
    """仅添加商品（原add_product函"""
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
        QMessageBox.critical(None, "错误", f"添加商品失败: {err}")
        return False
    finally:
        close_connection(conn, cursor)

def update_product(name, price, quantity):
    """更新商品信息"""
    conn = None
    cursor = None
    try:
        conn = get_connection()
        if not conn:
            return False
        cursor = conn.cursor()
        
        # 开始事务
        conn.start_transaction()
        
        try:
            # 更新商品信息
            cursor.execute(
                "UPDATE products SET price = %s, quantity = %s WHERE name = %s",
                (price, quantity, name)
            )
            
            if cursor.rowcount == 0:
                conn.rollback()
                QMessageBox.warning(None, "警告", f"没有找到商品: {name}")
                return False
                
            conn.commit()
            return True
            
        except Exception as e:
            if conn:
                conn.rollback()
            raise e
            
    except Error as err:
        QMessageBox.critical(None, "错误", f"更新商品失败: {err}")
        return False
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

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
            SELECT buyer_name, purchase_time, product_name, code, 
                   activation_status, transaction_amount 
            FROM orders 
            WHERE buyer_name = %s
            ORDER BY purchase_time DESC
        """, (username,))
        return cursor.fetchall()
    except Error as err:
        QMessageBox.critical(None, "错误", f"获取用户订单失败: {err}")
        return []
    finally:
        close_connection(conn, cursor)

def purchase_product(username, product_name, quantity, total_price):
    """购买商品"""
    try:
        conn = get_connection()
        if not conn:
            return False, "数据库连接失败"
        cursor = conn.cursor()
        
        # 开始事务
        conn.start_transaction()
        
        try:
            # 检查商品是否存在且库存充足
            cursor.execute(
                "SELECT quantity FROM products WHERE name = %s",
                (product_name,)
            )
            result = cursor.fetchone()
            if not result:
                return False, "商品不存在"
            if result[0] < quantity:
                return False, "库存不足"
            
            # 检查用户余额是否充足
            cursor.execute("""
                SELECT balance_amount 
                FROM balance 
                WHERE user_id = (SELECT id FROM users WHERE username = %s)
            """, (username,))
            balance = cursor.fetchone()
            if not balance:
                return False, "用户余额不存在"
            if balance[0] < total_price:
                return False, "余额不足"
            
            # 获取卡密
            cursor.execute("""
                SELECT CODE 
                FROM card_code 
                WHERE NAME = %s 
                LIMIT %s
            """, (product_name, quantity))
            codes = cursor.fetchall()
            if len(codes) < quantity:
                return False, "卡密库存不足"
            
            # 计算每个卡密的单价（总价除以数量）
            unit_price = total_price / quantity
            
            # 扣除用户余额
            cursor.execute("""
                UPDATE balance 
                SET balance_amount = balance_amount - %s 
                WHERE user_id = (SELECT id FROM users WHERE username = %s)
            """, (total_price, username))
            
            # 更新商品库存
            cursor.execute("""
                UPDATE products 
                SET quantity = quantity - %s 
                WHERE name = %s
            """, (quantity, product_name))
            
            # 创建订单并删除已使用的卡密
            code_list = []
            for code in codes:
                code_value = code[0]
                code_list.append(code_value)
                
                # 创建订单记录，包含实际交易金额
                cursor.execute("""
                    INSERT INTO orders (
                        buyer_name, purchase_time, product_name, 
                        code, activation_status, transaction_amount
                    ) VALUES (%s, NOW(), %s, %s, '未激活', %s)
                """, (username, product_name, code_value, unit_price))
                
                # 删除已使用的卡密
                cursor.execute("""
                    DELETE FROM card_code 
                    WHERE NAME = %s AND CODE = %s
                """, (product_name, code_value))
            
            # 更新商品收益
            update_product_revenue(product_name, total_price)
            
            conn.commit()
            return True, f"购买成功！\n卡密：{'，'.join(code_list)}"
            
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

def get_order_amount(code):
    """获取订单的实际交易金额"""
    try:
        conn = get_connection()
        if not conn:
            return None
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT transaction_amount 
            FROM orders 
            WHERE code = %s
        """, (code,))
        
        result = cursor.fetchone()
        return result[0] if result else None
        
    except Error as err:
        print(f"获取订单金额失败: {err}")
        return None
    finally:
        close_connection(conn, cursor)

def submit_refund_request(username, product_name, code):
    """提交退款申请"""
    try:
        conn = get_connection()
        if not conn:
            return False, "数据库连接失败"
        cursor = conn.cursor()
        
        # 开始事务
        conn.start_transaction()
        
        try:
            # 获取订单的实际交易金额
            cursor.execute("""
                SELECT transaction_amount 
                FROM orders 
                WHERE code = %s AND buyer_name = %s
            """, (code, username))
            
            result = cursor.fetchone()
            if not result:
                return False, "未找到对应的订单"
                
            refund_amount = result[0]
            
            # 插入退款申请
            cursor.execute("""
                INSERT INTO refunds (
                    username, product_name, refund_code, 
                    refund_amount, status
                ) VALUES (%s, %s, %s, %s, '待处理')
            """, (username, product_name, code, refund_amount))
            
            # 更新订单状态
            cursor.execute("""
                UPDATE orders 
                SET activation_status = '失效' 
                WHERE code = %s
            """, (code,))
            
            conn.commit()
            return True, "退款申请提交成功"
            
        except Exception as e:
            conn.rollback()
            raise e
            
    except Error as err:
        return False, f"提交退款申请失败: {err}"
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
        
        # 如果用户没有余额记录，创建个
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
                # 建新的余额记录
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
            ORDER BY status = '待处理' DESC, refund_code DESC
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

def process_refund(refund_code, status):
    """处理退款申请"""
    try:
        conn = get_connection()
        if not conn:
            return False
        cursor = conn.cursor()
        
        # 开始事务
        conn.start_transaction()
        
        try:
            # 获取退款申请信息
            cursor.execute("""
                SELECT username, product_name, refund_amount 
                FROM refunds 
                WHERE refund_code = %s AND status = '待处理'
            """, (refund_code,))
            
            result = cursor.fetchone()
            if not result:
                conn.rollback()
                return False
                
            username, product_name, refund_amount = result
            
            # 更退款状态
            cursor.execute("""
                UPDATE refunds 
                SET status = %s 
                WHERE refund_code = %s AND status = '待处理'
            """, (status, refund_code))
            cursor.fetchall()  # 清除未读结果
            
            if status == '已同意':
                # 获取用户ID
                cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
                user_result = cursor.fetchone()
                if not user_result:
                    conn.rollback()
                    return False
                
                user_id = user_result[0]
                
                # 退还用户余额
                cursor.execute("""
                    UPDATE balance 
                    SET balance_amount = balance_amount + %s 
                    WHERE user_id = %s
                """, (refund_amount, user_id))
                cursor.fetchall()  # 清除未读结果
                
                # 更新商品收益（减去退款金额）
                cursor.execute("""
                    SELECT total_revenue 
                    FROM product_revenue 
                    WHERE product_name = %s
                """, (product_name,))
                revenue_result = cursor.fetchone()
                if revenue_result:
                    new_revenue = float(revenue_result[0]) - float(refund_amount)
                    cursor.execute("""
                        UPDATE product_revenue 
                        SET total_revenue = %s 
                        WHERE product_name = %s
                    """, (new_revenue, product_name))
                    cursor.fetchall()  # 清除未读结果
                
                # 更新订单状态
                cursor.execute("""
                    UPDATE orders 
                    SET activation_status = '失效' 
                    WHERE code = %s
                """, (refund_code,))
                cursor.fetchall()  # 清除未读结果
            
            conn.commit()
            return True
            
        except Exception as e:
            conn.rollback()
            raise e
            
    except Error as err:
        print(f"处理退款申请失败: {err}")
        return False
    finally:
        close_connection(conn, cursor)

def delete_user(username):
    """删除用户及其所有相关数据"""
    try:
        conn = get_connection()
        if not conn:
            return False
        cursor = conn.cursor()
        
        # 开始事务
        conn.start_transaction()
        
        try:
            # 取用户ID
            cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
            result = cursor.fetchone()
            if not result:
                return False
            user_id = result[0]
            
            # 删除用户的签到记录
            cursor.execute("""
                DELETE FROM sign_in_records 
                WHERE user_id = %s
            """, (user_id,))
            cursor.fetchall()  # 清除未读结果
            
            # 删除用户的额记录
            cursor.execute("""
                DELETE FROM balance 
                WHERE user_id = %s
            """, (user_id,))
            cursor.fetchall()  # 清除未读结果
            
            # 删除用户的退款记录
            cursor.execute("""
                DELETE FROM refunds 
                WHERE username = %s
            """, (username,))
            cursor.fetchall()  # 清除未读结果
            
            # 删除用户的订单记录
            cursor.execute("""
                DELETE FROM orders 
                WHERE buyer_name = %s
            """, (username,))
            cursor.fetchall()  # 清除未读结果
            
            # 删除用户的VIP等级记录
            cursor.execute("""
                DELETE FROM userlevels 
                WHERE Username = %s
            """, (username,))
            cursor.fetchall()  # 清除未读结果
            
            # 最后删除用户记录
            cursor.execute("""
                DELETE FROM users 
                WHERE id = %s
            """, (user_id,))
            cursor.fetchall()  # 清除未读结果
            
            # 提交事务
            conn.commit()
            return True
            
        except Exception as e:
            # 发生错误时回滚事务
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
        QMessageBox.critical(None, "错误", f"获取退款记录失: {err}")
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
                return False, "今天已签到过了"
            
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

def get_user_vip_info():
    """获取所有用户的VIP等级信息"""
    try:
        conn = get_connection()
        if not conn:
            return []
        cursor = conn.cursor()
        cursor.execute("""
            SELECT Username, CumulativeRecharge, VIPLevel 
            FROM userlevels 
            ORDER BY CumulativeRecharge DESC
        """)
        return cursor.fetchall()
    except Error as err:
        QMessageBox.critical(None, "错误", f"获取用户VIP信息失败: {err}")
        return []
    finally:
        close_connection(conn, cursor)

def get_user_discount(username):
    """获取用户的折扣率"""
    try:
        conn = get_connection()
        if not conn:
            return 1.0
        cursor = conn.cursor()
        
        cursor.execute("SELECT VIPLevel FROM userlevels WHERE Username = %s", (username,))
        result = cursor.fetchone()
        
        if not result:
            return 1.0
            
        vip_level = result[0]
        # 根据VIP等级返回对应折扣
        discounts = {
            0: 1.00,  # 不打折
            1: 0.95,  # 95折
            2: 0.93,  # 93折
            3: 0.91,  # 91折
            4: 0.88,  # 88折
            5: 0.85   # 85折
        }
        return discounts.get(vip_level, 1.0)
        
    except Error as err:
        print(f"获取用户折扣失败: {err}")
        return 1.0
    finally:
        close_connection(conn, cursor)

def update_user_vip_level(username, recharge_amount):
    """更新用户VIP等级"""
    try:
        conn = get_connection()
        if not conn:
            return False
        cursor = conn.cursor()
        
        # 开始事务
        conn.start_transaction()
        
        try:
            # 获���当前累计充值金额
            cursor.execute(
                "SELECT CumulativeRecharge FROM userlevels WHERE Username = %s", 
                (username,)
            )
            result = cursor.fetchone()
            
            if result:
                # 更新现有记录
                new_total = float(result[0]) + float(recharge_amount)
                new_level = calculate_vip_level(new_total)
                
                cursor.execute("""
                    UPDATE userlevels 
                    SET CumulativeRecharge = %s, VIPLevel = %s 
                    WHERE Username = %s
                """, (new_total, new_level, username))
            else:
                # 创建新记录
                new_level = calculate_vip_level(float(recharge_amount))
                cursor.execute("""
                    INSERT INTO userlevels (Username, CumulativeRecharge, VIPLevel)
                    VALUES (%s, %s, %s)
                """, (username, recharge_amount, new_level))
            
            conn.commit()
            return True
            
        except Exception as e:
            conn.rollback()
            raise e
            
    except Error as err:
        QMessageBox.critical(None, "错误", f"更新VIP等级失败: {err}")
        return False
    finally:
        close_connection(conn, cursor)

def calculate_vip_level(total_recharge):
    """根据累计充值金额计算VIP等级"""
    if total_recharge <= 300:
        return 0  # VIP 0
    elif total_recharge <= 500:
        return 1  # VIP 1
    elif total_recharge <= 1000:
        return 2  # VIP 2
    elif total_recharge <= 1600:
        return 3  # VIP 3
    elif total_recharge <= 2500:
        return 4  # VIP 4
    else:
        return 5  # VIP 5

def get_product_revenue():
    """获取所有商品的总收益"""
    try:
        conn = get_connection()
        if not conn:
            return 0.0
        cursor = conn.cursor()
        
        # 检查表是否存在，如果不存在则创建
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS product_revenue (
                product_name VARCHAR(255) NOT NULL,
                total_revenue DECIMAL(10,2) NOT NULL DEFAULT 0.00,
                PRIMARY KEY (product_name)
            )
        """)
        
        # 计算总收益
        cursor.execute("""
            SELECT SUM(total_revenue) 
            FROM product_revenue
        """)
        result = cursor.fetchone()
        return result[0] if result[0] else 0.0
    except Error as err:
        QMessageBox.critical(None, "错误", f"获取商品收益失败: {err}")
        return 0.0
    finally:
        close_connection(conn, cursor)

def update_product_revenue(product_name, amount, is_refund=False):
    """更新商品收益
    amount: 金额
    is_refund: 是否是退款
    """
    try:
        conn = get_connection()
        if not conn:
            return False
        cursor = conn.cursor()
        
        # 开始事务
        conn.start_transaction()
        
        try:
            # 检查表是否存在，如果不存在则创建
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS product_revenue (
                    product_name VARCHAR(255) NOT NULL,
                    total_revenue DECIMAL(10,2) NOT NULL DEFAULT 0.00,
                    PRIMARY KEY (product_name)
                )
            """)
            
            # 检查商品是否已有收益记录
            cursor.execute(
                "SELECT total_revenue FROM product_revenue WHERE product_name = %s",
                (product_name,)
            )
            result = cursor.fetchone()
            
            if result:
                # 更新现记录
                new_revenue = float(result[0]) - amount if is_refund else float(result[0]) + amount
                cursor.execute("""
                    UPDATE product_revenue 
                    SET total_revenue = %s 
                    WHERE product_name = %s
                """, (new_revenue, product_name))
            else:
                # 创建新记录
                cursor.execute("""
                    INSERT INTO product_revenue (product_name, total_revenue)
                    VALUES (%s, %s)
                """, (product_name, amount))
            
            conn.commit()
            return True
            
        except Exception as e:
            conn.rollback()
            raise e
            
    except Error as err:
        print(f"更新商品收益失败: {err}")
        return False
    finally:
        close_connection(conn, cursor)

def get_refund_status(username):
    """获取用户的退款申请状态"""
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
        QMessageBox.critical(None, "错误", f"获取退款状态失败: {err}")
        return []
    finally:
        close_connection(conn, cursor)

def get_user_vip_info_by_username(username):
    """获取指定用户的VIP等级信息"""
    try:
        conn = get_connection()
        if not conn:
            return None
        cursor = conn.cursor()
        cursor.execute("""
            SELECT CumulativeRecharge, VIPLevel 
            FROM userlevels 
            WHERE Username = %s
        """, (username,))
        result = cursor.fetchone()
        return result if result else (0.0, 0)  # 如果没有记录，返回默认值
    except Error as err:
        QMessageBox.critical(None, "错误", f"获取用户VIP信息失败: {err}")
        return None
    finally:
        close_connection(conn, cursor)

def get_vip_benefits(vip_level):
    """获取VIP等级对应的权益"""
    benefits = {
        0: {
            "折扣优惠": "无折扣",
            "每日签到": "1元",
            "客服支持": "普通支持"
        },
        1: {
            "折扣优惠": "95折",
            "每日签到": "1元",
            "客服支持": "优先支持"
        },
        2: {
            "折扣优惠": "93折",
            "每日签到": "1元",
            "客服支持": "优先支持"
        },
        3: {
            "折扣优惠": "91折",
            "每日签���": "1元",
            "客服支持": "VIP专属支持"
        },
        4: {
            "折扣优惠": "88折",
            "每日签到": "1元",
            "客服支持": "VIP专属支持"
        },
        5: {
            "折扣优惠": "85折",
            "每日签到": "1元",
            "客服支持": "至尊VIP专属支持"
        }
    }
    return benefits.get(vip_level, benefits[0])

def generate_unique_code():
    """生成唯一的卡密码"""
    return str(uuid.uuid4())

def clear_product_revenue():
    """清空所有商品的收益记录"""
    try:
        conn = get_connection()
        if not conn:
            return False
        cursor = conn.cursor()
        
        try:
            # 开始事务
            conn.start_transaction()
            
            # 清空所有商品收益
            cursor.execute("UPDATE product_revenue SET total_revenue = 0.00")
            
            conn.commit()
            return True
            
        except Exception as e:
            conn.rollback()
            raise e
            
    except Error as err:
        QMessageBox.critical(None, "错误", f"清空商品收益失败: {err}")
        return False
    finally:
        close_connection(conn, cursor)
