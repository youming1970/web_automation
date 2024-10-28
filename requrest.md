您的思路很正确。从数据库设计开始是一个明智的选择，因为它将为整个项目奠定基础。让我们详细规划数据库结构：

1. 数据库选择：
   - 推荐使用 PostgreSQL，因为它支持复杂查询、JSON 数据类型，并且可以很好地处理大量数据。

2. 主要表结构：

   a. Websites 表
   ```sql
   CREATE TABLE websites (
     id SERIAL PRIMARY KEY,
     name VARCHAR(255) NOT NULL,
     url VARCHAR(255) NOT NULL,
     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
     updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
   );
   ```

   b. Users 表
   ```sql
   CREATE TABLE users (
     id SERIAL PRIMARY KEY,
     username VARCHAR(50) UNIQUE NOT NULL,
     email VARCHAR(255) UNIQUE NOT NULL,
     password_hash VARCHAR(255) NOT NULL,
     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
     updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
   );
   ```

   c. Selectors 表
   ```sql
   CREATE TABLE selectors (
     id SERIAL PRIMARY KEY,
     website_id INTEGER REFERENCES websites(id),
     name VARCHAR(100) NOT NULL,
     selector_type VARCHAR(20) NOT NULL, -- 例如：CSS, XPath, Custom
     selector_value TEXT NOT NULL,
     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
     updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
   );
   ```

   d. Actions 表
   ```sql
   CREATE TABLE actions (
     id SERIAL PRIMARY KEY,
     website_id INTEGER REFERENCES websites(id),
     name VARCHAR(100) NOT NULL,
     action_type VARCHAR(50) NOT NULL, -- 例如：click, input, scroll
     selector_id INTEGER REFERENCES selectors(id),
     parameters JSONB, -- 存储额外的参数
     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
     updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
   );
   ```

   e. Workflows 表
   ```sql
   CREATE TABLE workflows (
     id SERIAL PRIMARY KEY,
     user_id INTEGER REFERENCES users(id),
     website_id INTEGER REFERENCES websites(id),
     name VARCHAR(255) NOT NULL,
     description TEXT,
     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
     updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
   );
   ```

   f. WorkflowSteps 表
   ```sql
   CREATE TABLE workflow_steps (
     id SERIAL PRIMARY KEY,
     workflow_id INTEGER REFERENCES workflows(id),
     action_id INTEGER REFERENCES actions(id),
     step_order INTEGER NOT NULL,
     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
     updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
   );
   ```

   g. UserPreferences 表
   ```sql
   CREATE TABLE user_preferences (
     id SERIAL PRIMARY KEY,
     user_id INTEGER REFERENCES users(id),
     website_id INTEGER REFERENCES websites(id),
     preference_key VARCHAR(100) NOT NULL,
     preference_value JSONB,
     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
     updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
   );
   ```

3. 索引：
   - 为常用查询字段添加索引，如 website_id, user_id 等。

4. 触发器：
   - 创建触发器以自动更新 updated_at 字段。

5. 视图：
   - 创建视图来简化常用的复杂查询。

6. 数据库函数：
   - 创建函数来处理常见的数据操作，如创建新的工作流程。

实施步骤：

1. 设置开发环境：
   - 安装 PostgreSQL
   - 设置 Python 环境，安装必要的库（如 psycopg2）

2. 创建数据库：
   ```sql
   CREATE DATABASE web_automation;
   ```

3. 连接到数据库并执行上述 SQL 语句创建表结构。

4. 创建一个 Python 脚本来管理数据库连接和操作：

   ```python
   import psycopg2
   from psycopg2.extras import RealDictCursor

   class DatabaseManager:
       def __init__(self):
           self.conn = psycopg2.connect(
               dbname="web_automation",
               user="your_username",
               password="your_password",
               host="localhost"
           )
           self.cur = self.conn.cursor(cursor_factory=RealDictCursor)

       def execute_query(self, query, params=None):
           self.cur.execute(query, params)
           self.conn.commit()

       def fetch_all(self, query, params=None):
           self.cur.execute(query, params)
           return self.cur.fetchall()

       def close(self):
           self.cur.close()
           self.conn.close()

   # 使用示例
   db = DatabaseManager()
   db.execute_query("INSERT INTO websites (name, url) VALUES (%s, %s)", ("Example", "https://example.com"))
   results = db.fetch_all("SELECT * FROM websites")
   print(results)
   db.close()
   ```

5. 测试数据库连接和基本操作。

6. 开始实现基本的 CRUD (Create, Read, Update, Delete) 操作为每个表。

7. 考虑实现数据验证和安全措施，如参数化查询以防止 SQL 注入。

这个数据库结构为您的项目提供了一个坚实的基础。它允许存储网站信息、选择器、操作步骤、用户工作流程和偏好设置。随着项目的发展，您可能需要调整或扩展这个结构，但这是一个很好的起点。

# 数据库实现进度

## 1. 环境准备
- 操作系统：WSL Ubuntu 24.04
- Python版本：3.13.0
- PostgreSQL版本：16.4
- 已安装依赖：psycopg2-binary 2.9.10

## 2. 数据库配置
- 数据库名：web_automation
- 用户名：poording
- 密码：Ab.12345
- 主机：localhost

## 3. 已完成的表结构
已创建的表：
- websites
- users
- selectors
- actions
- workflows
- workflow_steps
- user_preferences

## 4. 优化措施
### 已创建的索引：
```sql
CREATE INDEX idx_websites_url ON websites(url);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_selectors_website_id ON selectors(website_id);
CREATE INDEX idx_actions_website_id ON actions(website_id);
CREATE INDEX idx_actions_selector_id ON actions(selector_id);
CREATE INDEX idx_workflow_steps_workflow_order ON workflow_steps(workflow_id, step_order);
CREATE INDEX idx_user_preferences_user_website ON user_preferences(user_id, website_id);
```

### 自动更新触发器：
已为所有表创建updated_at自动更新触发器

## 5. 数据库备份方法
### 创建完整备份：
```bash
# 创建SQL备份
pg_dump -U poording -d web_automation > web_automation_backup.sql

# 创建自定义格式备份（推荐）
pg_dump -U poording -d web_automation -Fc > web_automation_backup.dump
```

### 恢复备份：
```bash
# 恢复SQL备份
psql -U poording -d web_automation < web_automation_backup.sql

# 恢复自定义格式备份
pg_restore -U poording -d web_automation web_automation_backup.dump
```

## 6. 下一步计划
- [ ] 创建测试数据
- [ ] 编写Python连接代码
- [ ] 创建常用视图
- [ ] 实现基本的CRUD操作