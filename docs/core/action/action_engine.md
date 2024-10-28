 # 动作引擎设计文档

## 一、模块概述

动作引擎负责执行网页操作，支持各种交互类型，并提供可扩展的动作处理系统。

### 1.1 主要功能
- 标准动作执行
- 自定义动作支持
- 动作验证和重试
- 动作序列管理
- 条件判断和循环

### 1.2 依赖组件
- 选择器引擎
- 数据库模块
- 错误处理模块

## 二、核心组件

### 2.1 动作执行器
```python
class ActionExecutor:
    def __init__(self, page, selector_engine):
        self.page = page
        self.selector_engine = selector_engine
        self.handlers = {}

    async def execute_action(self, action_data: dict):
        """执行单个动作"""
        handler = self.get_handler(action_data['type'])
        if not handler:
            raise ActionError(f"Unknown action type: {action_data['type']}")
            
        return await handler.execute(action_data)

    async def execute_sequence(self, actions: list):
        """执行动作序列"""
        results = []
        for action in actions:
            try:
                result = await self.execute_action(action)
                results.append(result)
            except ActionError as e:
                await self.handle_action_error(e, action)
                raise
        return results
```

### 2.2 动作处理器基类
```python
class BaseActionHandler:
    def __init__(self, page, selector_engine):
        self.page = page
        self.selector_engine = selector_engine

    async def execute(self, action_data: dict):
        """执行动作"""
        raise NotImplementedError

    async def validate(self, action_data: dict):
        """验证动作参数"""
        raise NotImplementedError

    async def cleanup(self):
        """清理资源"""
        pass
```

### 2.3 标准动作处理器
```python
class ClickHandler(BaseActionHandler):
    async def execute(self, action_data: dict):
        element = await self.selector_engine.find_element(
            action_data['selector']
        )
        await element.click()

class InputHandler(BaseActionHandler):
    async def execute(self, action_data: dict):
        element = await self.selector_engine.find_element(
            action_data['selector']
        )
        await element.fill(action_data['value'])
```

## 三、动作验证

### 3.1 参数验证器
```python
class ActionValidator:
    def __init__(self):
        self.schemas = {}

    def register_schema(self, action_type: str, schema: dict):
        """注册动作参数模式"""
        self.schemas[action_type] = schema

    async def validate(self, action_data: dict):
        """验证动作参数"""
        schema = self.schemas.get(action_data['type'])
        if not schema:
            raise ValidationError(f"No schema for action type: {action_data['type']}")
            
        return validate_against_schema(action_data, schema)
```

### 3.2 动作结果验证
```python
class ActionResultValidator:
    def __init__(self, page):
        self.page = page

    async def validate_result(self, action_data: dict, result: any):
        """验证动作执行结果"""
        if 'expected_result' in action_data:
            actual = await self.get_actual_result(action_data)
            return self.compare_results(actual, action_data['expected_result'])
        return True
```

## 四、错误处理

### 4.1 异常定义
```python
class ActionError(Exception):
    """动作相关错误的基类"""
    pass

class ValidationError(ActionError):
    """参数验证错误"""
    pass

class ExecutionError(ActionError):
    """执行错误"""
    pass
```

### 4.2 重试机制
```python
class ActionRetry:
    def __init__(self, max_retries=3, delay=1):
        self.max_retries = max_retries
        self.delay = delay

    async def retry_action(self, action_executor, action_data):
        """重试执行动作"""
        for attempt in range(self.max_retries):
            try:
                return await action_executor.execute_action(action_data)
            except ActionError as e:
                if attempt == self.max_retries - 1:
                    raise
                await asyncio.sleep(self.delay * (attempt + 1))
```

## 五、动作序列管理

### 5.1 序列执行器
```python
class SequenceExecutor:
    def __init__(self, action_executor):
        self.action_executor = action_executor
        self.current_sequence = None

    async def execute_sequence(self, sequence_data: dict):
        """执行动作序列"""
        self.current_sequence = sequence_data
        results = []
        
        for action in sequence_data['actions']:
            if await self.should_execute(action):
                result = await self.action_executor.execute_action(action)
                results.append(result)
                
                if not await self.should_continue(result):
                    break
                    
        return results
```

### 5.2 条件控制
```python
class ConditionalExecutor:
    def __init__(self, page):
        self.page = page

    async def evaluate_condition(self, condition: dict) -> bool:
        """评估条件"""
        if condition['type'] == 'element_exists':
            return await self.page.query_selector(condition['selector']) is not None
        elif condition['type'] == 'element_visible':
            element = await self.page.query_selector(condition['selector'])
            return element and await element.is_visible()
        # 其他条件类型...
        return False
```

## 六、性能优化

### 6.1 并行执行
```python
class ParallelExecutor:
    def __init__(self, max_workers=5):
        self.max_workers = max_workers

    async def execute_parallel(self, actions: list):
        """并行执行动作"""
        async with asyncio.Semaphore(self.max_workers):
            tasks = [
                self.action_executor.execute_action(action)
                for action in actions
            ]
            return await asyncio.gather(*tasks)
```

### 6.2 动作缓存
```python
class ActionCache:
    def __init__(self):
        self.cache = {}

    def cache_action_result(self, action_data: dict, result: any):
        """缓存动作结果"""
        cache_key = self.generate_cache_key(action_data)
        self.cache[cache_key] = {
            'result': result,
            'timestamp': time.time()
        }

    def get_cached_result(self, action_data: dict):
        """获取缓存的结果"""
        cache_key = self.generate_cache_key(action_data)
        cached = self.cache.get(cache_key)
        if cached and time.time() - cached['timestamp'] < 300:  # 5分钟过期
            return cached['result']
        return None
```

## 七、监控和日志

### 7.1 性能监控
```python
class ActionMetrics:
    def __init__(self):
        self.metrics = defaultdict(list)

    def record_execution_time(self, action_type: str, duration: float):
        """记录执行时间"""
        self.metrics[action_type].append({
            'duration': duration,
            'timestamp': datetime.now()
        })

    def get_average_duration(self, action_type: str) -> float:
        """获取平均执行时间"""
        durations = [m['duration'] for m in self.metrics[action_type]]
        return sum(durations) / len(durations) if durations else 0
```

### 7.2 日志记录
```python
class ActionLogger:
    def __init__(self):
        self.logger = logging.getLogger('action_engine')

    def log_action_start(self, action_data: dict):
        """记录动作开始"""
        self.logger.info(f"Starting action: {action_data['type']}", extra={
            'action_data': action_data
        })

    def log_action_complete(self, action_data: dict, result: any):
        """记录动作完成"""
        self.logger.info(f"Completed action: {action_data['type']}", extra={
            'action_data': action_data,
            'result': result
        })
```