from .db_manager import DatabaseManager

class CRUDManager:
    def __init__(self):
        self.db = DatabaseManager()

    def create_website(self, name, url):
        query = """
        INSERT INTO websites (name, url)
        VALUES (%s, %s)
        RETURNING id, name, url
        """
        return self.db.fetch_one(query, (name, url))

    def get_website(self, website_id):
        query = "SELECT * FROM websites WHERE id = %s"
        return self.db.fetch_one(query, (website_id,))

    def update_website(self, website_id, name=None, url=None):
        updates = []
        params = []
        if name:
            updates.append("name = %s")
            params.append(name)
        if url:
            updates.append("url = %s")
            params.append(url)
        
        if not updates:
            return None
            
        params.append(website_id)
        query = f"""
        UPDATE websites 
        SET {', '.join(updates)}
        WHERE id = %s
        RETURNING *
        """
        return self.db.fetch_one(query, tuple(params))

    def delete_website(self, website_id):
        query = "DELETE FROM websites WHERE id = %s"
        self.db.execute_query(query, (website_id,))

    def get_all_websites(self):
        """获取所有网站"""
        return self.db.fetch_all("SELECT * FROM websites")

    def get_all_users(self):
        """获取所有用户"""
        return self.db.fetch_all("SELECT * FROM users")

    def get_user_workflows(self, user_id):
        """获取用户的工作流"""
        query = """
        SELECT * FROM workflow_details 
        WHERE username = (SELECT username FROM users WHERE id = %s)
        """
        return self.db.fetch_all(query, (user_id,))

    def create_workflow(self, name, user_id, website_id, description=None):
        """创建新的工作流"""
        query = """
        INSERT INTO workflows (name, user_id, website_id, description)
        VALUES (%s, %s, %s, %s)
        RETURNING id
        """
        return self.db.fetch_one(query, (name, user_id, website_id, description))

    def close(self):
        """关闭数据库连接"""
        self.db.close()
