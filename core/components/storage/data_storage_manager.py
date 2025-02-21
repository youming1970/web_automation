import json
import os
from typing import Dict, Any, List, Callable
from datetime import datetime

class DataStorageManager:
    def __init__(self, storage_dir: str = "data"):
        """
        初始化数据存储管理器
        
        :param storage_dir: 数据存储目录
        """
        self.storage_dir = storage_dir
        self._ensure_storage_dir()

    def _ensure_storage_dir(self):
        """确保存储目录存在"""
        if not os.path.exists(self.storage_dir):
            os.makedirs(self.storage_dir)

    def _generate_filename(self, workflow_id: int) -> str:
        """
        生成数据文件名
        
        :param workflow_id: 工作流ID
        :return: 文件名
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        return f"workflow_{workflow_id}_{timestamp}.json"

    def store_data(self, workflow_id: int, data: Dict[str, Any]) -> str:
        """
        保存工作流提取的数据
        
        :param workflow_id: 工作流ID
        :param data: 提取的数据
        :return: 保存的文件路径
        """
        if not isinstance(data, dict):
            raise ValueError("数据必须是字典类型")
            
        if not data:
            raise ValueError("数据不能为空")
            
        filename = self._generate_filename(workflow_id)
        filepath = os.path.join(self.storage_dir, filename)
        
        # 构建完整的数据结构
        storage_data = {
            'workflow_id': workflow_id,
            'timestamp': datetime.now().isoformat(),
            'data': data
        }
        
        # 写入JSON文件
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(storage_data, f, ensure_ascii=False, indent=2)
            
        return filepath

    def load_data(self, filepath: str) -> Dict[str, Any]:
        """
        加载工作流数据
        
        :param filepath: 数据文件路径
        :return: 加载的数据
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"数据文件不存在: {filepath}")
            
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)

    def get_workflow_data_files(self, workflow_id: int = None) -> List[str]:
        """
        获取工作流数据文件列表
        
        :param workflow_id: 可选的工作流ID过滤
        :return: 文件路径列表
        """
        if workflow_id is not None and not workflow_id:
            raise ValueError("工作流ID不能为空")
            
        files = []
        for filename in os.listdir(self.storage_dir):
            if filename.endswith('.json'):
                if workflow_id is None or f"workflow_{workflow_id}_" in filename:
                    files.append(os.path.join(self.storage_dir, filename))
        return sorted(files, reverse=True)  # 最新的文件排在前面

    def export_data(self, source_path: str, target_path: str):
        """
        导出数据到指定文件
        
        :param source_path: 源数据文件路径
        :param target_path: 目标文件路径
        """
        if not os.path.exists(source_path):
            raise FileNotFoundError(f"源数据文件不存在: {source_path}")
            
        data = self.load_data(source_path)
        with open(target_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def delete_data(self, filepath: str) -> bool:
        """
        删除数据文件
        
        :param filepath: 数据文件路径
        :return: 是否删除成功
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"数据文件不存在: {filepath}")
            
        os.remove(filepath)
        return True

    def search_data_files(self, workflow_id: int, condition: Callable[[Dict[str, Any]], bool]) -> List[str]:
        """
        搜索符合条件的数据文件
        
        :param workflow_id: 工作流ID
        :param condition: 搜索条件函数
        :return: 符合条件的文件路径列表
        """
        if not callable(condition):
            raise ValueError("搜索条件必须是可调用的函数")
            
        matching_files = []
        for filepath in self.get_workflow_data_files(workflow_id):
            try:
                data = self.load_data(filepath)
                if condition(data.get('data', {})):
                    matching_files.append(filepath)
            except:
                continue
        return matching_files

    def aggregate_data(self, workflow_id: int, value_getter: Callable[[Dict[str, Any]], Any], aggregator: Callable[[List[Any]], Any]) -> Any:
        """
        聚合数据
        
        :param workflow_id: 工作流ID
        :param value_getter: 值获取函数
        :param aggregator: 聚合函数
        :return: 聚合结果
        """
        if not callable(value_getter) or not callable(aggregator):
            raise ValueError("值获取函数和聚合函数必须是可调用的")
            
        values = []
        for filepath in self.get_workflow_data_files(workflow_id):
            try:
                data = self.load_data(filepath)
                value = value_getter(data.get('data', {}))
                if value is not None:
                    values.append(value)
            except:
                continue
        return aggregator(values) if values else None

    def cleanup_old_data(self, days: int = 30):
        """
        清理指定天数之前的数据文件
        
        :param days: 保留的天数
        """
        cutoff = datetime.now().timestamp() - (days * 24 * 60 * 60)
        
        for filepath in self.get_workflow_data_files():
            if os.path.getmtime(filepath) < cutoff:
                self.delete_data(filepath) 