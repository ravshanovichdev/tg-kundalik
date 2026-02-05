import logging
import mysql.connector
from mysql.connector import Error
from data.config import mysqlHost, mysqlUser, mysqlPassword, mysqlDatabase

logger = logging.getLogger(__name__)

def getConnection():
    try:
        conn = mysql.connector.connect(
            host=mysqlHost,
            user=mysqlUser,
            password=mysqlPassword,
            database=mysqlDatabase
        )
        return conn
    except Error as error:
        logger.error("DB connection error: {}".format(error))
        return None

def initDb():
    conn = getConnection()
    if conn is None:
        return
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    userId BIGINT NOT NULL,
                    userName VARCHAR(255) NOT NULL,
                    fullName VARCHAR(255) DEFAULT NULL,
                    role VARCHAR(10) NOT NULL DEFAULT 'user',
                    joinDate DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    isBlocked TINYINT(1) NOT NULL DEFAULT '0',
                    UNIQUE KEY unique_user (userId)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
                """
            )
            conn.commit()
            logger.info("DB initialized")
    except Error as error:
        logger.error("DB init error: {}".format(error))
        conn.rollback()
    finally:
        conn.close()

class Users:
    @staticmethod
    def isUserExist(userId: int) -> bool:
        """Проверяет существование пользователя"""
        connect = getConnection()
        if connect is None:
            return False
        try:
            cursor = connect.cursor()
            cursor.execute("SELECT userId FROM users WHERE userId = %s", (userId,))
            return cursor.fetchone() is not None
        finally:
            connect.close()

    @staticmethod
    def addUser(userId: int, userName: str):
        """Добавляет нового пользователя"""
        connect = getConnection()
        if connect is None:
            return False
        try:
            cursor = connect.cursor()
            cursor.execute("INSERT INTO users (userId, userName) VALUES (%s, %s)", (userId, userName))
            connect.commit()
            return True
        except Error as error:
            logger.error(f"addUser error {userId}: {error}")
            return False
        finally:
            connect.close()

    @staticmethod
    def ensure_user(userId: int, userName: str):
        connect = getConnection()
        if connect is None:
            return False
        try:
            cursor = connect.cursor()
            cursor.execute("SELECT userId FROM users WHERE userId = %s", (userId,))
            if cursor.fetchone() is None:
                cursor.execute("INSERT INTO users (userId, userName) VALUES (%s, %s)", (userId, userName))
                connect.commit()
            return True
        except Error as error:
            logger.error(f"ensure_user error {userId}: {error}")
            return False
        finally:
            connect.close()

    @staticmethod
    def isBlocked(userId: int) -> bool:
        connect = getConnection()
        if connect is None:
            return False
        try:
            cursor = connect.cursor()
            cursor.execute("SELECT isBlocked FROM users WHERE userId = %s", (userId,))
            row = cursor.fetchone()
            return bool(row and row[0])
        finally:
            connect.close()

    @staticmethod
    def getAllUsers():
        """Получить всех пользователей"""
        connect = getConnection()
        if connect is None:
            return []
        try:
            cursor = connect.cursor(dictionary=True)
            cursor.execute("SELECT * FROM users ORDER BY joinDate DESC")
            return cursor.fetchall()
        finally:
            connect.close()

    @staticmethod
    def getUserById(userId: int):
        """Получить пользователя по ID"""
        connect = getConnection()
        if connect is None:
            return None
        try:
            cursor = connect.cursor(dictionary=True)
            cursor.execute("SELECT * FROM users WHERE userId = %s", (userId,))
            return cursor.fetchone()
        finally:
            connect.close()

    @staticmethod
    def blockUser(userId: int):
        """Заблокировать пользователя"""
        connect = getConnection()
        if connect is None:
            return False
        try:
            cursor = connect.cursor()
            cursor.execute("UPDATE users SET isBlocked = 1 WHERE userId = %s", (userId,))
            connect.commit()
            return cursor.rowcount > 0
        except Error as error:
            logger.error(f"Ошибка блокировки пользователя {userId}: {error}")
            return False
        finally:
            connect.close()

    @staticmethod
    def unblockUser(userId: int):
        """Разблокировать пользователя"""
        connect = getConnection()
        if connect is None:
            return False
        try:
            cursor = connect.cursor()
            cursor.execute("UPDATE users SET isBlocked = 0 WHERE userId = %s", (userId,))
            connect.commit()
            return cursor.rowcount > 0
        except Error as error:
            logger.error(f"Ошибка разблокировки пользователя {userId}: {error}")
            return False
        finally:
            connect.close()

    @staticmethod
    def deleteUser(userId: int):
        """Удалить пользователя"""
        connect = getConnection()
        if connect is None:
            return False
        try:
            cursor = connect.cursor()
            cursor.execute("DELETE FROM users WHERE userId = %s", (userId,))
            connect.commit()
            return cursor.rowcount > 0
        except Error as error:
            logger.error(f"Ошибка удаления пользователя {userId}: {error}")
            return False
        finally:
            connect.close()

    @staticmethod
    def getStats():
        """Получить статистику"""
        connect = getConnection()
        if connect is None:
            return {}
        try:
            cursor = connect.cursor()

            # Общее количество пользователей
            cursor.execute("SELECT COUNT(*) FROM users")
            total_users = cursor.fetchone()[0]

            # Заблокированные пользователи
            cursor.execute("SELECT COUNT(*) FROM users WHERE isBlocked = 1")
            blocked_users = cursor.fetchone()[0]

            # Администраторы
            cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'admin'")
            admins_count = cursor.fetchone()[0]

            # Новые пользователи за последние 7 дней
            cursor.execute("SELECT COUNT(*) FROM users WHERE joinDate >= DATE_SUB(NOW(), INTERVAL 7 DAY)")
            new_users_week = cursor.fetchone()[0]

            return {
                'total_users': total_users,
                'blocked_users': blocked_users,
                'admins_count': admins_count,
                'new_users_week': new_users_week
            }
        finally:
            connect.close()

