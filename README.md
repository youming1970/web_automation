# Web Survey Automation Tool

这是一个用于自动化网上调查的工具，使用 PostgreSQL 和 Python 实现。

## 项目结构
```
web_automation/
├── core/
│   ├── components/       # 核心组件
│   │   ├── action/
│   │   │   ├── __init__.py
│   │   │   └── action_executor.py
│   │   ├── selector/     # 选择器引擎相关代码
│   │   │   ├── __init__.py
│   │   │   └── selector_engine.py
│   │   ├── browser/      # 浏览器管理器相关代码
│   │   │   ├── __init__.py
│   │   │   └── browser_manager.py
│   │   ├── processor/    # 数据处理器相关代码
│   │   │   ├── __init__.py
│   │   │   └── data_processor.py
├── database/
│   ├── __init__.py
│   ├── db_manager.py
│   └── crud_manager.py
├── docs/
│   └── request.md
├── test_connection.py
└── README.md
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

### **自动化网上调查**

本项目专注于自动化执行网上调查问卷。你可以配置调查问卷的 URL，以及需要自动填写的字段和选项，让程序自动完成问卷填写和提交。

**使用步骤：**

1.  **配置调查问卷信息：** 在数据库中添加调查问卷的 URL，并定义需要操作的元素选择器（例如问题、选项、提交按钮）。
2.  **创建工作流：**  根据调查问卷的步骤，创建包含 `goto`, `click`, `input`, `select`, `radio`, `checkbox` 等动作的工作流。
3.  **运行自动化脚本：**  执行 Python 脚本，程序将自动打开网页，填写问卷，并提交。

**示例 (概念代码):**

```python
from database.crud_manager import CRUDManager
from core.action.action_executor import ActionExecutor # 假设路径

crud = CRUDManager()
# 获取调查问卷配置 (假设 website_id = 1)
website_config = crud.get_website(1)
workflow = crud.get_website_workflows(website_config['id']) #  修正:  get_website_workflows 更贴切

# 初始化动作执行器 (需要 page 对象，这里只是概念代码)
action_executor = ActionExecutor() #  修正:  无需 page 对象在此初始化
# await action_executor.execute_sequence(workflow, page) # 修正:  page 对象应在 execute_sequence 中传入，并设为异步

print("自动化调查问卷已完成！")
```

## 下一步计划
1. 实现完整的 CRUD 操作
2. 添加数据验证
3. 实现用户界面
4. 编写单元测试
5. **完善自动化调查问卷功能**
    - **添加更多动作类型，例如 `select` (选择下拉框), `radio` (单选框), `checkbox` (复选框) 等**
    - **[已完成]** 实现更灵活的选择器配置，支持多种选择器类型**
        - CSS 选择器
        - XPath 选择器
        - ID 选择器
        - Name 选择器
        - Class 选择器
    - **增加反爬虫机制应对策略，例如设置请求延迟，更换 User-Agent，使用代理 IP 等**
    - **考虑验证码处理方案 (例如集成第三方验证码识别服务)**
    - **[已完成]** 增加日志记录功能，方便调试和监控
    - **[已完成]** 优化错误处理机制，提高程序的健壮性

### 选择器系统特性

#### 支持的选择器类型

1. CSS 选择器
   - 前缀：`css:` 或直接使用
   - 示例：`css:.class-name`、`#element-id`

2. XPath 选择器
   - 前缀：`xpath:`
   - 示例：`xpath://div[@class='example']`

3. ID 选择器
   - 前缀：`id:` 或 `#`
   - 示例：`id:login-button`、`#username`

4. Name 选择器
   - 前缀：`name:` 或 `[name=""]`
   - 示例：`name:email`、`[name="password"]`

5. Class 选择器
   - 前缀：`class:` 或 `.`
   - 示例：`class:btn-primary`、`.error-message`

#### 选择器使用示例

```python
async def example_selector_usage():
    selector_engine = SelectorEngine(page)
    
    # 使用不同类型的选择器
    login_button = await selector_engine.find_element('id:login-button')
    username_input = await selector_engine.find_element('name:username')
    error_messages = await selector_engine.find_elements('.error-message')
    
    # XPath 选择器
    specific_div = await selector_engine.find_element('xpath://div[@data-test="example"]')
```

#### 错误处理和日志记录

选择器系统提供详细的错误处理和日志记录：

- `InvalidSelectorError`：当选择器语法或类型不正确时抛出，例如 XPath 选择器未以 '//' 或 '(' 开头。
- `ElementNotFoundError`：当无法找到匹配的元素时抛出，例如使用 XPath 选择器未找到元素。

日志记录包括：
- `DEBUG`：记录详细的选择器查找过程，例如 "XPath 选择器查找单个元素: {selector}"。
- `INFO`：记录成功找到元素的信息，例如 "成功找到 XPath 元素: {selector}" 或 "成功找到 {len(elements)} 个 XPath 元素: {selector}"。
- `WARNING`：记录未找到元素的警告信息，例如 "未找到匹配 XPath 选择器的元素: {selector}"。
- `ERROR`：记录选择器处理过程中的严重错误。

## 贡献
欢迎提交 Issue 和 Pull Request。

## 许可证
MIT License
