# 数据处理模块设计

## 一、数据处理架构

### 1.1 项目结构
```
data_processor/
├── __init__.py
├── core/
│   ├── __init__.py
│   ├── processor_manager.py    # 处理器管理
│   └── pipeline.py            # 处理管道
├── processors/
│   ├── __init__.py
│   ├── base_processor.py      # 基础处理器
│   ├── text/                  # 文本处理器
│   │   ├── __init__.py
│   │   ├── html_cleaner.py
│   │   └── text_normalizer.py
│   ├── image/                 # 图片处理器
│   │   ├── __init__.py
│   │   ├── image_downloader.py
│   │   └── image_converter.py
│   └── file/                  # 文件处理器
│       ├── __init__.py
│       ├── pdf_processor.py
│       └── excel_processor.py
└── storage/                   # 存储管理
    ├── __init__.py
    └── storage_manager.py
```

### 1.2 数据库设计
```sql
-- 处理器类型表
CREATE TABLE processor_types (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    handler_class VARCHAR(100) NOT NULL,
    parameters_schema JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 处理管道表
CREATE TABLE processing_pipelines (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    steps JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 处理结果表
CREATE TABLE processed_data (
    id SERIAL PRIMARY KEY,
    source_id INTEGER,         -- 关联到源数据
    pipeline_id INTEGER REFERENCES processing_pipelines(id),
    result_data JSONB,        -- 处理结果
    storage_path TEXT,        -- 文件存储路径
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 二、核心组件

### 2.1 基础处理器
```python
class BaseProcessor:
    def __init__(self, config=None):
        self.config = config or {}

    async def process(self, data):
        """处理数据"""
        raise NotImplementedError

    @classmethod
    def get_schema(cls):
        """返回配置模式"""
        return {}

    async def validate_config(self):
        """验证配置"""
        pass
```

### 2.2 处理管道
```python
class ProcessingPipeline:
    def __init__(self, steps):
        self.steps = steps
        self.processors = []

    async def init_processors(self):
        """初始化处理器链"""
        for step in self.steps:
            processor_class = ProcessorRegistry.get(step['type'])
            processor = processor_class(step.get('config'))
            self.processors.append(processor)

    async def process(self, data):
        """执行处理流程"""
        result = data
        for processor in self.processors:
            result = await processor.process(result)
        return result
```

## 三、处理器实现示例

### 3.1 文本处理器
```python
class HTMLCleaner(BaseProcessor):
    async def process(self, html_content):
        """清理HTML内容"""
        soup = BeautifulSoup(html_content, 'html.parser')
        # 移除脚本和样式
        for script in soup(["script", "style"]):
            script.decompose()
        return soup.get_text()

class TextNormalizer(BaseProcessor):
    async def process(self, text):
        """标准化文本"""
        # 去除多余空白
        text = ' '.join(text.split())
        # 其他标准化操作
        return text
```

### 3.2 图片处理器
```python
class ImageDownloader(BaseProcessor):
    async def process(self, image_url):
        """下载图片"""
        async with aiohttp.ClientSession() as session:
            async with session.get(image_url) as response:
                if response.status == 200:
                    content = await response.read()
                    return await self._save_image(content)
                raise ProcessingError(f"Failed to download image: {image_url}")

    async def _save_image(self, content):
        """保存图片"""
        filename = f"{uuid.uuid4()}.jpg"
        storage_path = f"images/{filename}"
        await StorageManager.save(storage_path, content)
        return storage_path
```

### 3.3 文件处理器
```python
class PDFProcessor(BaseProcessor):
    async def process(self, pdf_path):
        """处理PDF文件"""
        text = await self._extract_text(pdf_path)
        return await self._process_text(text)

    async def _extract_text(self, pdf_path):
        """提取PDF文本"""
        # 使用 pdfplumber 或其他库提取文本
        pass

    async def _process_text(self, text):
        """处理提取的文本"""
        pass
```

## 四、存储管理

### 4.1 存储管理器
```python
class StorageManager:
    def __init__(self, base_path):
        self.base_path = base_path

    async def save(self, path, content):
        """保存内容"""
        full_path = os.path.join(self.base_path, path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        
        if isinstance(content, bytes):
            mode = 'wb'
        else:
            mode = 'w'
            
        async with aiofiles.open(full_path, mode) as f:
            await f
```