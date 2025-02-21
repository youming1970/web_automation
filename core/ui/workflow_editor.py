from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem,
    QPushButton, QLabel, QLineEdit, QComboBox, QFormLayout,
    QGroupBox, QMessageBox, QInputDialog, QScrollArea, QSplitter,
    QFrame, QTextEdit, QDialog, QDialogButtonBox,
    QProgressDialog
)
from PyQt5.QtCore import Qt, pyqtSignal, QThread, QTimer
from PyQt5.QtGui import QIcon, QDragEnterEvent, QDropEvent, QCloseEvent
from database.crud_manager import CRUDManager
from core.components.workflow.workflow_engine import WorkflowEngine
from PyQt5.QtWidgets import QApplication
import asyncio
import logging
from typing import Optional, List, Dict, Any, TypeVar
from functools import partial

Event = TypeVar('Event')

class StepConfigDialog(QDialog):
    """步骤配置对话框"""
    
    def __init__(self, parent=None, step_data=None):
        super().__init__(parent)
        self.step_data = step_data or {}
        self.setup_ui()
        
    def setup_ui(self):
        self.setWindowTitle("步骤配置")
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout(self)
        
        # 步骤配置表单
        form_layout = QFormLayout()
        
        # 动作类型
        self.action_type = QComboBox()
        self.action_type.addItems([
            "navigate", "click", "input", "extract_text",
            "extract_attribute", "extract_html", "extract_url",
            "extract_multiple", "wait", "scroll"
        ])
        if self.step_data.get('action_type'):
            self.action_type.setCurrentText(self.step_data['action_type'])
        form_layout.addRow("动作类型:", self.action_type)
        
        # 选择器类型
        self.selector_type = QComboBox()
        self.selector_type.addItems(["css", "xpath", "id", "name", "text"])
        if self.step_data.get('selector_type'):
            self.selector_type.setCurrentText(self.step_data['selector_type'])
        form_layout.addRow("选择器类型:", self.selector_type)
        
        # 选择器值
        self.selector_value = QLineEdit()
        self.selector_value.setText(self.step_data.get('selector_value', ''))
        form_layout.addRow("选择器值:", self.selector_value)
        
        # 动作值
        self.action_value = QLineEdit()
        self.action_value.setText(self.step_data.get('value', ''))
        form_layout.addRow("动作值:", self.action_value)
        
        # 描述
        self.description = QTextEdit()
        self.description.setMaximumHeight(100)
        self.description.setText(self.step_data.get('description', ''))
        form_layout.addRow("描述:", self.description)
        
        layout.addLayout(form_layout)
        
        # 按钮
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
    def get_step_data(self):
        """获取步骤配置数据"""
        return {
            'action_type': self.action_type.currentText(),
            'selector_type': self.selector_type.currentText(),
            'selector_value': self.selector_value.text(),
            'value': self.action_value.text(),
            'description': self.description.toPlainText()
        }

class DraggableListWidget(QListWidget):
    """可拖拽的列表组件"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setDragDropMode(QListWidget.InternalMove)
        self.setAcceptDrops(True)
        self.setDefaultDropAction(Qt.MoveAction)
        
    def dropEvent(self, event: QDropEvent):
        super().dropEvent(event)
        # 通知父组件重新排序
        if isinstance(self.parent(), WorkflowEditorWidget):
            self.parent().reorder_steps()

class CreateWorkflowThread(QThread):
    """
    工作线程，用于在后台创建工作流，避免阻塞 UI 线程。
    """
    workflow_created_signal = pyqtSignal(dict)  # 工作流创建成功信号
    workflow_creation_failed_signal = pyqtSignal(str)  # 工作流创建失败信号

    def __init__(self, crud_manager: CRUDManager, workflow_name: str, 
                workflow_description: str, website_id: int, user_id: int) -> None:
        """
        初始化工作流创建线程
        
        Args:
            crud_manager: CRUD管理器实例
            workflow_name: 工作流名称
            workflow_description: 工作流描述
            website_id: 网站ID
            user_id: 用户ID
        """
        super().__init__()
        logging.info(f"初始化工作流创建线程: name={workflow_name}, website_id={website_id}, user_id={user_id}")
        self.crud_manager = crud_manager
        self.workflow_name = workflow_name
        self.workflow_description = workflow_description
        self.website_id = website_id
        self.user_id = user_id

    async def _create_workflow(self) -> None:
        """异步创建工作流"""
        try:
            logging.info("开始创建工作流...")
            if self.isInterruptionRequested():
                logging.info("线程已被终止")
                return

            logging.info(f"正在创建工作流: {self.workflow_name}")
            workflow = await self.crud_manager.create_workflow(
                name=self.workflow_name,
                description=self.workflow_description,
                website_id=self.website_id,
                user_id=self.user_id
            )
            logging.info(f"工作流创建成功: {workflow}")
            
            if not self.isInterruptionRequested():
                self.workflow_created_signal.emit(workflow)
            else:
                logging.info("线程已被终止，不发送成功信号")
                
        except Exception as e:
            error_msg = f"创建工作流失败: {str(e)}"
            logging.error(error_msg)
            if not self.isInterruptionRequested():
                self.workflow_creation_failed_signal.emit(error_msg)

    def run(self) -> None:
        """线程执行体"""
        asyncio.run(self._create_workflow())

    def terminate(self) -> None:
        """终止线程"""
        logging.info("正在终止工作流创建线程...")
        self.requestInterruption()
        super().terminate()

class LoadWorkflowThread(QThread):
    """工作流加载线程"""
    workflow_loaded = pyqtSignal(dict)  # 工作流加载成功信号
    workflow_load_failed = pyqtSignal(str)  # 工作流加载失败信号
    steps_loaded = pyqtSignal(list)  # 步骤加载成功信号

    def __init__(self, crud_manager: CRUDManager, workflow_id: int) -> None:
        """
        初始化工作流加载线程
        
        Args:
            crud_manager: CRUD管理器实例
            workflow_id: 工作流ID
        """
        super().__init__()
        self.crud_manager = crud_manager
        self.workflow_id = workflow_id

    async def _load_workflow(self) -> None:
        """异步加载工作流"""
        try:
            logging.info(f"开始加载工作流 {self.workflow_id}")
            
            # 加载工作流
            workflow = await self.crud_manager.get_workflow(self.workflow_id)
            if not workflow:
                raise ValueError(f"工作流 {self.workflow_id} 不存在")

            if self.isInterruptionRequested():
                logging.info("线程已被终止")
                return

            # 发送工作流加载成功信号
            self.workflow_loaded.emit(workflow)
            
            # 加载工作流步骤
            steps = await self.crud_manager.get_workflow_steps(self.workflow_id)
            if self.isInterruptionRequested():
                logging.info("线程已被终止")
                return

            # 发送步骤加载成功信号
            self.steps_loaded.emit(steps)
            logging.info(f"工作流 {self.workflow_id} 加载完成")

        except Exception as e:
            error_msg = f"加载工作流失败: {str(e)}"
            logging.error(error_msg)
            if not self.isInterruptionRequested():
                self.workflow_load_failed.emit(error_msg)

    def run(self) -> None:
        """线程执行体"""
        asyncio.run(self._load_workflow())

    def terminate(self) -> None:
        """终止线程"""
        logging.info("正在终止工作流加载线程...")
        self.requestInterruption()
        super().terminate()

class WorkflowEditorWidget(QWidget):
    """工作流编辑器组件"""
    
    workflow_updated = pyqtSignal()  # 工作流更新信号
    execution_requested = pyqtSignal(int)  # 工作流执行请求信号
    workflow_created = pyqtSignal(dict)  # 工作流创建成功的信号
    workflow_creation_failed = pyqtSignal(str)  # 工作流创建失败的信号
    workflow_loaded = pyqtSignal(dict)  # 工作流加载成功的信号
    workflow_load_failed = pyqtSignal(str)  # 工作流加载失败的信号
    operation_completed = pyqtSignal()  # 操作完成信号

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """
        初始化工作流编辑器组件
        
        Args:
            parent: 父组件
        """
        super().__init__(parent)
        self.crud_manager: Optional[CRUDManager] = None
        self.workflow_engine = WorkflowEngine()
        self.current_workflow: Optional[Dict[str, Any]] = None
        self.current_user_id: Optional[int] = None
        self._is_initialized: bool = False
        self.setup_ui()

    async def initialize(self) -> None:
        """
        异步初始化编辑器
        
        初始化数据库连接并加载网站列表
        """
        if self._is_initialized:
            return
        
        try:
            self.crud_manager = CRUDManager()
            await self.crud_manager.ensure_connected()
            # 异步加载网站列表
            await self.async_load_websites()
            self._is_initialized = True
            logging.info("编辑器初始化完成")
        except Exception as e:
            logging.error(f"初始化失败: {e}")
            raise

    def setup_ui(self) -> None:
        """设置UI布局"""
        main_layout = QVBoxLayout(self)
        
        # 工作流信息区域
        info_group = QGroupBox("工作流信息")
        info_layout = QFormLayout()
        
        self.workflow_name = QLineEdit()
        info_layout.addRow("名称:", self.workflow_name)
        
        self.workflow_description = QTextEdit()
        self.workflow_description.setMaximumHeight(60)
        info_layout.addRow("描述:", self.workflow_description)
        
        self.website_selector = QComboBox()
        info_layout.addRow("目标网站:", self.website_selector)
        
        info_group.setLayout(info_layout)
        main_layout.addWidget(info_group)
        
        # 分割器
        splitter = QSplitter(Qt.Horizontal)
        
        # 左侧：步骤列表
        steps_group = QGroupBox("工作流步骤")
        steps_layout = QVBoxLayout()
        
        self.step_list = DraggableListWidget()
        self.step_list.currentItemChanged.connect(self.on_step_selected)
        steps_layout.addWidget(self.step_list)
        
        # 步骤操作按钮
        buttons_layout = QHBoxLayout()
        
        self.add_step_button = QPushButton("添加步骤")
        self.add_step_button.clicked.connect(self.add_step)
        buttons_layout.addWidget(self.add_step_button)
        
        self.edit_step_button = QPushButton("编辑步骤")
        self.edit_step_button.clicked.connect(self.edit_step)
        buttons_layout.addWidget(self.edit_step_button)
        
        self.remove_step_button = QPushButton("删除步骤")
        self.remove_step_button.clicked.connect(self.remove_step)
        buttons_layout.addWidget(self.remove_step_button)
        
        steps_layout.addLayout(buttons_layout)
        steps_group.setLayout(steps_layout)
        splitter.addWidget(steps_group)
        
        # 右侧：步骤预览
        preview_group = QGroupBox("步骤预览")
        preview_layout = QVBoxLayout()
        
        self.step_preview = QTextEdit()
        self.step_preview.setReadOnly(True)
        preview_layout.addWidget(self.step_preview)
        
        preview_group.setLayout(preview_layout)
        splitter.addWidget(preview_group)
        
        main_layout.addWidget(splitter)
        
        # 底部按钮区域
        bottom_layout = QHBoxLayout()
        
        save_button = QPushButton("保存工作流")
        save_button.clicked.connect(self.save_workflow)
        bottom_layout.addWidget(save_button)
        
        execute_button = QPushButton("执行工作流")
        execute_button.clicked.connect(self.execute_workflow)
        bottom_layout.addWidget(execute_button)
        
        main_layout.addLayout(bottom_layout)

    async def async_load_websites(self) -> None:
        """异步加载网站列表"""
        try:
            if not self.crud_manager:
                logging.warning("CRUD管理器未初始化")
                return
            websites = await self.crud_manager.get_all_websites()
            # 在主线程中更新 UI
            self._update_website_selector(websites)
            self.operation_completed.emit()
            logging.info("网站列表加载完成")
        except Exception as e:
            logging.error(f"加载网站列表失败: {str(e)}")
            QMessageBox.warning(self, "警告", f"加载网站列表失败: {str(e)}")

    def _update_website_selector(self, websites: List[Dict[str, Any]]) -> None:
        """
        在主线程中更新网站选择器
        
        Args:
            websites: 网站列表
        """
        self.website_selector.clear()
        for website in websites:
            self.website_selector.addItem(website['name'], website['id'])

    async def save_workflow(self) -> None:
        """异步保存工作流"""
        if not self.current_workflow:
            QMessageBox.warning(self, "警告", "请先创建或加载工作流")
            return
            
        try:
            # 更新工作流基本信息
            self.current_workflow = await self.crud_manager.update_workflow(
                self.current_workflow['id'],
                name=self.workflow_name.text(),
                description=self.workflow_description.toPlainText(),
                website_id=self.website_selector.currentData()
            )
            
            QMessageBox.information(self, "成功", "工作流保存成功")
            self.workflow_updated.emit()
            self.operation_completed.emit()
        except Exception as e:
            error_msg = f"保存工作流失败: {str(e)}"
            logging.error(error_msg)
            QMessageBox.critical(self, "错误", error_msg)

    async def add_step(self) -> None:
        """异步添加工作流步骤"""
        if not self.current_workflow:
            QMessageBox.warning(self, "警告", "请先创建或加载工作流")
            return
            
        dialog = StepConfigDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            try:
                step_data = dialog.get_step_data()
                
                # 获取当前最大步骤序号
                next_order = self.step_list.count() + 1
                
                # 创建新步骤
                step = await self.crud_manager.add_workflow_step(
                    workflow_id=self.current_workflow['id'],
                    step_order=next_order,
                    **step_data
                )
                
                # 添加到列表
                item = QListWidgetItem(f"步骤 {next_order}: {step['action_type']}")
                item.setData(Qt.UserRole, step)
                self.step_list.addItem(item)
                self.workflow_updated.emit()
            except Exception as e:
                error_msg = f"添加步骤失败: {str(e)}"
                logging.error(error_msg)
                QMessageBox.critical(self, "错误", error_msg)

    async def remove_step(self) -> None:
        """异步删除工作流步骤"""
        current_item = self.step_list.currentItem()
        if not current_item:
            return
            
        step = current_item.data(Qt.UserRole)
        reply = QMessageBox.question(
            self,
            "确认删除",
            f"确定要删除步骤 {step['step_order']} 吗？",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                await self.crud_manager.delete_workflow_step(step['id'])
                self.step_list.takeItem(self.step_list.row(current_item))
                await self.reorder_steps()
                self.workflow_updated.emit()
            except Exception as e:
                error_msg = f"删除步骤失败: {str(e)}"
                logging.error(error_msg)
                QMessageBox.critical(self, "错误", error_msg)

    async def reorder_steps(self) -> None:
        """异步重新排序步骤"""
        try:
            for i in range(self.step_list.count()):
                item = self.step_list.item(i)
                step = item.data(Qt.UserRole)
                step['step_order'] = i + 1
                updated_step = await self.crud_manager.update_workflow_step(
                    step['id'],
                    step_order=step['step_order']
                )
                item.setText(f"步骤 {updated_step['step_order']}: {updated_step['action_type']}")
                item.setData(Qt.UserRole, updated_step)
        except Exception as e:
            error_msg = f"重新排序步骤失败: {str(e)}"
            logging.error(error_msg)
            QMessageBox.critical(self, "错误", error_msg)

    async def edit_step(self) -> None:
        """异步编辑步骤"""
        current_item = self.step_list.currentItem()
        if not current_item:
            return
            
        step = current_item.data(Qt.UserRole)
        dialog = StepConfigDialog(self, step)
        if dialog.exec_() == QDialog.Accepted:
            try:
                step_data = dialog.get_step_data()
                updated_step = await self.crud_manager.update_workflow_step(
                    step['id'],
                    **step_data
                )
                current_item.setData(Qt.UserRole, updated_step)
                current_item.setText(f"步骤 {updated_step['step_order']}: {updated_step['action_type']}")
                self.workflow_updated.emit()
            except Exception as e:
                error_msg = f"编辑步骤失败: {str(e)}"
                logging.error(error_msg)
                QMessageBox.critical(self, "错误", error_msg)

    def on_step_selected(self, current: Optional[QListWidgetItem], previous: Optional[QListWidgetItem]) -> None:
        """
        步骤选择变更处理
        
        Args:
            current: 当前选中的项
            previous: 之前选中的项
        """
        if not current:
            self.step_preview.clear()
            return
            
        step = current.data(Qt.UserRole)
        preview_text = f"""步骤信息：
动作类型: {step['action_type']}
选择器类型: {step.get('selector_type', 'N/A')}
选择器值: {step.get('selector_value', 'N/A')}
动作值: {step.get('value', 'N/A')}
描述: {step.get('description', 'N/A')}
"""
        self.step_preview.setText(preview_text)

    def execute_workflow(self) -> None:
        """执行工作流"""
        if not self.current_workflow:
            QMessageBox.warning(self, "警告", "请先创建或加载工作流")
            return
            
        workflow_id = self.current_workflow['id']
        self.execution_requested.emit(workflow_id)

    async def load_workflow(self) -> None:
        """异步加载工作流"""
        try:
            if not self.current_user_id:
                QMessageBox.warning(self, "警告", "请先登录")
                return

            # 获取用户的工作流列表
            workflows = await self.crud_manager.get_user_workflows(self.current_user_id)
            if not workflows:
                QMessageBox.information(self, "提示", "没有可用的工作流")
                return

            # 在主线程中显示选择对话框
            items = [f"{w['name']} (ID: {w['id']})" for w in workflows]
            item, ok = QInputDialog.getItem(
                self, "加载工作流", "选择工作流:", items, 0, False
            )

            if ok and item:
                workflow_id = int(item.split("ID: ")[1].rstrip(")"))
                
                try:
                    workflow = await self.crud_manager.get_workflow(workflow_id)
                    if not workflow:
                        raise ValueError(f"工作流 {workflow_id} 不存在")
                    
                    # 更新 UI
                    self._handle_workflow_loaded(workflow)
                    
                    # 加载步骤
                    steps = await self.crud_manager.get_workflow_steps(workflow_id)
                    self._handle_steps_loaded(steps)
                    
                    self.operation_completed.emit()
                    
                except Exception as e:
                    error_msg = f"加载工作流失败: {str(e)}"
                    logging.error(error_msg)
                    self._handle_workflow_load_failed(error_msg)

        except Exception as e:
            error_msg = f"加载工作流失败: {str(e)}"
            logging.error(error_msg)
            QMessageBox.critical(self, "错误", error_msg)

    def _handle_workflow_loaded(self, workflow: Dict[str, Any]) -> None:
        """
        处理工作流加载成功
        
        Args:
            workflow: 工作流信息
        """
        logging.info(f"工作流 {workflow['id']} 加载成功")
        self.current_workflow = workflow
        self.workflow_name.setText(workflow['name'])
        self.workflow_description.setText(workflow.get('description', ''))
        
        # 设置网站选择器
        website_id = workflow.get('website_id')
        if website_id:
            index = self.website_selector.findData(website_id)
            if index >= 0:
                self.website_selector.setCurrentIndex(index)
        
        self.workflow_loaded.emit(workflow)
        self.workflow_updated.emit()

    def _handle_workflow_load_failed(self, error_msg: str) -> None:
        """
        处理工作流加载失败
        
        Args:
            error_msg: 错误信息
        """
        logging.error(f"工作流加载失败: {error_msg}")
        QMessageBox.critical(self, "错误", f"加载工作流失败: {error_msg}")
        self.workflow_load_failed.emit(error_msg)

    def _handle_steps_loaded(self, steps: List[Dict[str, Any]]) -> None:
        """
        处理步骤加载成功
        
        Args:
            steps: 步骤列表
        """
        logging.info(f"加载了 {len(steps)} 个步骤")
        self.step_list.clear()
        for step in steps:
            item = QListWidgetItem(f"步骤 {step['step_order']}: {step['action_type']}")
            item.setData(Qt.UserRole, step)
            self.step_list.addItem(item)

    async def cleanup(self) -> None:
        """清理资源"""
        if not self.crud_manager:
            return  # 已经清理过了，直接返回
            
        try:
            await self.crud_manager.close()
            self.crud_manager = None
            self._is_initialized = False
            logging.info("资源清理完成")
        except Exception as e:
            logging.error(f"清理资源时发生错误: {str(e)}")

    def closeEvent(self, event: QCloseEvent) -> None:
        """
        关闭事件处理
        
        Args:
            event: 关闭事件
        """
        try:
            if self.crud_manager:
                logging.info("开始清理资源")
                # 使用 QTimer 延迟关闭，确保所有事件都被处理
                QTimer.singleShot(100, self.close)
                event.ignore()  # 暂时忽略关闭事件
                return
            
            # 如果已经清理完成，接受关闭事件
            super().closeEvent(event)
            logging.info("窗口已关闭")
        except Exception as e:
            logging.error(f"关闭事件处理时发生错误: {str(e)}")
            super().closeEvent(event) 