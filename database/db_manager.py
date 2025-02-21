import asyncpg
import logging
from typing import Optional, List, Dict, Any, Tuple
from contextlib import asynccontextmanager

class DatabaseManager:
    def __init__(self):
        """初始化数据库管理器"""
        self.pool = None
        self.dsn = "postgresql://poording:Ab.12345@localhost/web_automation"
        
    async def connect(self):
        """创建数据库连接池"""
        if not self.pool:
            try:
                self.pool = await asyncpg.create_pool(
                    dsn=self.dsn,
                    min_size=1,
                    max_size=10
                )
                logging.info("数据库连接池创建成功")
            except Exception as e:
                logging.error(f"创建数据库连接池失败: {str(e)}")
                raise

    async def ensure_connected(self):
        """确保数据库已连接"""
        if not self.pool:
            await self.connect()

    async def execute_query(self, query: str, params: Optional[tuple] = None) -> str:
        """
        执行 SQL 查询
        
        :param query: SQL 查询语句
        :param params: 查询参数
        :return: 执行结果
        """
        await self.ensure_connected()
        async with self.pool.acquire() as conn:
            try:
                return await conn.execute(query, *params if params else [])
            except Exception as e:
                logging.error(f"执行查询失败: {str(e)}, Query: {query}, Params: {params}")
                raise

    @asynccontextmanager
    async def transaction(self):
        """获取事务上下文管理器"""
        conn = await self.pool.acquire()
        tr = conn.transaction()
        try:
            await tr.start()
            yield tr
            await tr.commit()
        except Exception:
            await tr.rollback()
            raise
        finally:
            await self.pool.release(conn)

    async def execute(self, query: str, params: Optional[Tuple] = None) -> None:
        """执行 SQL 语句"""
        try:
            async with self.pool.acquire() as conn:
                await conn.execute(query, *params if params else [])
        except Exception as e:
            logging.error(f"执行 SQL 失败: {e}, Query: {query}, Params: {params}")
            raise

    async def fetch_one(self, query: str, params: Optional[Tuple] = None) -> Optional[Dict[str, Any]]:
        """获取单条记录"""
        try:
            async with self.pool.acquire() as conn:
                record = await conn.fetchrow(query, *params if params else [])
                return dict(record) if record else None
        except Exception as e:
            logging.error(f"获取单条记录失败: {e}, Query: {query}, Params: {params}")
            raise

    async def fetch_all(self, query: str, params: Optional[Tuple] = None) -> List[Dict[str, Any]]:
        """获取多条记录"""
        try:
            async with self.pool.acquire() as conn:
                records = await conn.fetch(query, *params if params else [])
                return [dict(record) for record in records]
        except Exception as e:
            logging.error(f"获取多条记录失败: {e}, Query: {query}, Params: {params}")
            raise

    async def close(self):
        """关闭数据库连接池"""
        if self.pool:
            await self.pool.close()
            self.pool = None
            logging.info("数据库连接池已关闭")

    async def __aenter__(self):
        """异步上下文管理器入口"""
        await self.ensure_connected()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        await self.close()
