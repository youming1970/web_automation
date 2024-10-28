# 核心工具模块设计文档

## 一、配置管理

### 1.1 配置结构
```python
class Config:
    DEFAULT_CONFIG = {
        'browser': {
            'headless': True,
            'slow_mo': 50,
            'timeout': 30000
        },
        'storage': {
            'data_dir': './data',
            'backup_dir': './backup'
        },
        'database': {
            'host': 'localhost',
            'port': 5432,
            'database': 'web_automation',
            'user': 'poording'
        },
        'logging': {
            'level': 'INFO',
            'file': 'automation.log'
        }
    }

    def __init__(self):
        self.config = self.load_config()

    def load_config(self):
        """加载配置文件"""
        try:
            with open('config.json', 'r') as f:
                user_config = json.load(f)
            return deep_update(self.DEFAULT_CONFIG, user_config)
        except FileNotFoundError:
            return self.DEFAULT_CONFIG
```

### 1.2 用户配置界面
```python
class ConfigUI:
    def __init__(self, config: Config):
        self.config = config

    def show_dialog(self):
        """显示配置对话框"""
        # 使用PyQt5创建简单的配置界面
        pass

    def save_config(self):
        """保存配置"""
        with open('config.json', 'w') as f:
            json.dump(self.config.config, f, indent=4)
```

## 二、错误处理

### 2.1 错误管理器
```python
class ErrorManager:
    def __init__(self):
        self.logger = logging.getLogger('error_manager')
        self.error_count = defaultdict(int)

    async def handle_error(self, error: Exception, context: dict):
        """处理错误"""
        error_type = type(error).__name__
        self.error_count[error_type] += 1

        # 记录错误
        self.logger.error(f"Error occurred: {str(error)}", 
                         exc_info=True, 
                         extra=context)

        # 简单的重试逻辑
        if self.error_count[error_type] < 3:
            return 'retry'
        return 'abort'

    def show_error_dialog(self, error: Exception):
        """显示错误对话框"""
        # 使用PyQt5显示用户友好的错误信息
        pass
```

## 三、日志系统

### 3.1 日志管理器
```python
class LogManager:
    def __init__(self, config: Config):
        self.config = config
        self.setup_logging()

    def setup_logging(self):
        """配置日志系统"""
        logging.basicConfig(
            level=self.config.config['logging']['level'],
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            filename=self.config.config['logging']['file']
        )

    def get_logger(self, name: str):
        """获取logger"""
        return logging.getLogger(name)

    def show_logs(self):
        """显示日志查看器"""
        # 简单的日志查看界面
        pass
```

## 四、数据备份

### 4.1 备份管理器
```python
class BackupManager:
    def __init__(self, config: Config):
        self.config = config
        self.backup_dir = Path(config.config['storage']['backup_dir'])
        self.backup_dir.mkdir(parents=True, exist_ok=True)

    async def create_backup(self):
        """创建备份"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = self.backup_dir / f'backup_{timestamp}.zip'
        
        # 备份数据库
        await self.backup_database()
        
        # 备份配置和数据文件
        self.backup_files()

    async def restore_backup(self, backup_file: str):
        """恢复备份"""
        # 实现备份恢复逻辑
        pass
```