# 实施指南

## 一、优先级实施顺序

### 1. 第一阶段：基础框架（1-2周）
1. 数据库设置
   - 创建数据库和表
   - **[已完成]** 实现基本的CRUD操作
2. 浏览器管理
   - Playwright基础设置，**初步完成浏览器启动和关闭功能**
   - 简单的页面操作 (待实现)

### 2. 第二阶段：核心功能（2-3周）
1. 选择器系统
   - **[已完成]** 基本选择器实现
     - CSS 选择器处理器
     - XPath 选择器处理器
     - ID 选择器处理器
     - Name 选择器处理器
     - Class 选择器处理器
   - 选择器存储和管理 (已实现基础框架)
   - 错误处理和日志记录 (已完善)

### 选择器系统详细说明

#### 选择器类型

选择器引擎支持以下选择器类型：

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

#### 错误处理

选择器系统提供详细的错误处理和日志记录：

- `InvalidSelectorError`：当选择器语法或类型不正确时抛出
- `ElementNotFoundError`：当无法找到匹配的元素时抛出

日志记录包括：
- DEBUG：选择器查找详情，例如 XPath 选择器查找的详细信息
- INFO：成功找到元素，例如成功找到 XPath 元素
- WARNING：未找到元素，例如未找到匹配 XPath 选择器的元素
- ERROR：选择器处理过程中的严重错误

#### 性能和最佳实践

1. 选择器性能优先级
   - ID 选择器最快
   - CSS 选择器次之
   - XPath 选择器性能最低

2. 推荐做法
   - 尽可能使用 ID 选择器
   - 避免复杂的 XPath 表达式
   - 保持选择器简洁明了

3. 选择器缓存
   - 对于频繁使用的选择器，考虑缓存结果
   - 避免重复查找相同元素

2. 动作系统
   - 完善基本动作实现，例如 `select`, `radio`, `checkbox` (待实现)
   - 动作序列管理 (待实现)
3. 数据处理
   - 基本数据提取 (待实现)
   - 简单数据存储 (待实现)

### 3. 第三阶段：工具和优化（1-2周）
1. 配置系统
2. 错误处理
3. 日志系统
4. 简单的备份功能

## 二、测试计划

### 1. 单元测试
```python
def test_crud_manager():
    """测试 CRUD 管理器"""
    pass

def test_browser_manager():
    """测试浏览器管理器"""
    pass

def test_action_executor():
    """测试动作执行器"""
    pass

def test_selector_engine():
    """测试选择器引擎"""
    pass

def test_data_processor():
    """测试数据处理器"""
    pass
```

### 2. 集成测试
```python
async def test_simple_workflow():
    """测试简单工作流"""
    pass

async def test_workflow():
    """测试完整工作流"""
    pass
```

## 三、部署说明

### 1. 环境设置
```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# 安装依赖
pip install -r requirements.txt
```

### 2. 数据库设置
```bash
# 创建数据库
createdb web_automation

# 运行初始化脚本
python scripts/init_db.py
```

## 四、使用示例

### 1. 基本使用流程
```python
async def main():
    # 初始化系统
    config = Config()
    browser_manager = BrowserManager(config)
    
    try:
        # 打开页面
        page = await browser_manager.new_page()
        await page.goto('https://example.com')
        
        # 执行操作
        action_executor = ActionExecutor(page)
        await action_executor.execute_sequence([
            {'type': 'click', 'selector': '#login-button'},
            {'type': 'input', 'selector': '#username', 'value': 'test'}
        ])
        
        # 处理数据
        processor = DataProcessor()
        result = await processor.process(await page.content())
        
    except Exception as e:
        ErrorManager().handle_error(e)
    finally:
        await browser_manager.close()
```

## 五、维护建议

1. 定期检查
   - 每周检查日志
   - 每月进行数据备份
   - 定期更新选择器

2. 问题排查
   - 检查日志文件
   - 验证数据库连接
   - 测试网络连接

3. 性能优化
   - 清理旧数据
   - 优化数据库查询
   - 管理浏览器资源

## 六、注意事项

1. 资源使用
   - 及时关闭浏览器实例
   - 定期清理临时文件
   - 控制并发数量

2. 数据安全
   - 定期备份数据
   - 保护敏感信息
   - 验证数据完整性

3. 错误处理
   - 记录所有错误
   - 实现优雅降级
   - 提供用户反馈

## 日志配置指南

### 基本日志配置

在应用程序的主入口点，建议使用 `logging.config.dictConfig()` 或 `logging.config.fileConfig()` 进行日志配置。以下是推荐的日志配置示例：

```python
import logging
import logging.config

# 使用字典配置日志
logging.config.dictConfig({
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'standard',
            'level': 'INFO'
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': 'app.log',
            'formatter': 'standard',
            'level': 'DEBUG'
        }
    },
    'loggers': {
        '': {  # root logger
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': True
        },
        'core.components.selector': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': False
        }
    }
})
```

### 日志级别说明

- `DEBUG`: 详细信息，用于诊断问题
- `INFO`: 确认事情按预期工作
- `WARNING`: 表明发生了意外情况，但程序仍可继续运行
- `ERROR`: 由于更严重的问题，程序无法执行某些功能
- `CRITICAL`: 严重错误，程序可能无法继续运行

### 在模块中使用日志

在每个模块中，通过 `logging.getLogger(__name__)` 获取日志记录器：

```python
import logging

logger = logging.getLogger(__name__)

def some_function():
    logger.debug('这是一条调试消息')
    logger.info('这是一条信息消息')
    logger.warning('这是一条警告消息')
    logger.error('这是一条错误消息')
```
