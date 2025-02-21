from .db_manager import DatabaseManager

def init_database():
    """初始化数据库表"""
    db = DatabaseManager()
    
    # 创建用户表
    db.execute_query("""
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        username VARCHAR(100) UNIQUE NOT NULL,
        email VARCHAR(255) UNIQUE NOT NULL,
        password_hash VARCHAR(255) NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # 创建网站表
    db.execute_query("""
    CREATE TABLE IF NOT EXISTS websites (
        id SERIAL PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        url TEXT NOT NULL,
        description TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # 创建选择器表
    db.execute_query("""
    CREATE TABLE IF NOT EXISTS selectors (
        id SERIAL PRIMARY KEY,
        website_id INTEGER REFERENCES websites(id),
        name VARCHAR(255) NOT NULL,
        selector_type VARCHAR(50) NOT NULL,
        selector_value TEXT NOT NULL,
        description TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # 创建工作流表
    db.execute_query("""
    CREATE TABLE IF NOT EXISTS workflows (
        id SERIAL PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        user_id INTEGER REFERENCES users(id),
        website_id INTEGER REFERENCES websites(id),
        description TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # 创建工作流步骤表
    db.execute_query("""
    CREATE TABLE IF NOT EXISTS workflow_steps (
        id SERIAL PRIMARY KEY,
        workflow_id INTEGER REFERENCES workflows(id),
        step_order INTEGER NOT NULL,
        action_type VARCHAR(50) NOT NULL,
        selector_id INTEGER REFERENCES selectors(id),
        value TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # 创建动作表
    db.execute_query("""
    CREATE TABLE IF NOT EXISTS actions (
        id SERIAL PRIMARY KEY,
        website_id INTEGER REFERENCES websites(id),
        name VARCHAR(255) NOT NULL,
        action_type VARCHAR(50) NOT NULL,
        selector_id INTEGER REFERENCES selectors(id),
        parameters JSONB DEFAULT '{}',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # 创建用户偏好表
    db.execute_query("""
    CREATE TABLE IF NOT EXISTS user_preferences (
        id SERIAL PRIMARY KEY,
        user_id INTEGER REFERENCES users(id),
        website_id INTEGER REFERENCES websites(id),
        preference_key VARCHAR(255) NOT NULL,
        preference_value TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    db.close()
    print("数据库初始化完成")

if __name__ == "__main__":
    init_database() 