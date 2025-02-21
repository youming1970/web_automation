from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QComboBox,
    QLabel, QGroupBox, QMessageBox, QFileDialog,
    QHeaderView
)
from PyQt5.QtCore import Qt
from database.crud_manager import CRUDManager
from core.components.storage.data_storage_manager import DataStorageManager
import json
import os

class DataViewerWidget(QWidget):
    """数据查看器组件"""

    def __init__(self):
        super().__init__()
        self.crud_manager = CRUDManager()
        self.data_storage = DataStorageManager()
        self.current_data = None
        self.setup_ui()

    def setup_ui(self):
        """设置UI布局"""
        layout = QVBoxLayout(self)
        
        # 工作流选择和数据文件选择
        selection_group = QGroupBox("数据选择")
        selection_layout = QHBoxLayout(selection_group)
        
        # 工作流选择
        self.workflow_selector = QComboBox()
        self.load_workflows()
        selection_layout.addWidget(QLabel("工作流:"))
        selection_layout.addWidget(self.workflow_selector)
        self.workflow_selector.currentIndexChanged.connect(self.on_workflow_changed)
        
        # 数据文件选择
        self.file_selector = QComboBox()
        selection_layout.addWidget(QLabel("数据文件:"))
        selection_layout.addWidget(self.file_selector)
        self.file_selector.currentIndexChanged.connect(self.load_data)
        
        layout.addWidget(selection_group)
        
        # 工具栏
        toolbar_group = QGroupBox("工具栏")
        toolbar_layout = QHBoxLayout(toolbar_group)
        
        # 刷新按钮
        refresh_button = QPushButton("刷新")
        refresh_button.clicked.connect(self.refresh)
        toolbar_layout.addWidget(refresh_button)
        
        # 导出按钮
        export_button = QPushButton("导出")
        export_button.clicked.connect(self.export_data)
        toolbar_layout.addWidget(export_button)
        
        # 删除按钮
        delete_button = QPushButton("删除")
        delete_button.clicked.connect(self.delete_data)
        toolbar_layout.addWidget(delete_button)
        
        layout.addWidget(toolbar_group)
        
        # 数据表格
        self.table = QTableWidget()
        self.table.setColumnCount(3)  # 默认3列：步骤、类型、数据
        self.table.setHorizontalHeaderLabels(["步骤", "类型", "数据"])
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        layout.addWidget(self.table)

    def load_workflows(self):
        """加载工作流列表"""
        self.workflow_selector.clear()
        self.workflow_selector.addItem("全部工作流", None)
        workflows = self.crud_manager.get_all_workflows()
        for workflow in workflows:
            self.workflow_selector.addItem(
                f"{workflow['name']} (ID: {workflow['id']})",
                workflow['id']
            )

    def on_workflow_changed(self):
        """工作流选择变更处理"""
        workflow_id = self.workflow_selector.currentData()
        self.load_data_files(workflow_id)

    def load_data_files(self, workflow_id: int = None):
        """加载数据文件列表"""
        self.file_selector.clear()
        files = self.data_storage.list_workflow_data(workflow_id)
        
        for filepath in files:
            filename = os.path.basename(filepath)
            self.file_selector.addItem(filename, filepath)
            
        if self.file_selector.count() > 0:
            self.load_data()  # 加载第一个文件的数据
        else:
            self.clear_table()

    def load_data(self):
        """加载数据文件内容"""
        filepath = self.file_selector.currentData()
        if not filepath:
            self.clear_table()
            return
            
        try:
            data = self.data_storage.load_workflow_data(filepath)
            self.current_data = data
            self.display_data(data)
        except Exception as e:
            QMessageBox.critical(self, "错误", f"加载数据失败: {str(e)}")
            self.clear_table()

    def display_data(self, data: dict):
        """显示数据到表格"""
        self.clear_table()
        
        if not data or 'data' not in data:
            return
            
        extracted_data = data['data']
        self.table.setRowCount(len(extracted_data))
        
        for row, item in enumerate(extracted_data):
            # 步骤ID
            step_item = QTableWidgetItem(str(item.get('step_id', '')))
            self.table.setItem(row, 0, step_item)
            
            # 数据类型
            type_item = QTableWidgetItem(item.get('type', ''))
            self.table.setItem(row, 1, type_item)
            
            # 数据内容
            data_content = item.get('data', '')
            if isinstance(data_content, (dict, list)):
                data_content = json.dumps(data_content, ensure_ascii=False, indent=2)
            data_item = QTableWidgetItem(str(data_content))
            self.table.setItem(row, 2, data_item)

    def clear_table(self):
        """清空表格"""
        self.table.setRowCount(0)
        self.current_data = None

    def export_data(self):
        """导出数据"""
        if not self.current_data:
            QMessageBox.warning(self, "警告", "没有可导出的数据")
            return
            
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "导出数据",
            "",
            "JSON文件 (*.json);;CSV文件 (*.csv);;所有文件 (*.*)"
        )
        
        if not file_path:
            return
            
        try:
            if file_path.endswith('.json'):
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(self.current_data, f, ensure_ascii=False, indent=2)
            elif file_path.endswith('.csv'):
                self.export_to_csv(file_path)
            else:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(self.current_data, f, ensure_ascii=False, indent=2)
                    
            QMessageBox.information(self, "成功", "数据导出成功")
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"导出数据失败: {str(e)}")

    def export_to_csv(self, file_path: str):
        """导出数据到CSV文件"""
        import csv
        
        with open(file_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            # 写入表头
            writer.writerow(["步骤ID", "类型", "数据"])
            
            # 写入数据
            for row in range(self.table.rowCount()):
                row_data = []
                for col in range(self.table.columnCount()):
                    item = self.table.item(row, col)
                    row_data.append(item.text() if item else '')
                writer.writerow(row_data)

    def delete_data(self):
        """删除数据文件"""
        filepath = self.file_selector.currentData()
        if not filepath:
            return
            
        reply = QMessageBox.question(
            self,
            "确认删除",
            "确定要删除选中的数据文件吗？",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                if self.data_storage.delete_workflow_data(filepath):
                    QMessageBox.information(self, "成功", "数据文件删除成功")
                    self.refresh()
                else:
                    QMessageBox.warning(self, "警告", "数据文件删除失败")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"删除数据文件失败: {str(e)}")

    def refresh(self):
        """刷新视图"""
        current_workflow_id = self.workflow_selector.currentData()
        self.load_workflows()
        
        # 恢复之前选择的工作流
        if current_workflow_id is not None:
            index = self.workflow_selector.findData(current_workflow_id)
            if index >= 0:
                self.workflow_selector.setCurrentIndex(index)
            
        self.load_data_files(current_workflow_id) 