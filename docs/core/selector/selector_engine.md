# 选择器引擎设计文档

## 一、模块概述

选择器引擎负责管理和优化网页元素的定位策略，支持多种选择器类型，并提供智能选择器更新机制。

### 1.1 主要功能
- 多类型选择器支持
- 选择器验证和优化
- 智能选择器更新
- 选择器历史管理
- 性能监控和优化

### 1.2 依赖组件
- Playwright
- 数据库模块
- 错误处理模块

## 二、核心组件

### 2.1 选择器引擎基类
```python
class BaseSelectorEngine:
    def __init__(self, page, db_manager):
        self.page = page
        self.db_manager = db_manager
        self.selector_cache = {}

    async def find_element(self, selector_data: dict):
        """查找元素的通用方法"""
        selector_type = selector_data['type']
        selector_value = selector_data['value']
        
        handler = self.get_selector_handler(selector_type)
        return await handler.find(selector_value)

    def get_selector_handler(self, selector_type: str):
        """获取对应类型的选择器处理器"""
        return SELECTOR_HANDLERS.get(selector_type)
```

### 2.2 选择器处理器
```python
class SelectorHandler:
    def __init__(self, page):
        self.page = page

    async def find(self, selector: str):
        """查找元素"""
        raise NotImplementedError

    async def validate(self, selector: str):
        """验证选择器"""
        raise NotImplementedError

    async def optimize(self, selector: str):
        """优化选择器"""
        raise NotImplementedError
```

### 2.3 具体实现示例
```python
class CSSSelector(SelectorHandler):
    async def find(self, selector: str):
        try:
            return await self.page.wait_for_selector(selector)
        except Exception as e:
            raise SelectorError(f"Failed to find element: {str(e)}")

class XPathSelector(SelectorHandler):
    async def find(self, selector: str):
        try:
            return await self.page.wait_for_selector(f"xpath={selector}")
        except Exception as e:
            raise SelectorError(f"Failed to find element: {str(e)}")
```

## 三、选择器优化

### 3.1 选择器生成策略
```python
class SelectorGenerator:
    def __init__(self, page):
        self.page = page

    async def generate_selectors(self, element) -> list:
        """生成多个可能的选择器"""
        selectors = []
        
        # CSS选择器
        css = await self._generate_css(element)
        selectors.append(('css', css))
        
        # XPath选择器
        xpath = await self._generate_xpath(element)
        selectors.append(('xpath', xpath))
        
        return selectors

    async def _generate_css(self, element):
        """生成CSS选择器"""
        # 实现CSS选择器生成逻辑
        pass

    async def _generate_xpath(self, element):
        """生成XPath选择器"""
        # 实现XPath选择器生成逻辑
        pass
```

### 3.2 选择器验证
```python
class SelectorValidator:
    def __init__(self, page):
        self.page = page

    async def validate_selector(self, selector_data: dict) -> bool:
        """验证选择器的有效性"""
        try:
            element = await self.page.query_selector(selector_data['value'])
            return element is not None
        except Exception:
            return False

    async def validate_uniqueness(self, selector_data: dict) -> bool:
        """验证选择器的唯一性"""
        elements = await self.page.query_selector_all(selector_data['value'])
        return len(elements) == 1
```

## 四、数据库集成

### 4.1 选择器存储
```sql
-- 选择器历史表
CREATE TABLE selector_history (
    id SERIAL PRIMARY KEY,
    selector_id INTEGER REFERENCES selectors(id),
    selector_value TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    success_rate FLOAT DEFAULT 0,
    is_active BOOLEAN DEFAULT true
);
```

### 4.2 选择器更新
```python
class SelectorUpdater:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    async def update_selector(self, selector_id: int, new_value: str):
        """更新选择器"""
        await self.db_manager.execute("""
            UPDATE selectors 
            SET selector_value = $1, updated_at = CURRENT_TIMESTAMP
            WHERE id = $2
        """, (new_value, selector_id))
```

## 五、错误处理

### 5.1 异常定义
```python
class SelectorError(Exception):
    """选择器相关错误的基类"""
    pass

class SelectorNotFoundError(SelectorError):
    """选择器未找到元素"""
    pass

class SelectorTimeoutError(SelectorError):
    """选择器等待超时"""
    pass
```

### 5.2 错误恢复策略
```python
async def handle_selector_error(error: SelectorError, selector_data: dict):
    """处理选择器错误"""
    if isinstance(error, SelectorNotFoundError):
        # 尝试更新选择器
        new_selector = await selector_generator.generate_selectors(
            selector_data['target_element']
        )
        if new_selector:
            await selector_updater.update_selector(
                selector_data['id'],
                new_selector[0][1]
            )
```