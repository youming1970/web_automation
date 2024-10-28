# Web Automation Database

这是一个用于 Web 自动化的数据库系统，使用 PostgreSQL 和 Python 实现。

## 项目结构
```
web_automation/
├── database/
│   ├── __init__.py          # 包初始化文件
│   ├── db_manager.py        # 数据库连接管理
│   └── crud_manager.py      # CRUD 操作
├── docs/
│   └── request.md           # 数据库设计文档
├── test_connection.py       # 测试脚本
└── README.md               # 项目说明文件
```

## 环境要求
- Python 3.13.0
- PostgreSQL 16.4
- psycopg2-binary 2.9.10

## 快速开始

1. **克隆仓库**
```bash
git clone <repository-url>
cd web_automation
```

2. **安装依赖**
```bash
pip install psycopg2-binary
```

3. **配置数据库**
- 确保 PostgreSQL 服务正在运行
- 创建数据库和用户：
```bash
sudo -u postgres psql
CREATE DATABASE web_automation;
CREATE USER poording WITH PASSWORD 'Ab.12345';
GRANT ALL PRIVILEGES ON DATABASE web_automation TO poording;
```

4. **运行测试**
```bash
python test_connection.py
```

## 使用说明

### 数据库管理
```python
from database import DatabaseManager

# 创建数据库连接
db = DatabaseManager()

# 执行查询
results = db.fetch_all("SELECT * FROM websites")

# 关闭连接
db.close()
```

### CRUD 操作
```python
from database import CRUDManager

# 创建 CRUD 管理器
crud = CRUDManager()

# 获取所有网站
websites = crud.get_all_websites()

# 获取用户工作流
workflows = crud.get_user_workflows(user_id=1)

# 关闭连接
crud.close()
```

## 下一步计划
1. 实现完整的 CRUD 操作
2. 添加数据验证
3. 实现用户界面
4. 编写单元测试

## 贡献
欢迎提交 Issue 和 Pull Request。

## 许可证
MIT License
