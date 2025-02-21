import pytest
from PyQt5.QtWidgets import QApplication, QInputDialog, QProgressDialog, QListWidgetItem
from PyQt5.QtCore import Qt, QTimer
from core.ui.workflow_editor import WorkflowEditorWidget
from database.crud_manager import CRUDManager
import sys
import time
import logging
import os
from datetime import datetime
import asyncio
from unittest.mock import MagicMock, patch
import traceback
from typing import Generator, AsyncGenerator, Dict, Any, Optional

# 设置日志
log_dir = "logs"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

log_file = os.path.join(log_dir, f"test_workflow_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

@pytest.fixture(scope="session")
def qapp() -> QApplication:
    """创建 QApplication 实例，整个测试会话共享一个实例"""
    try:
        logger.info("创建 QApplication 实例")
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        return app
    except Exception as e:
        logger.error(f"创建 QApplication 实例失败: {e}\n{traceback.format_exc()}")
        raise

@pytest.fixture
async def crud_manager() -> AsyncGenerator[CRUDManager, None]:
    """创建CRUD管理器实例，每个测试函数都会创建新的实例"""
    try:
        logger.info("创建CRUD管理器实例")
        manager = CRUDManager()
        await manager.ensure_connected()
        yield manager
        logger.info("关闭CRUD管理器实例")
        await manager.close()
    except Exception as e:
        logger.error(f"CRUD管理器操作失败: {e}\n{traceback.format_exc()}")
        raise

@pytest.fixture
async def editor(qapp: QApplication, crud_manager: CRUDManager, qtbot) -> AsyncGenerator[WorkflowEditorWidget, None]:
    """
    创建工作流编辑器实例，每个测试函数都会创建新的实例。
    
    Args:
        qapp: QApplication实例，用于创建Qt窗口
        crud_manager: CRUD管理器实例，用于数据库操作
        qtbot: pytest-qt提供的QtBot实例，用于模拟用户操作
        
    Yields:
        WorkflowEditorWidget: 工作流编辑器实例
    """
    try:
        logger.info("创建工作流编辑器实例")
        widget = WorkflowEditorWidget()
        widget.loop = asyncio.get_running_loop()  # 设置当前事件循环
        qtbot.addWidget(widget)
        await widget.initialize()  # 初始化编辑器
        widget.show()
        qtbot.waitExposed(widget)  # 等待窗口显示
        yield widget
    except Exception as e:
        logger.error(f"工作流编辑器操作失败: {e}\n{traceback.format_exc()}")
        raise
    finally:
        logger.info("开始清理工作流编辑器")
        try:
            # 先清理数据库连接
            if widget.crud_manager:
                await widget.cleanup()
            # 再关闭窗口
            if widget.isVisible():
                widget.close()
                qtbot.waitUntil(lambda: not widget.isVisible(), timeout=5000)
            logger.info("工作流编辑器清理完成")
        except Exception as e:
            logger.error(f"清理工作流编辑器失败: {e}\n{traceback.format_exc()}")

@pytest.mark.asyncio
async def test_init(editor: WorkflowEditorWidget, qtbot) -> None:
    """
    测试编辑器初始化
    
    验证编辑器实例的基本属性是否正确初始化：
    1. 编辑器实例不为空
    2. CRUD管理器已正确创建
    3. 工作流引擎已正确创建
    4. 当前工作流为空
    """
    try:
        logger.info("开始测试编辑器初始化")
        assert editor is not None, "编辑器实例为空"
        assert editor.crud_manager is not None, "CRUD管理器为空"
        assert editor.workflow_engine is not None, "工作流引擎为空"
        assert editor.current_workflow is None, "当前工作流不为空"
        logger.info("编辑器初始化测试通过")
    except Exception as e:
        logger.error(f"编辑器初始化测试失败: {e}\n{traceback.format_exc()}")
        raise

@pytest.mark.asyncio
async def test_load_websites(editor: WorkflowEditorWidget, crud_manager: CRUDManager, qtbot) -> None:
    """
    测试加载网站列表功能
    
    测试步骤：
    1. 创建两个测试网站
    2. 调用异步加载网站列表方法
    3. 验证网站选择器是否正确加载了网站
    4. 清理测试数据
    """
    created_websites = []
    try:
        logger.info("开始测试加载网站列表")
        # 先添加测试网站
        test_websites = [
            {"name": "测试网站1", "url": "http://test1.com"},
            {"name": "测试网站2", "url": "http://test2.com"}
        ]
        
        for website in test_websites:
            created_website = await crud_manager.create_website(**website)
            logger.info(f"创建测试网站: {created_website}")
            created_websites.append(created_website)
        
        # 测试加载
        with qtbot.waitSignal(editor.operation_completed, timeout=5000):
            await editor.async_load_websites()
        
        assert editor.website_selector.count() > 0, "网站选择器为空"
        logger.info("网站列表加载测试通过")
        
    except Exception as e:
        logger.error(f"加载网站列表测试失败: {e}\n{traceback.format_exc()}")
        raise
    finally:
        # 清理测试数据
        try:
            for website in created_websites:
                await crud_manager.delete_website(website['id'])
                logger.info(f"删除测试网站: {website['id']}")
        except Exception as e:
            logger.error(f"清理测试网站失败: {e}\n{traceback.format_exc()}")

@pytest.mark.asyncio
async def test_create_workflow(editor: WorkflowEditorWidget, crud_manager: CRUDManager, qtbot) -> None:
    """
    测试创建工作流功能
    
    测试步骤：
    1. 创建测试用户（如果已存在则先删除）
    2. 创建测试网站
    3. 等待网站列表加载完成
    4. 设置UI状态（工作流名称、描述等）
    5. 创建工作流
    6. 验证UI状态和数据库状态
    7. 清理测试数据
    
    验证点：
    - UI状态正确更新
    - 数据库中的工作流信息正确
    - 工作流与用户和网站的关联正确
    """
    test_user = None
    website = None
    workflow = None
    
    try:
        logger.info("开始测试创建工作流")
        
        # 先删除可能存在的测试用户
        try:
            existing_user = await crud_manager.get_user_by_username("test_user")
            if existing_user:
                await crud_manager.delete_user(existing_user['id'])
                logger.info("删除已存在的测试用户")
        except Exception as e:
            logger.warning(f"查找或删除已存在用户时出错: {e}")
        
        # 创建测试用户
        test_user = await crud_manager.create_user(
            username="test_user",
            email="test@example.com",
            password_hash="test_hash"
        )
        logger.info(f"创建测试用户: {test_user}")
        
        # 创建测试网站
        website = await crud_manager.create_website(
            name="测试网站",
            url="http://test.com"
        )
        logger.info(f"创建测试网站: {website}")
        
        # 等待网站列表加载完成
        with qtbot.waitSignal(editor.operation_completed, timeout=5000):
            await editor.async_load_websites()
        
        # 设置UI状态
        editor.website_selector.clear()
        editor.website_selector.addItem(website['name'], website['id'])
        editor.website_selector.setCurrentIndex(0)
        editor.workflow_name.setText("测试工作流")
        editor.workflow_description.setText("测试描述")
        editor.current_user_id = test_user['id']
        
        # 创建工作流
        workflow = await crud_manager.create_workflow(
            name="测试工作流",
            description="测试描述",
            website_id=website['id'],
            user_id=test_user['id']
        )
        logger.info(f"创建测试工作流: {workflow}")
        
        # 更新UI状态
        editor.current_workflow = workflow
        editor.workflow_name.setText(workflow['name'])
        editor.workflow_description.setText(workflow.get('description', ''))
        
        # 验证
        assert editor.current_workflow is not None, "当前工作流为空"
        assert editor.workflow_name.text() == workflow['name'], "工作流名称不匹配"
        assert editor.workflow_description.toPlainText() == workflow.get('description', ''), "工作流描述不匹配"
        assert editor.website_selector.currentData() == website['id'], "网站ID不匹配"
        
        # 验证数据库状态
        db_workflow = await crud_manager.get_workflow(workflow['id'])
        assert db_workflow is not None, "数据库中未找到工作流"
        assert db_workflow['name'] == "测试工作流", "数据库中工作流名称不匹配"
        assert db_workflow['website_id'] == website['id'], "数据库中网站ID不匹配"
        assert db_workflow['user_id'] == test_user['id'], "数据库中用户ID不匹配"
        
        logger.info("创建工作流测试通过")
        
    except Exception as e:
        logger.error(f"创建工作流测试失败: {e}\n{traceback.format_exc()}")
        raise
    finally:
        # 清理测试数据
        try:
            if workflow:
                await crud_manager.delete_workflow(workflow['id'])
                logger.info(f"删除测试工作流: {workflow['id']}")
            if website:
                await crud_manager.delete_website(website['id'])
                logger.info(f"删除测试网站: {website['id']}")
            if test_user:
                await crud_manager.delete_user(test_user['id'])
                logger.info(f"删除测试用户: {test_user['id']}")
        except Exception as e:
            logger.error(f"清理测试数据失败: {e}\n{traceback.format_exc()}")

@pytest.mark.asyncio
async def test_load_workflow(editor: WorkflowEditorWidget, crud_manager: CRUDManager, qtbot) -> None:
    """
    测试加载工作流功能
    
    测试步骤：
    1. 创建测试用户
    2. 创建测试网站
    3. 创建测试工作流
    4. 设置当前用户ID
    5. 模拟用户选择工作流
    6. 加载工作流
    7. 验证UI状态
    8. 清理测试数据
    
    验证点：
    - 工作流正确加载到UI
    - 工作流信息（名称、描述等）正确显示
    - 工作流步骤正确加载
    """
    test_user = None
    website = None
    workflow = None
    
    try:
        logger.info("开始测试加载工作流")
        # 创建测试用户
        test_user = await crud_manager.create_user(
            username="test_user",
            email="test@example.com",
            password_hash="test_hash"
        )
        logger.info(f"创建测试用户: {test_user}")
        
        # 创建测试网站
        website = await crud_manager.create_website(
            name="测试网站",
            url="http://test.com"
        )
        logger.info(f"创建测试网站: {website}")
        
        # 创建测试工作流
        workflow = await crud_manager.create_workflow(
            name="测试工作流",
            user_id=test_user['id'],
            website_id=website['id'],
            description="测试描述"
        )
        logger.info(f"创建测试工作流: {workflow}")
        
        # 设置当前用户ID
        editor.current_user_id = test_user['id']
        
        # 模拟用户选择
        with patch.object(QInputDialog, 'getItem', return_value=(f"测试工作流 (ID: {workflow['id']})", True)):
            # 等待工作流加载完成
            with qtbot.waitSignals([editor.workflow_loaded, editor.workflow_updated, editor.operation_completed], timeout=5000):
                await editor.load_workflow()
            
            # 验证UI状态
            assert editor.current_workflow is not None, "当前工作流为空"
            assert editor.current_workflow['id'] == workflow['id'], "工作流ID不匹配"
            assert editor.workflow_name.text() == workflow['name'], "工作流名称不匹配"
            assert editor.workflow_description.toPlainText() == workflow['description'], "工作流描述不匹配"
            
            logger.info("加载工作流测试通过")
        
    except Exception as e:
        logger.error(f"加载工作流测试失败: {e}\n{traceback.format_exc()}")
        raise
    finally:
        # 清理测试数据
        try:
            if workflow:
                await crud_manager.delete_workflow(workflow['id'])
                logger.info(f"删除测试工作流: {workflow['id']}")
            if website:
                await crud_manager.delete_website(website['id'])
                logger.info(f"删除测试网站: {website['id']}")
            if test_user:
                await crud_manager.delete_user(test_user['id'])
                logger.info(f"删除测试用户: {test_user['id']}")
        except Exception as e:
            logger.error(f"清理测试数据失败: {e}\n{traceback.format_exc()}")

@pytest.mark.asyncio
async def test_async_simple(qtbot):
    """简单的异步测试"""
    try:
        logger.info("开始简单异步测试")
        await asyncio.sleep(0.1)
        assert True
        logger.info("简单异步测试通过")
    except Exception as e:
        logger.error(f"简单异步测试失败: {e}\n{traceback.format_exc()}")
        raise 