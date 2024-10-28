# 浏览器管理器设计文档

## 一、模块概述

浏览器管理器负责创建、管理和销毁 Playwright 浏览器实例，处理会话管理和代理配置。

### 1.1 主要功能
- 浏览器生命周期管理
- 会话状态维护
- 代理配置和轮换
- 资源使用优化
- 错误处理和恢复

### 1.2 技术栈
- Playwright
- asyncio
- aiohttp (用于代理验证)

## 二、核心组件

### 2.1 浏览器管理器
```python
class BrowserManager:
    def __init__(self, config: dict = None):
        self.config = config or {}
        self.browser = None
        self.context = None
        self.active_pages = {}

    async def init_browser(self):
        """初始化浏览器实例"""
        self.browser = await playwright.chromium.launch(
            proxy=self.config.get('proxy'),
            **self.config.get('browser_options', {})
        )

    async def new_context(self, **kwargs):
        """创建新的浏览器上下文"""
        self.context = await self.browser.new_context(**kwargs)
        return self.context

    async def new_page(self, context_id: str = None):
        """创建新页面"""
        context = self.context or await self.new_context()
        page = await context.new_page()
        self.active_pages[id(page)] = page
        return page

    async def close(self):
        """关闭所有资源"""
        for page in self.active_pages.values():
            await page.close()
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
```

### 2.2 会话管理器
```python
class SessionManager:
    def __init__(self, storage_state: str = None):
        self.storage_state = storage_state
        self.contexts = {}

    async def create_session(self, website_id: int):
        """创建新会话"""
        context = await browser_manager.new_context(
            storage_state=self.storage_state
        )
        self.contexts[website_id] = context
        return context

    async def get_session(self, website_id: int):
        """获取或创建会话"""
        if website_id not in self.contexts:
            return await self.create_session(website_id)
        return self.contexts[website_id]
```

## 三、配置系统

### 3.1 浏览器配置
```python
DEFAULT_BROWSER_CONFIG = {
    'headless': True,
    'proxy': None,
    'viewport': {'width': 1920, 'height': 1080},
    'timeout': 30000,
    'user_agent': 'Mozilla/5.0 ...',
}
```

### 3.2 会话配置
```python
SESSION_CONFIG = {
    'storage_state': './storage/auth.json',
    'permissions': ['geolocation'],
    'locale': 'zh-CN',
}
```

## 四、错误处理

### 4.1 异常类型
```python
class BrowserError(Exception):
    """浏览器相关错误的基类"""
    pass

class SessionError(BrowserError):
    """会话相关错误"""
    pass

class ResourceError(BrowserError):
    """资源管理错误"""
    pass
```

### 4.2 错误处理策略
```python
async def handle_browser_error(error: Exception):
    """处理浏览器错误"""
    if isinstance(error, playwright.Error):
        await browser_manager.close()
        await browser_manager.init_browser()
    elif isinstance(error, SessionError):
        await session_manager.cleanup()
```

## 五、使用示例

### 5.1 基本使用
```python
async def main():
    browser_manager = BrowserManager()
    await browser_manager.init_browser()
    
    try:
        page = await browser_manager.new_page()
        await page.goto('https://example.com')
        # 执行操作
    finally:
        await browser_manager.close()
```

### 5.2 带会话管理
```python
async def with_session():
    session_manager = SessionManager()
    context = await session_manager.get_session(website_id=1)
    
    page = await context.new_page()
    await page.goto('https://example.com')
    # 执行操作
```

## 六、性能优化

### 6.1 资源池化
- 实现页面复用
- 限制最大并发数
- 智能清理未使用的资源

### 6.2 缓存策略
- 缓存常用会话
- 复用浏览器上下文
- 优化存储状态

## 七、安全考虑

1. 隔离性
   - 每个网站使用独立上下文
   - 敏感数据加密存储
   
2. 资源限制
   - 设置最大内存使用
   - 限制并发连接数
   - 超时控制

## 八、监控和日志

1. 性能指标
   - 页面加载时间
   - 内存使用情况
   - 并发会话数

2. 日志记录
   - 错误追踪
   - 性能监控
   - 资源使用统计
