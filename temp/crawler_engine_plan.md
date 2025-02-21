# Playwright 网站抓取引擎设计文档

## 一、抓取引擎概述

### 1.1 目标
构建一个基于 Playwright 的网站抓取引擎，实现：
- 可扩展的选择器系统
- 灵活的数据提取方法
- 与数据库的无缝集成
- 健壮的错误处理机制

### 1.2 技术栈
- Playwright
- Python 3.13+
- PostgreSQL 16+
- asyncio

## 二、核心架构

### 2.1 项目结构
```
crawler_engine/
├── __init__.py
├── core/
│   ├── __init__.py
│   ├── browser_manager.py     # 浏览器管理
│   ├── selector_engine.py     # 选择器引擎
│   └── extractor.py          # 数据提取器
├── handlers/
│   ├── __init__.py
│   ├── base_handler.py       # 基础处理器
│   └── element_handlers/     # 元素处理器集合
└── utils/
    ├── __init__.py
    └── error_handler.py      # 错误处理
```

## 三、选择器系统设计

### 3.1 数据库表结构
```sql
-- 选择器类型表
CREATE TABLE selector_types (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    handler_class VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 选择器表
CREATE TABLE selectors (
    id SERIAL PRIMARY KEY,
    website_id INTEGER REFERENCES websites(id),
    selector_type_id INTEGER REFERENCES selector_types(id),
    selector_value TEXT NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 3.2 基础选择器处理器
```python
class BaseSelectorHandler:
    def __init__(self, page):
        self.page = page

    async def find_element(self, selector_value):
        """查找元素"""
        raise NotImplementedError

    async def extract_data(self, element, extract_type):
        """提取数据"""
        raise NotImplementedError
```

### 3.3 选择器注册系统
```python
class SelectorRegistry:
    _handlers = {}

    @classmethod
    def register(cls, selector_type, handler_class):
        """注册新的选择器处理器"""
        cls._handlers[selector_type] = handler_class

    @classmethod
    def get_handler(cls, selector_type):
        """获取选择器处理器"""
        return cls._handlers.get(selector_type)
```

## 四、扩展机制

### 4.1 添加新选择器类型
1. **数据库注册**
```sql
INSERT INTO selector_types (name, description, handler_class)
VALUES (
    'shadow_dom',
    '处理 Shadow DOM 元素',
    'ShadowDOMHandler'
);
```

2. **实现处理器**
```python
class ShadowDOMHandler(BaseSelectorHandler):
    async def find_element(self, selector_value):
        # 实现 Shadow DOM 元素查找逻辑
        host, shadow_selector = selector_value.split(' >> ')
        host_element = await self.page.query_selector(host)
        shadow_root = await host_element.evaluate('el => el.shadowRoot')
        return await shadow_root.query_selector(shadow_selector)
```

### 4.2 数据提取方法
```python
class DataExtractor:
    @staticmethod
    async def extract_text(element):
        return await element.text_content()

    @staticmethod
    async def extract_attribute(element, attribute):
        return await element.get_attribute(attribute)

    @staticmethod
    async def extract_html(element):
        return await element.inner_html()
```

## 五、核心功能实现

### 5.1 浏览器管理器
```python
class BrowserManager:
    def __init__(self):
        self.browser = None
        self.context = None
        self.page = None

    async def init_browser(self, **kwargs):
        """初始化浏览器"""
        self.browser = await playwright.chromium.launch(**kwargs)
        self.context = await self.browser.new_context()
        self.page = await self.context.new_page()

    async def close(self):
        """关闭浏览器资源"""
        await self.page.close()
        await self.context.close()
        await self.browser.close()
```

### 5.2 选择器引擎
```python
class SelectorEngine:
    def __init__(self, page, db_manager):
        self.page = page
        self.db_manager = db_manager

    async def find_element(self, selector_id):
        """根据选择器ID查找元素"""
        selector_data = await self.db_manager.get_selector(selector_id)
        handler = SelectorRegistry.get_handler(selector_data['type'])
        return await handler(self.page).find_element(selector_data['value'])

    async def extract_data(self, element, extract_type):
        """提取元素数据"""
        extractor = DataExtractor()
        return await getattr(extractor, f'extract_{extract_type}')(element)
```

## 六、错误处理

### 6.1 自定义异常
```python
class SelectorError(Exception):
    def __init__(self, message, selector_id=None):
        self.message = message
        self.selector_id = selector_id

class ElementNotFoundError(SelectorError):
    pass

class ExtractionError(SelectorError):
    pass
```

### 6.2 错误处理器
```python
class ErrorHandler:
    @staticmethod
    async def handle_selector_error(error, context):
        """处理选择器错误"""
        # 记录错误
        await log_error(error)
        # 尝试更新选择器
        if isinstance(error, ElementNotFoundError):
            await update_selector(error.selector_id)
```

## 七、使用示例

### 7.1 基本使用
```python
async def scrape_data(website_id, selector_id):
    browser_manager = BrowserManager()
    await browser_manager.init_browser()
    
    try:
        selector_engine = SelectorEngine(
            browser_manager.page,
            db_manager
        )
        
        element = await selector_engine.find_element(selector_id)
        data = await selector_engine.extract_data(element, 'text')
        
        return data
    finally:
        await browser_manager.close()
```

### 7.2 添加新选择器类型
```python
# 1. 注册到数据库
async def register_new_selector_type():
    await db_manager.execute("""
        INSERT INTO selector_types (name, description, handler_class)
        VALUES ($1, $2, $3)
    """, ('iframe', 'iframe内元素选择器', 'IframeHandler'))

# 2. 实现处理器
class IframeHandler(BaseSelectorHandler):
    async def find_element(self, selector_value):
        iframe_selector, element_selector = selector_value.split(' >> ')
        frame = await self.page.frame_locator(iframe_selector)
        return await frame.locator(element_selector)

# 3. 注册处理器
SelectorRegistry.register('iframe', IframeHandler)
```

## 八、最佳实践

### 8.1 选择器管理
1. 定期验证选择器有效性
2. 保存选择器历史版本
3. 实现选择器自动修复机制

### 8.2 性能优化
1. 使用连接池管理数据库连接
2. 实现选择器缓存
3. 优化浏览器资源使用

### 8.3 错误处理
1. 实现重试机制
2. 记录详细错误信息
3. 建立选择器更新机制

## 九、后续规划

1. 实现更多选择器类型
2. 添加选择器验证工具
3. 优化性能和资源使用
4. 完善错误处理机制
5. 添加选择器自动修复功能
