from .db_manager import DatabaseManager
from typing import Dict, Any, Optional, List
import time
import logging

class CRUDManager:
    def __init__(self):
        """
        初始化 CRUD 管理器
        """
        self.db = DatabaseManager()
        self._connected = False

    async def ensure_connected(self):
        """确保数据库已连接"""
        if not self._connected:
            await self.db.connect()
            self._connected = True

    # 网站相关操作
    async def create_website(self, name: str, url: str) -> Dict[str, Any]:
        """
        创建新网站
        
        :param name: 网站名称
        :param url: 网站 URL
        :return: 创建的网站信息
        """
        await self.ensure_connected()
        query = """
        INSERT INTO websites (name, url)
        VALUES ($1, $2)
        RETURNING *
        """
        return await self.db.fetch_one(query, (name, url))

    async def get_website(self, website_id: int) -> Dict[str, Any]:
        """
        获取指定网站信息
        
        :param website_id: 网站 ID
        :return: 网站信息
        """
        await self.ensure_connected()
        query = "SELECT * FROM websites WHERE id = $1"
        return await self.db.fetch_one(query, (website_id,))

    async def get_all_websites(self) -> List[Dict[str, Any]]:
        """
        获取所有网站信息
        
        :return: 网站信息列表
        """
        await self.ensure_connected()
        query = "SELECT * FROM websites"
        return await self.db.fetch_all(query)

    async def update_website(self, website_id: int, name: Optional[str] = None, 
                       url: Optional[str] = None, description: Optional[str] = None) -> Dict[str, Any]:
        """
        更新网站信息
        
        :param website_id: 网站 ID
        :param name: 新的网站名称
        :param url: 新的网站 URL
        :param description: 新的网站描述
        :return: 更新后的网站信息
        """
        await self.ensure_connected()
        updates = []
        params = []
        param_count = 1
        
        if name is not None:
            updates.append(f"name = ${param_count}")
            params.append(name)
            param_count += 1
        if url is not None:
            updates.append(f"url = ${param_count}")
            params.append(url)
            param_count += 1
        if description is not None:
            updates.append(f"description = ${param_count}")
            params.append(description)
            param_count += 1
        
        if not updates:
            return None
        
        params.append(website_id)
        query = f"""
        UPDATE websites 
        SET {', '.join(updates)}
        WHERE id = ${param_count}
        RETURNING *
        """
        return await self.db.fetch_one(query, tuple(params))

    async def delete_website(self, website_id: int) -> bool:
        """
        删除网站
        
        :param website_id: 网站 ID
        :return: 是否删除成功
        """
        await self.ensure_connected()
        query = "DELETE FROM websites WHERE id = $1"
        await self.db.execute_query(query, (website_id,))
        return True

    # 选择器相关操作
    def create_selector(self, website_id: int, name: str, selector_type: str, 
                        selector_value: str, description: Optional[str] = None) -> Dict[str, Any]:
        """
        创建选择器
        
        :param website_id: 网站 ID
        :param name: 选择器名称
        :param selector_type: 选择器类型（CSS/XPath等）
        :param selector_value: 选择器值
        :param description: 选择器描述
        :return: 创建的选择器信息
        """
        query = """
        INSERT INTO selectors (website_id, name, selector_type, selector_value, description)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING *
        """
        return self.db.fetch_one(query, (website_id, name, selector_type, selector_value, description))

    def get_selector(self, selector_id: int) -> Dict[str, Any]:
        """
        获取选择器信息
        
        :param selector_id: 选择器 ID
        :return: 选择器信息
        """
        query = "SELECT * FROM selectors WHERE id = %s"
        return self.db.fetch_one(query, (selector_id,))

    def get_website_selectors(self, website_id: int) -> List[Dict[str, Any]]:
        """
        获取指定网站的所有选择器
        
        :param website_id: 网站 ID
        :return: 选择器列表
        """
        query = "SELECT * FROM selectors WHERE website_id = %s"
        return self.db.fetch_all(query, (website_id,))

    def delete_selector(self, selector_id: int) -> bool:
        """
        删除选择器
        
        :param selector_id: 选择器 ID
        :return: 是否删除成功
        """
        query = "DELETE FROM selectors WHERE id = %s"
        self.db.execute_query(query, (selector_id,))
        return True

    # 工作流相关操作
    async def create_workflow(self, name: str, user_id: int, website_id: int, 
                        description: Optional[str] = None) -> Dict[str, Any]:
        """
        创建工作流
        
        :param name: 工作流名称
        :param user_id: 用户 ID
        :param website_id: 网站 ID
        :param description: 工作流描述
        :return: 创建的工作流信息
        """
        await self.ensure_connected()
        start_time = time.time()
        logging.info(f"开始创建工作流: {name}")

        query = """
        INSERT INTO workflows (name, user_id, website_id, description)
        VALUES ($1, $2, $3, $4)
        RETURNING *
        """
        workflow = await self.db.fetch_one(query, (name, user_id, website_id, description))

        end_time = time.time()
        duration = end_time - start_time
        logging.info(f"工作流创建完成: {name} (ID: {workflow['id']}), 耗时: {duration:.4f} 秒")

        return workflow

    async def get_workflow(self, workflow_id: int) -> Dict[str, Any]:
        """
        获取工作流信息
        
        :param workflow_id: 工作流 ID
        :return: 工作流信息
        """
        await self.ensure_connected()
        query = "SELECT * FROM workflows WHERE id = $1"
        return await self.db.fetch_one(query, (workflow_id,))

    async def get_all_workflows(self) -> List[Dict[str, Any]]:
        """
        获取所有工作流
        
        :return: 工作流列表
        """
        await self.ensure_connected()
        query = "SELECT * FROM workflows"
        return await self.db.fetch_all(query)

    async def get_user_workflows(self, user_id: int) -> List[Dict[str, Any]]:
        """
        获取用户的所有工作流
        
        :param user_id: 用户 ID
        :return: 工作流列表
        """
        await self.ensure_connected()
        query = "SELECT * FROM workflows WHERE user_id = $1"
        return await self.db.fetch_all(query, (user_id,))

    async def add_workflow_step(self, workflow_id: int, step_order: int, action_type: str, 
                          selector_type: Optional[str] = None, selector_value: Optional[str] = None,
                          value: Optional[str] = None, description: Optional[str] = None) -> Dict[str, Any]:
        """
        为工作流添加步骤
        
        :param workflow_id: 工作流 ID
        :param step_order: 步骤顺序
        :param action_type: 动作类型
        :param selector_type: 选择器类型
        :param selector_value: 选择器值
        :param value: 动作值
        :param description: 步骤描述
        :return: 创建的工作流步骤信息
        """
        await self.ensure_connected()
        query = """
        INSERT INTO workflow_steps 
        (workflow_id, step_order, action_type, selector_type, selector_value, value, description)
        VALUES ($1, $2, $3, $4, $5, $6, $7)
        RETURNING *
        """
        return await self.db.fetch_one(query, (
            workflow_id, step_order, action_type, selector_type,
            selector_value, value, description
        ))

    async def get_workflow_steps(self, workflow_id: int) -> List[Dict[str, Any]]:
        """
        获取工作流的所有步骤
        
        :param workflow_id: 工作流 ID
        :return: 工作流步骤列表
        """
        await self.ensure_connected()
        query = """
        SELECT * FROM workflow_steps
        WHERE workflow_id = $1
        ORDER BY step_order
        """
        return await self.db.fetch_all(query, (workflow_id,))

    # 用户相关操作
    async def create_user(self, username: str, email: str, password_hash: str) -> Dict[str, Any]:
        """
        创建新用户
        
        :param username: 用户名
        :param email: 电子邮件
        :param password_hash: 密码哈希
        :return: 创建的用户信息
        """
        await self.ensure_connected()
        query = """
        INSERT INTO users (username, email, password_hash)
        VALUES ($1, $2, $3)
        RETURNING *
        """
        return await self.db.fetch_one(query, (username, email, password_hash))

    async def get_user(self, user_id: int) -> Dict[str, Any]:
        """
        获取用户信息
        
        :param user_id: 用户 ID
        :return: 用户信息
        """
        await self.ensure_connected()
        query = "SELECT * FROM users WHERE id = $1"
        return await self.db.fetch_one(query, (user_id,))

    async def update_user(self, user_id: int, username: Optional[str] = None, 
                    email: Optional[str] = None, role: Optional[str] = None) -> Dict[str, Any]:
        """
        更新用户信息
        
        :param user_id: 用户 ID
        :param username: 新的用户名
        :param email: 新的电子邮件
        :param role: 新的用户角色
        :return: 更新后的用户信息
        """
        await self.ensure_connected()
        updates = []
        params = []
        
        if username is not None:
            updates.append("username = %s")
            params.append(username)
        if email is not None:
            updates.append("email = %s")
            params.append(email)
        if role is not None:
            updates.append("role = %s")
            params.append(role)
        
        if not updates:
            return None
        
        params.append(user_id)
        query = f"""
        UPDATE users 
        SET {', '.join(updates)}
        WHERE id = %s
        RETURNING *
        """
        return await self.db.fetch_one(query, tuple(params))

    async def delete_workflow(self, workflow_id: int) -> bool:
        """
        删除工作流及其所有步骤
        
        :param workflow_id: 工作流 ID
        :return: 是否删除成功
        """
        try:
            async with self.db.transaction() as transaction:
                # 先删除工作流的所有步骤
                query = """
                DELETE FROM workflow_steps
                WHERE workflow_id = $1
                """
                await self.db.execute(query, (workflow_id,))
                
                # 再删除工作流本身
                query = """
                DELETE FROM workflows
                WHERE id = $1
                """
                await self.db.execute(query, (workflow_id,))
                return True
        except Exception as e:
            logging.error(f"删除工作流失败: {e}")
            raise

    async def delete_user_workflows(self, user_id: int) -> None:
        """删除用户的所有工作流"""
        try:
            # 开启事务
            async with self.db.transaction() as transaction:
                # 先删除工作流的步骤
                query = """
                DELETE FROM workflow_steps
                WHERE workflow_id IN (
                    SELECT id FROM workflows WHERE user_id = $1
                )
                """
                await self.db.execute(query, (user_id,))
                
                # 再删除工作流
                query = """
                DELETE FROM workflows
                WHERE user_id = $1
                """
                await self.db.execute(query, (user_id,))
        except Exception as e:
            logging.error(f"删除用户工作流失败: {e}")
            raise

    async def delete_user(self, user_id: int) -> None:
        """删除用户"""
        try:
            # 开启事务
            async with self.db.transaction() as transaction:
                # 先删除用户的工作流
                await self.delete_user_workflows(user_id)
                
                # 再删除用户
                query = """
                DELETE FROM users
                WHERE id = $1
                """
                await self.db.execute(query, (user_id,))
        except Exception as e:
            logging.error(f"删除用户失败: {e}")
            raise

    # 动作相关操作
    def create_action(self, website_id: int, name: str, action_type: str, 
                      selector_id: Optional[int] = None, parameters: Optional[str] = '{}') -> Dict[str, Any]:
        """
        创建动作
        
        :param website_id: 网站 ID
        :param name: 动作名称
        :param action_type: 动作类型
        :param selector_id: 选择器 ID
        :param parameters: 动作参数（JSON 字符串）
        :return: 创建的动作信息
        """
        query = """
        INSERT INTO actions (website_id, name, action_type, selector_id, parameters)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING *
        """
        return self.db.fetch_one(query, (website_id, name, action_type, selector_id, parameters))

    def get_action(self, action_id: int) -> Dict[str, Any]:
        """
        获取动作信息
        
        :param action_id: 动作 ID
        :return: 动作信息
        """
        query = "SELECT * FROM actions WHERE id = %s"
        return self.db.fetch_one(query, (action_id,))

    def get_website_actions(self, website_id: int) -> List[Dict[str, Any]]:
        """
        获取指定网站的所有动作
        
        :param website_id: 网站 ID
        :return: 动作列表
        """
        query = "SELECT * FROM actions WHERE website_id = %s"
        return self.db.fetch_all(query, (website_id,))

    # 用户偏好相关操作
    def create_user_preference(self, user_id: int, website_id: int, 
                                preference_key: str, preference_value: str) -> Dict[str, Any]:
        """
        创建用户偏好
        
        :param user_id: 用户 ID
        :param website_id: 网站 ID
        :param preference_key: 偏好键
        :param preference_value: 偏好值
        :return: 创建的用户偏好信息
        """
        query = """
        INSERT INTO user_preferences (user_id, website_id, preference_key, preference_value)
        VALUES (%s, %s, %s, %s)
        RETURNING *
        """
        return self.db.fetch_one(query, (user_id, website_id, preference_key, preference_value))

    def get_user_preference(self, preference_id: int) -> Dict[str, Any]:
        """
        获取用户偏好信息
        
        :param preference_id: 偏好 ID
        :return: 用户偏好信息
        """
        query = "SELECT * FROM user_preferences WHERE id = %s"
        return self.db.fetch_one(query, (preference_id,))

    def get_user_website_preferences(self, user_id: int, website_id: int) -> List[Dict[str, Any]]:
        """
        获取用户在特定网站的所有偏好
        
        :param user_id: 用户 ID
        :param website_id: 网站 ID
        :return: 用户偏好列表
        """
        query = """
        SELECT * FROM user_preferences 
        WHERE user_id = %s AND website_id = %s
        """
        return self.db.fetch_all(query, (user_id, website_id))

    async def close(self):
        """关闭数据库连接"""
        await self.db.close()
        self._connected = False

    async def __aenter__(self):
        """异步上下文管理器入口"""
        await self.ensure_connected()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        await self.close()

    async def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """根据用户名获取用户"""
        query = """
        SELECT * FROM users
        WHERE username = $1
        """
        return await self.db.fetch_one(query, (username,))
