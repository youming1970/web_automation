# Web Survey Automation Tool

这是一个用于自动化网上调查的工具，使用 PostgreSQL、Python 和 PyQt5 实现。该工具提供了图形用户界面，支持工作流的创建、编辑和执行。

## 项目结构
```
web_automation/
├── core/
│   ├── components/       # 核心组件
│   │   ├── action/      # 动作执行相关代码
│   │   ├── selector/    # 选择器引擎相关代码
│   │   ├── browser/     # 浏览器管理器相关代码
│   │   ├── workflow/    # 工作流引擎相关代码
│   │   └── processor/   # 数据处理器相关代码
│   └── ui/             # 用户界面组件
│       └── workflow_editor.py  # 工作流编辑器
├── database/           # 数据库相关代码
│   ├── db_manager.py   # 数据库连接管理
│   └── crud_manager.py # CRUD操作管理
├── tests/             # 测试代码
│   └── test_workflow_editor.py # 工作流编辑器测试
└── docs/              # 项目文档
```

## 环境要求
- Python 3.12.4
- PostgreSQL 16.4
- PyQt5 5.15.11
- pytest 8.3.4
- pytest-qt 4.4.0
- pytest-asyncio 0.25.3
- asyncpg 0.29.0

## 快速开始

1. **克隆仓库**
```bash
git clone <repository-url>
cd web_automation
```

2. **安装依赖**
```bash
pip install -r requirements.txt
pip install -r requirements-test.txt  # 如果需要运行测试
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
PYTHONPATH=/path/to/web_automation pytest tests/test_workflow_editor.py -v
```

## 主要功能

### 工作流编辑器
工作流编辑器是一个图形用户界面工具，用于创建和管理自动化工作流。主要功能包括：

1. **工作流管理**
   - 创建新工作流
   - 加载已有工作流
   - 保存工作流
   - 执行工作流

2. **步骤编辑**
   - 添加步骤
   - 编辑步骤
   - 删除步骤
   - 拖拽排序

3. **支持的动作类型**
   - navigate: 导航到指定URL
   - click: 点击元素
   - input: 输入文本
   - extract_text: 提取文本
   - extract_attribute: 提取属性
   - extract_html: 提取HTML
   - extract_url: 提取URL
   - extract_multiple: 提取多个元素
   - wait: 等待
   - scroll: 滚动

### 选择器系统
支持多种选择器类型：
- CSS 选择器
- XPath 选择器
- ID 选择器
- Name 选择器
- Text 选择器

### 异步操作
- 所有数据库操作都是异步的
- UI操作与后台任务分离
- 支持长时间运行的工作流

### 错误处理和日志
- 详细的错误日志
- 操作追踪
- 异常恢复机制

## 使用示例

### 创建工作流
```python
from core.ui.workflow_editor import WorkflowEditorWidget
from PyQt5.QtWidgets import QApplication
import sys

app = QApplication(sys.argv)
editor = WorkflowEditorWidget()
await editor.initialize()
editor.show()
sys.exit(app.exec_())
```

### 数据库操作
```python
from database.crud_manager import CRUDManager

async def main():
    crud = CRUDManager()
    await crud.ensure_connected()
    
    # 创建工作流
    workflow = await crud.create_workflow(
        name="测试工作流",
        user_id=1,
        website_id=1,
        description="这是一个测试工作流"
    )
    
    # 添加步骤
    await crud.add_workflow_step(
        workflow_id=workflow['id'],
        step_order=1,
        action_type="click",
        selector_type="css",
        selector_value="#submit-button"
    )
    
    await crud.close()
```

## 开发状态

### 已完成功能
- [x] 基础数据库操作
- [x] CRUD管理器
- [x] 工作流编辑器UI
- [x] 异步操作支持
- [x] 测试框架集成
- [x] 日志系统

### 进行中
- [ ] 工作流执行引擎
- [ ] 浏览器自动化集成
- [ ] 验证码处理
- [ ] 数据导出功能

### 计划中
- [ ] 用户认证系统
- [ ] 工作流模板
- [ ] 批量操作支持
- [ ] 性能优化

## 测试
项目使用 pytest 进行测试，包括：
- 单元测试
- 集成测试
- UI测试

运行测试：
```bash
# 运行所有测试
pytest

# 运行特定测试
pytest tests/test_workflow_editor.py

# 运行特定测试函数
pytest tests/test_workflow_editor.py::test_create_workflow
```

## 贡献
欢迎提交 Issue 和 Pull Request。

## 许可证
MIT License
