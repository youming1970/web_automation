from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTextEdit, QComboBox, QLabel, QProgressBar,
    QGroupBox, QMessageBox
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from database.crud_manager import CRUDManager
from core.components.workflow.workflow_engine import WorkflowEngine
from core.components.browser.browser_manager import BrowserManager

class WorkflowExecutorThread(QThread):
    """工作流执行线程"""
    
    progress = pyqtSignal(int)  # 进度信号
    log = pyqtSignal(str)  # 日志信号
    finished = pyqtSignal(dict)  # 完成信号
    error = pyqtSignal(str)  # 错误信号

    def __init__(self, workflow_id: int, browser_manager: BrowserManager):
        super().__init__()
        self.workflow_id = workflow_id
        self.workflow_engine = WorkflowEngine(browser_manager)
        self.is_running = False

    def run(self):
        """执行工作流"""
        self.is_running = True
        try:
            # 加载工作流
            self.log.emit("正在加载工作流...")
            workflow = self.workflow_engine.load_workflow(self.workflow_id)
            
            # 获取步骤总数
            total_steps = len(workflow['steps'])
            self.log.emit(f"工作流 '{workflow['name']}' 包含 {total_steps} 个步骤")
            
            # 执行工作流
            self.log.emit("开始执行工作流...")
            result = self.workflow_engine.execute_workflow(self.workflow_id)
            
            # 发送结果
            self.finished.emit(result)
            
        except Exception as e:
            self.error.emit(str(e))
        finally:
            self.is_running = False

    def stop(self):
        """停止执行"""
        self.is_running = False
        self.terminate()

class WorkflowExecutorWidget(QWidget):
    """工作流执行器组件"""

    def __init__(self):
        super().__init__()
        self.crud_manager = CRUDManager()
        self.browser_manager = BrowserManager()
        self.executor_thread = None
        self.setup_ui()

    def setup_ui(self):
        """设置UI布局"""
        layout = QVBoxLayout(self)
        
        # 工作流选择区域
        selection_group = QGroupBox("工作流选择")
        selection_layout = QHBoxLayout(selection_group)
        
        self.workflow_selector = QComboBox()
        self.load_workflows()
        selection_layout.addWidget(QLabel("选择工作流:"))
        selection_layout.addWidget(self.workflow_selector)
        
        layout.addWidget(selection_group)
        
        # 控制按钮区域
        control_group = QGroupBox("执行控制")
        control_layout = QHBoxLayout(control_group)
        
        self.run_button = QPushButton("运行")
        self.run_button.clicked.connect(self.run_workflow)
        control_layout.addWidget(self.run_button)
        
        self.stop_button = QPushButton("停止")
        self.stop_button.clicked.connect(self.stop_workflow)
        self.stop_button.setEnabled(False)
        control_layout.addWidget(self.stop_button)
        
        layout.addWidget(control_group)
        
        # 进度显示
        progress_group = QGroupBox("执行进度")
        progress_layout = QVBoxLayout(progress_group)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        progress_layout.addWidget(self.progress_bar)
        
        layout.addWidget(progress_group)
        
        # 日志显示区域
        log_group = QGroupBox("执行日志")
        log_layout = QVBoxLayout(log_group)
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        log_layout.addWidget(self.log_text)
        
        layout.addWidget(log_group)

    def load_workflows(self):
        """加载工作流列表"""
        self.workflow_selector.clear()
        workflows = self.crud_manager.get_all_workflows()
        for workflow in workflows:
            self.workflow_selector.addItem(
                f"{workflow['name']} (ID: {workflow['id']})",
                workflow['id']
            )

    def run_workflow(self):
        """运行工作流"""
        workflow_id = self.workflow_selector.currentData()
        if workflow_id is None:
            QMessageBox.warning(self, "警告", "请先选择工作流")
            return
        
        # 创建并启动执行线程
        self.executor_thread = WorkflowExecutorThread(
            workflow_id,
            self.browser_manager
        )
        
        # 连接信号
        self.executor_thread.progress.connect(self.update_progress)
        self.executor_thread.log.connect(self.append_log)
        self.executor_thread.finished.connect(self.on_execution_finished)
        self.executor_thread.error.connect(self.on_execution_error)
        
        # 更新UI状态
        self.run_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.workflow_selector.setEnabled(False)
        self.progress_bar.setValue(0)
        self.log_text.clear()
        
        # 启动线程
        self.executor_thread.start()

    def stop_workflow(self):
        """停止工作流执行"""
        if self.executor_thread and self.executor_thread.is_running:
            reply = QMessageBox.question(
                self,
                "确认停止",
                "确定要停止当前工作流的执行吗？",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                self.executor_thread.stop()
                self.append_log("工作流执行已停止")
                self.reset_ui_state()

    def update_progress(self, value: int):
        """更新进度条"""
        self.progress_bar.setValue(value)

    def append_log(self, message: str):
        """添加日志"""
        self.log_text.append(message)
        # 滚动到底部
        self.log_text.verticalScrollBar().setValue(
            self.log_text.verticalScrollBar().maximum()
        )

    def on_execution_finished(self, result: dict):
        """执行完成处理"""
        status = result.get('status', 'unknown')
        if status == 'completed':
            self.append_log("工作流执行完成")
            # 显示提取的数据数量
            data_count = len(result.get('extracted_data', []))
            self.append_log(f"共提取 {data_count} 条数据")
            
            QMessageBox.information(
                self,
                "执行完成",
                f"工作流执行成功，共提取 {data_count} 条数据"
            )
        else:
            self.append_log(f"工作流执行失败: {result.get('error', '未知错误')}")
            
        self.reset_ui_state()

    def on_execution_error(self, error_message: str):
        """执行错误处理"""
        self.append_log(f"错误: {error_message}")
        QMessageBox.critical(self, "执行错误", error_message)
        self.reset_ui_state()

    def reset_ui_state(self):
        """重置UI状态"""
        self.run_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.workflow_selector.setEnabled(True)
        self.progress_bar.setValue(0)

    def refresh(self):
        """刷新视图"""
        self.load_workflows()
        if self.executor_thread and self.executor_thread.is_running:
            self.run_button.setEnabled(False)
            self.stop_button.setEnabled(True)
            self.workflow_selector.setEnabled(False)
        else:
            self.reset_ui_state() 