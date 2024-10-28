# 数据处理模块设计文档

## 一、模块概述

数据处理模块负责对抓取的数据进行处理、转换、清洗和存储，支持多种数据类型和处理方式。

### 1.1 主要功能
- 数据提取和解析
- 数据清洗和转换
- 数据验证和格式化
- 数据存储和导出
- 处理管道管理

### 1.2 支持的数据类型
- 文本数据
- HTML内容
- 表格数据
- 图片数据
- JSON/XML数据
- 文件下载

## 二、核心组件

### 2.1 数据处理器基类
```python
class BaseDataProcessor:
    def __init__(self, config: dict = None):
        self.config = config or {}
        self.validators = []
        self.transformers = []

    async def process(self, data: Any) -> Any:
        """处理数据的主方法"""
        try:
            # 验证输入数据
            await self.validate(data)
            
            # 转换数据
            processed_data = await self.transform(data)
            
            # 验证输出数据
            await self.validate_output(processed_data)
            
            return processed_data
        except ProcessorError as e:
            await self.handle_error(e)
            raise

    async def validate(self, data: Any) -> bool:
        """验证输入数据"""
        for validator in self.validators:
            if not await validator.validate(data):
                raise ValidationError(f"Data validation failed: {validator}")
        return True

    async def transform(self, data: Any) -> Any:
        """转换数据"""
        result = data
        for transformer in self.transformers:
            result = await transformer.transform(result)
        return result
```

### 2.2 专用处理器
```python
class HTMLProcessor(BaseDataProcessor):
    async def transform(self, html: str) -> dict:
        """处理HTML内容"""
        soup = BeautifulSoup(html, 'html.parser')
        return {
            'text': soup.get_text(),
            'links': [a['href'] for a in soup.find_all('a', href=True)],
            'images': [img['src'] for img in soup.find_all('img', src=True)]
        }

class TableProcessor(BaseDataProcessor):
    async def transform(self, table_element) -> pd.DataFrame:
        """处理表格数据"""
        rows = []
        headers = []
        # 提取表格数据
        # 转换为DataFrame
        return pd.DataFrame(rows, columns=headers)

class ImageProcessor(BaseDataProcessor):
    async def transform(self, image_data: bytes) -> dict:
        """处理图片数据"""
        image = Image.open(io.BytesIO(image_data))
        return {
            'format': image.format,
            'size': image.size,
            'mode': image.mode
        }
```

### 2.3 处理管道
```python
class ProcessingPipeline:
    def __init__(self):
        self.steps = []
        self.error_handlers = {}

    def add_step(self, processor: BaseDataProcessor, error_handler=None):
        """添加处理步骤"""
        self.steps.append(processor)
        if error_handler:
            self.error_handlers[processor] = error_handler

    async def execute(self, data: Any) -> Any:
        """执行处理管道"""
        result = data
        for step in self.steps:
            try:
                result = await step.process(result)
            except Exception as e:
                handler = self.error_handlers.get(step)
                if handler:
                    result = await handler(e, result)
                else:
                    raise
        return result
```

## 三、数据存储

### 3.1 存储管理器
```python
class StorageManager:
    def __init__(self, config: dict):
        self.config = config
        self.db_manager = DatabaseManager()
        self.file_manager = FileManager()

    async def store_data(self, data: Any, storage_type: str):
        """存储数据"""
        if storage_type == 'database':
            return await self.db_manager.store(data)
        elif storage_type == 'file':
            return await self.file_manager.store(data)
        else:
            raise StorageError(f"Unknown storage type: {storage_type}")

class FileManager:
    def __init__(self, base_path: str = './data'):
        self.base_path = base_path

    async def store(self, data: Any, filename: str):
        """存储文件"""
        full_path = os.path.join(self.base_path, filename)
        async with aiofiles.open(full_path, 'wb') as f:
            await f.write(data)
        return full_path
```

### 3.2 数据导出
```python
class DataExporter:
    def __init__(self):
        self.exporters = {}

    def register_exporter(self, format_type: str, exporter):
        """注册导出器"""
        self.exporters[format_type] = exporter

    async def export_data(self, data: Any, format_type: str):
        """导出数据"""
        exporter = self.exporters.get(format_type)
        if not exporter:
            raise ExportError(f"No exporter for format: {format_type}")
        return await exporter.export(data)

class CSVExporter:
    async def export(self, data: pd.DataFrame) -> str:
        """导出为CSV"""
        buffer = io.StringIO()
        data.to_csv(buffer, index=False)
        return buffer.getvalue()
```

## 四、数据验证

### 4.1 验证器
```python
class DataValidator:
    def __init__(self, schema: dict):
        self.schema = schema

    async def validate(self, data: Any) -> bool:
        """验证数据"""
        try:
            jsonschema.validate(instance=data, schema=self.schema)
            return True
        except jsonschema.exceptions.ValidationError as e:
            raise ValidationError(str(e))

class CustomValidator:
    def __init__(self, validation_func):
        self.validation_func = validation_func

    async def validate(self, data: Any) -> bool:
        """自定义验证"""
        return await self.validation_func(data)
```

### 4.2 数据清洗
```python
class DataCleaner:
    def __init__(self):
        self.cleaning_rules = []

    def add_rule(self, rule):
        """添加清洗规则"""
        self.cleaning_rules.append(rule)

    async def clean(self, data: Any) -> Any:
        """清洗数据"""
        result = data
        for rule in self.cleaning_rules:
            result = await rule(result)
        return result
```

## 五、错误处理

### 5.1 异常定义
```python
class ProcessorError(Exception):
    """处理器相关错误的基类"""
    pass

class ValidationError(ProcessorError):
    """数据验证错误"""
    pass

class TransformError(ProcessorError):
    """数据转换错误"""
    pass

class StorageError(ProcessorError):
    """存储错误"""
    pass
```

### 5.2 错误恢复
```python
class ErrorRecovery:
    def __init__(self):
        self.recovery_strategies = {}

    def register_strategy(self, error_type: type, strategy):
        """注册恢复策略"""
        self.recovery_strategies[error_type] = strategy

    async def recover(self, error: Exception, data: Any) -> Any:
        """执行恢复策略"""
        strategy = self.recovery_strategies.get(type(error))
        if strategy:
            return await strategy(error, data)
        raise error
```

## 六、性能优化

### 6.1 批处理
```python
class BatchProcessor:
    def __init__(self, processor: BaseDataProcessor, batch_size: int = 100):
        self.processor = processor
        self.batch_size = batch_size

    async def process_batch(self, items: list) -> list:
        """批量处理数据"""
        results = []
        for i in range(0, len(items), self.batch_size):
            batch = items[i:i + self.batch_size]
            batch_results = await asyncio.gather(
                *[self.processor.process(item) for item in batch]
            )
            results.extend(batch_results)
        return results
```

### 6.2 缓存机制
```python
class ProcessorCache:
    def __init__(self, max_size: int = 1000):
        self.cache = {}
        self.max_size = max_size

    async def get_or_process(self, data: Any, processor: BaseDataProcessor):
        """获取缓存或处理数据"""
        cache_key = self._generate_key(data)
        if cache_key in self.cache:
            return self.cache[cache_key]

        result = await processor.process(data)
        self._update_cache(cache_key, result)
        return result

    def _update_cache(self, key: str, value: Any):
        """更新缓存"""
        if len(self.cache) >= self.max_size:
            # 移除最旧的项
            self.cache.pop(next(iter(self.cache)))
        self.cache[key] = value
```

## 七、监控和日志

### 7.1 性能监控
```python
class ProcessorMetrics:
    def __init__(self):
        self.metrics = defaultdict(list)

    def record_processing_time(self, processor_type: str, duration: float):
        """记录处理时间"""
        self.metrics[processor_type].append({
            'duration': duration,
            'timestamp': datetime.now()
        })

    def get_statistics(self, processor_type: str) -> dict:
        """获取统计信息"""
        durations = [m['duration'] for m in self.metrics[processor_type]]
        return {
            'avg_duration': sum(durations) / len(durations),
            'max_duration': max(durations),
            'min_duration': min(durations),
            'total_processed': len(durations)
        }
```

### 7.2 日志记录
```python
class ProcessorLogger:
    def __init__(self):
        self.logger = logging.getLogger('data_processor')

    def log_processing_start(self, data_type: str, size: int):
        """记录处理开始"""
        self.logger.info(f"Starting processing {data_type}", extra={
            'data_type': data_type,
            'size': size
        })

    def log_processing_complete(self, data_type: str, result: Any):
        """记录处理完成"""
        self.logger.info(f"Completed processing {data_type}", extra={
            'data_type': data_type,
            'result_size': len(str(result))
        })
```

## 八、使用示例

### 8.1 基本使用
```python
async def process_webpage_data():
    # 创建处理管道
    pipeline = ProcessingPipeline()
    
    # 添加处理步骤
    pipeline.add_step(HTMLProcessor())
    pipeline.add_step(DataCleaner())
    pipeline.add_step(CustomValidator(validate_content))
    
    # 处理数据
    html_content = await fetch_webpage()
    result = await pipeline.execute(html_content)
    
    # 存储结果
    storage = StorageManager(config={})
    await storage.store_data(result, 'database')
```

### 8.2 批量处理
```python
async def process_multiple_pages(urls: list):
    processor = HTMLProcessor()
    batch_processor = BatchProcessor(processor)
    
    # 获取页面内容
    pages_content = await fetch_multiple_pages(urls)
    
    # 批量处理
    results = await batch_processor.process_batch(pages_content)
    
    # 导出结果
    exporter = DataExporter()
    csv_data = await exporter.export_data(results, 'csv')
    return csv_data
```