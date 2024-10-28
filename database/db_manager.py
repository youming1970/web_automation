import psycopg2
from psycopg2.extras import RealDictCursor

class DatabaseManager:
    def __init__(self):
        self.conn = psycopg2.connect(
            dbname="web_automation",
            user="poording",
            password="Ab.12345",
            host="localhost"
        )
        self.cur = self.conn.cursor(cursor_factory=RealDictCursor)

    def execute_query(self, query, params=None):
        """执行 SQL 查询"""
        try:
            self.cur.execute(query, params)
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            raise e

    def fetch_all(self, query, params=None):
        """获取所有查询结果"""
        self.cur.execute(query, params)
        return self.cur.fetchall()

    def fetch_one(self, query, params=None):
        """获取单个查询结果"""
        self.cur.execute(query, params)
        return self.cur.fetchone()

    def close(self):
        """关闭数据库连接"""
        self.cur.close()
        self.conn.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
