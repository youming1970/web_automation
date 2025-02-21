from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QMenuBar, QMenu, QAction, QMessageBox,
    QStatusBar
)
from PyQt5.QtCore import Qt
from .workflow_editor import WorkflowEditorWidget
from .workflow_executor import WorkflowExecutorWidget
from .data_viewer import DataViewerWidget

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Web自动化工具")
        self.setMinimumSize(1200, 800)
        
        # 创建中心部件
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # 创建主布局
        self.main_layout = QVBoxLayout(self.central_widget)
        
        # 创建标签页
        self.tab_widget = QTabWidget()
        self.main_layout.addWidget(self.tab_widget)
        
        # 创建工作流编辑器标签页
        self.workflow_editor = WorkflowEditorWidget()
        self.tab_widget.addTab(self.workflow_editor, "工作流编辑器")
        
        # 创建工作流执行器标签页
        self.workflow_executor = WorkflowExecutorWidget()
        self.tab_widget.addTab(self.workflow_executor, "工作流执行")
        
        # 创建数据查看器标签页
        self.data_viewer = DataViewerWidget()
        self.tab_widget.addTab(self.data_viewer, "数据查看")
        
        # 创建菜单栏
        self.create_menu_bar()
        
        # 创建状态栏
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("就绪")

    def create_menu_bar(self):
        """创建菜单栏"""
        menubar = self.menuBar()
        
        # 文件菜单
        file_menu = menubar.addMenu("文件")
        
        new_workflow_action = QAction("新建工作流", self)
        new_workflow_action.setShortcut("Ctrl+N")
        new_workflow_action.triggered.connect(self.workflow_editor.new_workflow)
        file_menu.addAction(new_workflow_action)
        
        open_workflow_action = QAction("打开工作流", self)
        open_workflow_action.setShortcut("Ctrl+O")
        open_workflow_action.triggered.connect(self.workflow_editor.load_workflow)
        file_menu.addAction(open_workflow_action)
        
        save_workflow_action = QAction("保存工作流", self)
        save_workflow_action.setShortcut("Ctrl+S")
        save_workflow_action.triggered.connect(self.workflow_editor.save_workflow)
        file_menu.addAction(save_workflow_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("退出", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # 执行菜单
        execution_menu = menubar.addMenu("执行")
        
        run_workflow_action = QAction("运行工作流", self)
        run_workflow_action.setShortcut("F5")
        run_workflow_action.triggered.connect(self.workflow_executor.run_workflow)
        execution_menu.addAction(run_workflow_action)
        
        stop_workflow_action = QAction("停止工作流", self)
        stop_workflow_action.setShortcut("F6")
        stop_workflow_action.triggered.connect(self.workflow_executor.stop_workflow)
        execution_menu.addAction(stop_workflow_action)
        
        # 视图菜单
        view_menu = menubar.addMenu("视图")
        
        refresh_action = QAction("刷新", self)
        refresh_action.setShortcut("F5")
        refresh_action.triggered.connect(self.refresh_current_view)
        view_menu.addAction(refresh_action)
        
        # 帮助菜单
        help_menu = menubar.addMenu("帮助")
        
        about_action = QAction("关于", self)
        about_action.triggered.connect(self.show_about_dialog)
        help_menu.addAction(about_action)

    def refresh_current_view(self):
        """刷新当前视图"""
        current_widget = self.tab_widget.currentWidget()
        if hasattr(current_widget, 'refresh'):
            current_widget.refresh()

    def show_about_dialog(self):
        """显示关于对话框"""
        QMessageBox.about(
            self,
            "关于Web自动化工具",
            "Web自动化工具 v1.0\n\n"
            "一个强大的网页数据提取和自动化工具。\n"
            "支持工作流定义、数据提取和反爬虫功能。"
        )

    def closeEvent(self, event):
        """关闭窗口事件处理"""
        reply = QMessageBox.question(
            self,
            "确认退出",
            "确定要退出程序吗？\n未保存的更改将会丢失。",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore() 